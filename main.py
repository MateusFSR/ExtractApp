from flask import Flask, render_template, jsonify
from telethon import TelegramClient, events
import asyncio
import threading
import re
import time


# Configurações do Telegram
api_id = '23529013'
api_hash = 'a889d755b13bf00f042339a2a75a5c73'
phone_number = '+5541992596254'
group_username = 'https://t.me/+GmYiheEus8kyNTRh'

client = TelegramClient('user_session', api_id, api_hash)
last_message = "Carregando mensagens..."
entrada_coluna = "Nenhuma entrada detectada"

# Função que processa a mensagem para extrair a 4ª linha e a entrada
def processar_entrada(mensagem):
    global entrada_coluna
    try:
        linhas = mensagem.splitlines()  # Divide a mensagem em linhas
        # Verifica se a 4ª linha existe e contém a palavra "Entrada"
        if len(linhas) >= 4 and "Entrada" in linhas[3]:
            # Usa regex para capturar os números da coluna (por exemplo, "2º e 3° COLUNA")
            match = re.search(r"(\d)º e (\d)°", linhas[3])
            if match:
                entrada_coluna = f"{match.group(1)} e {match.group(2)}"  # Extrai e formata "2 e 3"
            else:
                entrada_coluna = "Entrada não reconhecida"
        else:
            entrada_coluna = "Entrada não encontrada na 4ª linha"
    except Exception as e:
        entrada_coluna = f"Erro ao processar entrada: {str(e)}"

# Função que atualiza a última mensagem do grupo
ultima_mensagem_processada = ""

async def get_last_message():
    global last_message, ultima_mensagem_processada
    await client.start(phone=phone_number)

    try:
        group = await client.get_entity(group_username)
        print(f"Grupo encontrado: {group.title}")

        # Busca a última mensagem no grupo
        async for message in client.iter_messages(group, limit=1):
            if message.text and message.text != ultima_mensagem_processada:
                last_message = message.text
                ultima_mensagem_processada = message.text  # Atualiza a última mensagem processada
                processar_entrada(last_message)
            else:
                last_message = "(Mensagem sem texto ou mídia)"
            print(f"Última mensagem: {last_message}")
        
        # Atraso após a leitura
        await asyncio.sleep(7)  # Aguarde 5 segundos antes de tentar novamente

    except Exception as e:
        last_message = f"Erro ao capturar mensagens: {str(e)}"
        print(f"Erro: {e}")

async def start_telegram_client():
    while True:
        await get_last_message()
        await asyncio.sleep(7)  # Mantenha um pequeno intervalo para não sobrecarregar

# Configuração do Flask para exibir a última mensagem
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/last_message')
def get_message():
    global last_message, entrada_coluna
    # Retorna a última mensagem e a entrada extraída
    return jsonify({'message': last_message, 'entrada': entrada_coluna})

# Função para rodar o Flask
def run_flask():
    app.run(debug=True, use_reloader=False)

# Executar o Telegram e o Flask juntos
if __name__ == '__main__':
    # Rodar Flask em uma thread separada
    threading.Thread(target=run_flask).start()

    # Rodar o Telegram na thread principal com asyncio
    asyncio.run(start_telegram_client())
