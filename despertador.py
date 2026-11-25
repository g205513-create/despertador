import datetime
import os
import tkinter as tk

import cv2
import pygame
from PIL import Image, ImageTk

img = cv2.imread("qr_despertar.png")
texto, pts, _ = cv2.QRCodeDetector().detectAndDecode(img)
print("Leu:", repr(texto))

# --- CONFIGURAÇÕES ---
CAMERA = "http://192.168.0.249:8080/video"
CODIGOS_VALIDOS = {"DESPERTAR-GABRIEL-2026"}

# Som na mesma pasta do script. Confira se o nome é exatamente o do seu arquivo
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SOM = os.path.join(PASTA, "despertador.wav.mp3")

alarme_id = None
alvo = None


def tocar_som():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(ARQUIVO_SOM)
        pygame.mixer.music.play(-1)  # repete até parar
    except Exception as e:
        print(f"Erro ao tocar o som: {e}")


def parar_som():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def abrir_camera():
    cap = cv2.VideoCapture(CAMERA)
    if not cap.isOpened():
        print("Celular não respondeu, usando a webcam do PC")
        cap = cv2.VideoCapture(0)
    return cap


def abrir_bloqueio():
    tocar_som()

    janela = tk.Toplevel(root)
    janela.attributes("-fullscreen", True)
    janela.attributes("-topmost", True)
    janela.configure(bg="#222222")
    janela.protocol("WM_DELETE_WINDOW", lambda: None)

    tk.Label(janela, text="ACORDA!", font=("Helvetica", 32, "bold"),
             bg="#222222", fg="#FF5555").pack(pady=20)
    tk.Label(janela, text="Escaneie o QR Code para desligar o alarme",
             font=("Helvetica", 16), bg="#222222", fg="white").pack(pady=10)

    label_video = tk.Label(janela, bg="#222222")
    label_video.pack(pady=10)
    label_msg = tk.Label(janela, text="", font=("Helvetica", 14),
                         bg="#222222", fg="red")
    label_msg.pack()

    cap = abrir_camera()
    detector = cv2.QRCodeDetector()
    if not cap.isOpened():
        label_msg.config(text="Não consegui abrir nenhuma câmera!")

    def ler_camera():
        ok, frame = cap.read()
        if ok:
            texto, _, _ = detector.detectAndDecode(frame)
            if texto in CODIGOS_VALIDOS:
                cap.release()
                parar_som()
                janela.destroy()
                status_var.set("Alarme desativado")
                return
            elif texto:
                label_msg.config(text="QR Code errado!")

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb).resize((480, 360)))
            label_video.imgtk = img  # evita o Python apagar a imagem
            label_video.config(image=img)
        janela.after(30, ler_camera)

    ler_camera()


def verificar_alarme():
    global alarme_id
    if datetime.datetime.now() >= alvo:
        status_var.set("Alarme tocando!")
        abrir_bloqueio()
        return
    alarme_id = root.after(500, verificar_alarme)


def iniciar_alarme():
    global alarme_id, alvo
    if alarme_id:
        root.after_cancel(alarme_id)  # evita vários loops ao clicar de novo

    agora = datetime.datetime.now()
    alvo = agora.replace(hour=int(hour.get()), minute=int(minute.get()),
                         second=int(second.get()), microsecond=0)
    if alvo <= agora:
        alvo += datetime.timedelta(days=1)  # se já passou, vale pra amanhã

    status_var.set(f"Alarme para {alvo:%d/%m %H:%M:%S}")
    verificar_alarme()


def option(value):
    opt = tk.StringVar(root)
    opcoes = [str(i).zfill(2) for i in range(value)]
    opt.set(opcoes[0])
    tk.OptionMenu(frame, opt, *opcoes).pack(side=tk.LEFT, padx=10)
    return opt


# --- JANELA PRINCIPAL ---
root = tk.Tk()
root.geometry("500x300")
root.title("Desperta cabra Safado")
root.configure(bg="gray")

status_var = tk.StringVar(value="Alarme desativado")

tk.Label(root, text="Despertador", font=("Helvetica", 20, "bold"),
         bg="gray", fg="white").pack(pady=20)

frame = tk.Frame(root, bg="gray")
frame.pack(pady=10)
hour = option(24)
minute = option(60)
second = option(60)

tk.Label(root, textvariable=status_var, font=("Helvetica", 12),
         bg="gray", fg="white").pack(pady=10)
tk.Button(root, text="Definir Alarme", font=("Helvetica", 16, "bold"),
          bg="gray", fg="white", command=iniciar_alarme).pack(pady=15)

root.mainloop()