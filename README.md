## Emma bot Discord
Uma robo de conversação 100% gratuito para jogar conversa fora, ter dicas de jogos principalmente de ritmo e comprar comidinhas com ela!

## Instalação

**Passos de preparação**

1. [Instale o Python](https://www.python.org/downloads/)
2. [Instale o Ollama](https://ollama.com/download/)
3. Instale o modelo pelo terminal `ollama pull llama3.2-vision` (emma.modelfile é 100% funcional com llama 3.2-vision)

**Passos de costumização (opcional)**

4. Abra a pasta onde o arquivo `emma.modelfile` está e abra o terminal lá
5. Use o comando `notepad emma.modelfile` para modificar o modelo caso queira, apois modificar salve as alterações
6. Sem sair do CMD crie a versão modificada do llama 3.2-vision executando o comando ` ollama  create emma --file emma.modelfile`

**Passos de desenvolvimento**

7. Use o terminal integrado do projeto para instalar requerimentos do llama `pip install discord.py ollama requests`
8. Abra `config.toml` coloque o seu TOKEN e seu modelo de IA (se pulou costumização insira `"llama3.2-vision"` se não `"emma"`)
9. Dê play no arquivo `emma.py`
10. Divirta-se com o bot :3!

## Comandos

**@Emma**: quando emma é mensionada você pode escrever qualquer coisa depois, assim ela responde sua pergunta/fala, use "*" para fazer um "roleplay"

**@loja**: abre opções da padaria da emma, onde vende algumas delicias, para selecionar apenas escreva o numero do item depois de usar o comando

## Comportamentos

**Na conversa**
Emma se comporta como uma menina de 16 anos com gostos bem definidos e uma certa opnião feita sobre muitas coisas, perfeito para uma simples conversa descontraida e bobinha

**Por trás dos panos**
Emma salva as interações em `history.json`, responde quando é mensionada, exibe a loja quando é pedido, responde um usuario de cada vez caso tenha mais de 1 usuaio falando ao mesmo tempo com ela e pode funcionar no privado de forma exelente! 

## Faça ser a sua cara!
- Modifique o modelo
- Dê uma limpada no codigo
- Modifique as funcionalidades
- Ajuste o desempenho (ela consome bastante da maquina)
