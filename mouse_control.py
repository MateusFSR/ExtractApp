import tkinter as tk
from tkinter import messagebox
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import threading
import requests
import time

# Inicialização dos controladores
mouse_controller = MouseController()
keyboard_controller = KeyboardController()

# Variáveis para armazenar as posições
posicao1 = None
posicao2 = None
posicao3 = None

# URL do servidor Flask
FLASK_URL = 'http://localhost:5000/last_message'

# Função para capturar a próxima posição do mouse
def capturar_posicao(posicao_num):
    messagebox.showinfo("Capturar Posição", f"Clique em qualquer lugar da tela para capturar a Posição {posicao_num}.")
    
    def on_click(x, y, button, pressed):
        if pressed:
            global posicao1, posicao2, posicao3
            if posicao_num == 1:
                posicao1 = (x, y)
                btn_pos1.config(text=f"Posição 1: {posicao1}")
            elif posicao_num == 2:
                posicao2 = (x, y)
                btn_pos2.config(text=f"Posição 2: {posicao2}")
            elif posicao_num == 3:
                posicao3 = (x, y)
                btn_pos3.config(text=f"Posição 3: {posicao3}")
            listener.stop()

    # Inicia o listener para capturar a próxima posição do mouse
    listener = mouse.Listener(on_click=on_click)
    listener.start()

# Função para simular cliques com base na entrada
def executar_clique(combinacao):
    if combinacao == "1 e 2" and posicao1 and posicao2:
        clicar_em(posicao1)
    elif combinacao == "1 e 3" and posicao1 and posicao3:
        clicar_em(posicao2)
    elif combinacao == "2 e 3" and posicao2 and posicao3:
        clicar_em(posicao3)

def clicar_em(posicao):
    x, y = posicao
    mouse_controller.position = (x, y)
    mouse_controller.click(Button.left, 1)
    print(f"Clicou na posição: {posicao}")

# Função para monitorar as mensagens do Flask
def monitorar_mensagens():
    ultima_entrada = ""
    while True:
        try:
            response = requests.get(FLASK_URL)
            if response.status_code == 200:
                data = response.json()
                entrada = data.get('entrada', '')
                print(f"Entrada detectada: {entrada}")
                if entrada != ultima_entrada:
                    ultima_entrada = entrada
                    if entrada in ["1 e 2", "1 e 3", "2 e 3"]:
                        executar_clique(entrada)
            else:
                print(f"Falha na requisição: Status Code {response.status_code}")
        except Exception as e:
            print(f"Erro ao verificar a entrada: {e}")
        time.sleep(5)  # Aguarda 5 segundos antes de verificar novamente

# Configuração da interface gráfica
root = tk.Tk()
root.title("Controle de Cliques")
root.geometry("400x300")
root.configure(bg="#2E2E2E")  # Fundo escuro para combinar com tema de roleta

# Título
titulo = tk.Label(root, text="Controle de Cliques Automáticos", font=("Helvetica", 16, "bold"), fg="#FFD700", bg="#2E2E2E")
titulo.pack(pady=20)

# Botões para capturar posições
btn_pos1 = tk.Button(root, text="Capturar Posição 1", command=lambda: capturar_posicao(1), width=30, height=2, bg="#FF5733", fg="white")
btn_pos1.pack(pady=5)

btn_pos2 = tk.Button(root, text="Capturar Posição 2", command=lambda: capturar_posicao(2), width=30, height=2, bg="#33FF57", fg="white")
btn_pos2.pack(pady=5)

btn_pos3 = tk.Button(root, text="Capturar Posição 3", command=lambda: capturar_posicao(3), width=30, height=2, bg="#3357FF", fg="white")
btn_pos3.pack(pady=5)

# Labels para exibir as posições capturadas
label_pos1 = tk.Label(root, text="Posição 1: Não Capturada", fg="white", bg="#2E2E2E")
label_pos1.pack(pady=5)

label_pos2 = tk.Label(root, text="Posição 2: Não Capturada", fg="white", bg="#2E2E2E")
label_pos2.pack(pady=5)

label_pos3 = tk.Label(root, text="Posição 3: Não Capturada", fg="white", bg="#2E2E2E")
label_pos3.pack(pady=5)

# Atualizar os textos dos botões após captura
def atualizar_botoes():
    if posicao1:
        btn_pos1.config(text=f"Posição 1: {posicao1}")
    if posicao2:
        btn_pos2.config(text=f"Posição 2: {posicao2}")
    if posicao3:
        btn_pos3.config(text=f"Posição 3: {posicao3}")

# Thread para monitorar mensagens
thread_mensagens = threading.Thread(target=monitorar_mensagens, daemon=True)
thread_mensagens.start()

root.mainloop()
