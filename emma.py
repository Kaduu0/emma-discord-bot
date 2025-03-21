import discord
import tomllib
import aiohttp
import json
import os
import asyncio  # Para gerenciar a fila de processamento

# Carregar variáveis do arquivo config.toml
with open("config.toml", 'rb') as f:
    config_data = tomllib.load(f)

# Informações da API para o Ollama
TOKEN = config_data['discord']['token']
API_URL = 'http://localhost:11434/api/chat'

# Caminho do arquivo de histórico de conversação
HISTORY_FILE_PATH = "history.json"

# Carregar histórico de conversação
def load_conversation_history():
    if os.path.exists(HISTORY_FILE_PATH):
        with open(HISTORY_FILE_PATH, 'r') as file:
            return json.load(file)
    return []

# Salvar histórico de conversação
def save_conversation_history():
    with open(HISTORY_FILE_PATH, 'w') as file:
        json.dump(conversation_history, file)

# Histórico de conversação
conversation_history = load_conversation_history()

# Configuração de intenções do Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Limitar histórico de conversação
def limit_conversation_history():
    global conversation_history
    max_history_length = 5
    if len(conversation_history) > max_history_length:
        conversation_history = conversation_history[-max_history_length:]

# Função para enviar a solicitação à API
async def generate_response(prompt):
    limit_conversation_history()
    conversation_history.append({"role": "user", "content": prompt})

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
                assistant_message = limit_message_to_five_lines(assistant_message)
                conversation_history.append({"role": "assistant", "content": assistant_message})

                # Salvar histórico atualizado
                save_conversation_history()
                
                return assistant_message
            except Exception as e:
                print(f"Erro ao processar resposta: {e}")
                return "Erro: Resposta inválida da API"

# Limitar resposta do bot a 5 linhas
def limit_message_to_five_lines(message):
    lines = message.split('\n')
    return '\n'.join(lines[:5]) if len(lines) > 5 else message

# Cache de respostas
response_cache = {}

async def get_response_from_cache_or_generate(prompt):
    if prompt in response_cache:
        return response_cache[prompt]
    response = await generate_response(prompt)
    response_cache[prompt] = response
    return response

# Fila para processar mensagens uma por vez
processing_queue = asyncio.Queue()

# Lista de itens disponíveis para compra com emojis
itens_para_venda = [
    "🍪 Cookie",
    "🧁 Cupcake",
    "🥛 Leite",
    "☕ Café"
]

@client.event
async def on_ready():
    print(f'Logado como {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    # Verifica se a mensagem menciona a IA
    if client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        await processing_queue.put((message, prompt))

        if processing_queue.qsize() == 1:
            while not processing_queue.empty():
                current_message, current_prompt = await processing_queue.get()
                try:
                    async with current_message.channel.typing():
                        response = await get_response_from_cache_or_generate(current_prompt)
                        response_with_mention = f"<@{current_message.author.id}> {response}"
                        await current_message.channel.send(response_with_mention)
                except discord.errors.Forbidden:
                    print(f"Erro: Sem permissão para enviar mensagem em {current_message.channel.name}")

    # Verifica se a mensagem menciona a loja para comprar
    elif "@loja" in message.content:
        descricao_itens = "\n".join([f"{i+1}. {item}" for i, item in enumerate(itens_para_venda)])
        mensagem = f"Bem vindo(a)! gostaria de algo?\n\n{descricao_itens}\n\nEscolha o número correspondente ao seu pedido!"
        await message.channel.send(mensagem)
        
        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.isdigit()
        
        try:
            resposta = await client.wait_for("message", check=check, timeout=30)
            escolha = int(resposta.content)
            
            if 1 <= escolha <= len(itens_para_venda):
                item_escolhido = itens_para_venda[escolha - 1]
                await message.channel.send(f"<@{message.author.id}> comprou {item_escolhido}! volte sempre!")
            else:
                await message.channel.send(f"<@{message.author.id}>, essa opção não está disponível.")
        except asyncio.TimeoutError:
            await message.channel.send(f"precisa de mais tempo <@{message.author.id}>? Me chame de novo quando se decidir!")

# Executa o bot
client.run(TOKEN)
