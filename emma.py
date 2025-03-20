import discord
import tomllib
import aiohttp
import json
import os
import asyncio  # Importar asyncio para controlar a fila de processamento

# Carregar variáveis do arquivo config.toml
with open("config.toml", 'rb') as f:
    config_data = tomllib.load(f)

# Informações da API para o Ollama
TOKEN = config_data['discord']['token']
API_URL = 'http://localhost:11434/api/chat'

# Caminho do arquivo de histórico de conversação
HISTORY_FILE_PATH = "history.json"

# Carregar o histórico de conversação se existir
def load_conversation_history():
    if os.path.exists(HISTORY_FILE_PATH):
        with open(HISTORY_FILE_PATH, 'r') as file:
            return json.load(file)
    return []

# Salvar o histórico de conversação (apenas quando necessário)
def save_conversation_history():
    with open(HISTORY_FILE_PATH, 'w') as file:
        json.dump(conversation_history, file)

# Histórico de conversação armazenado em uma lista
conversation_history = load_conversation_history()

# Configuração de intenções do Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Limitar o histórico de conversação (últimas 5 mensagens)
def limit_conversation_history():
    global conversation_history
    max_history_length = 5
    if len(conversation_history) > max_history_length:
        conversation_history = conversation_history[-max_history_length:]

# Função assíncrona para enviar a solicitação à API do Ollama e obter uma resposta
async def generate_response(prompt):
    # Limita o histórico de mensagens antes de enviar à API
    limit_conversation_history()

    # Adiciona a mensagem do usuário ao histórico
    conversation_history.append({
        "role": "user",
        "content": prompt
    })

    # Dados da requisição
    data = {
        "model": config_data['ollama']['model'],
        "messages": conversation_history,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=data) as response:
            try:
                response_data = await response.json()
                assistant_message = response_data['message']['content']

                # Limitar o número de linhas da resposta para no máximo 5
                assistant_message = limit_message_to_five_lines(assistant_message)

                # Adiciona a resposta do assistente ao histórico de conversação
                conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                return assistant_message
            except Exception as e:
                print(f"Erro ao processar resposta: {e}")
                return "Error: Invalid API response"

# Função para garantir que a resposta do bot tenha no máximo 5 linhas
def limit_message_to_five_lines(message):
    lines = message.split('\n')
    if len(lines) > 5:
        return '\n'.join(lines[:5])  # Limita a resposta a 5 linhas
    return message

# Usar cache para evitar fazer a mesma solicitação várias vezes
response_cache = {}

async def get_response_from_cache_or_generate(prompt):
    if prompt in response_cache:
        return response_cache[prompt]
    response = await generate_response(prompt)
    response_cache[prompt] = response
    return response

# Implementação de uma fila para garantir que uma mensagem seja processada de cada vez
processing_queue = asyncio.Queue()

# Quando o bot estiver pronto
@client.event
async def on_ready():
    print(f'Logado como {client.user}')

# Quando o bot detectar uma nova mensagem
@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    prompt = message.content
    prompt = f"{message.author.display_name} diz: " + prompt

    # Coloca a tarefa na fila
    await processing_queue.put(message)

    # Processa as mensagens da fila uma por vez
    if processing_queue.qsize() == 1:  # Se for a única mensagem na fila
        while not processing_queue.empty():
            current_message = await processing_queue.get()
            try:
                async with current_message.channel.typing():
                    # Usar cache para evitar chamadas repetidas à API
                    response = await get_response_from_cache_or_generate(current_message.content)

                    # Mencionar o usuário
                    response_with_mention = f"<@{current_message.author.id}> {response}"
                    await current_message.channel.send(response_with_mention)

            except discord.errors.Forbidden:
                print(f"Erro: Bot não tem permissão para digitar em {current_message.channel.name}")

# Executa o bot
client.run(TOKEN)
