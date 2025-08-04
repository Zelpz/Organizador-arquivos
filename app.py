import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime

# Tipos de arquivos
tipos = {
    'Documentos': ['.pdf', '.docx', '.txt', '.xlsx'],
    'Imagens': ['.png', '.jpg', '.jpeg', '.gif'],
    'Vídeos': ['.mp4', '.avi', '.mov'],
    'Áudio': ['.mp3', '.wav'],
    'Executáveis': ['.exe', '.msi'],
    'Compactados': ['.zip', '.rar', '.7z'],
    'Scripts': ['.py', '.js', '.bat'],
    'Outros': []
}

pasta_organizar = None
log_path = None

def registrar_log(msg):
    if not log_path:
        return
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def organizar_arquivos():
    if not pasta_organizar:
        return 0
    count = 0
    for arquivo in pasta_organizar.iterdir():
        if arquivo.is_file():
            movido = False
            for pasta, extensoes in tipos.items():
                if arquivo.suffix.lower() in extensoes:
                    destino = pasta_organizar / pasta
                    destino.mkdir(exist_ok=True)
                    shutil.move(str(arquivo), destino / arquivo.name)
                    registrar_log(f"Movido: {arquivo.name} → {pasta}")
                    movido = True
                    count += 1
                    break
            if not movido:
                destino = pasta_organizar / "Outros"
                destino.mkdir(exist_ok=True)
                shutil.move(str(arquivo), destino / arquivo.name)
                registrar_log(f"Movido: {arquivo.name} → Outros")
                count += 1
    return count

def executar_organizador():
    if not pasta_organizar:
        messagebox.showwarning("Erro", "Selecione uma pasta primeiro.")
        return
    total = organizar_arquivos()
    messagebox.showinfo("Organizador", f"{total} arquivo(s) organizados.")
    atualizar_ultima_execucao()

def selecionar_pasta():
    global pasta_organizar, log_path
    caminho = filedialog.askdirectory()
    if caminho:
        pasta_organizar = Path(caminho)
        log_path = pasta_organizar / "organizador_log.txt"
        label_pasta.config(text=f"Pasta: {pasta_organizar}")
        atualizar_ultima_execucao()

def atualizar_ultima_execucao():
    if log_path and log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            linhas = f.readlines()
            if linhas:
                ultima = linhas[-1]
                label_status.config(text=f"Último registro: {ultima.strip()}")

def criar_interface():
    janela = tk.Tk()
    janela.title("Organizador de Arquivos")
    janela.geometry("450x280")
    janela.resizable(False, False)

    # Estilo moderno com ttk
    style = ttk.Style(janela)
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))

    container = ttk.Frame(janela, padding=20)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="Organizador de Arquivos", style="Title.TLabel").pack(pady=(0, 15))

    ttk.Button(container, text="Selecionar Pasta", command=selecionar_pasta).pack(pady=5)

    global label_pasta
    label_pasta = ttk.Label(container, text="Pasta: nenhuma selecionada", foreground="gray")
    label_pasta.pack(pady=5)

    ttk.Button(container, text="Organizar Agora", command=executar_organizador).pack(pady=15)

    global label_status
    label_status = ttk.Label(container, text="", foreground="gray")
    label_status.pack(pady=(10, 0))

    janela.mainloop()

# Agendador em thread
def agendador():
    while True:
        if pasta_organizar:
            organizar_arquivos()
        time.sleep(3600)

threading.Thread(target=agendador, daemon=True).start()
criar_interface()