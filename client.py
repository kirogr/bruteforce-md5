import socket

HOST = '127.0.0.1'
PORT = 22351

def start_client():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((HOST, PORT))
    soc.sendall(b"client")

    ack = soc.recv(1024).decode()
    if ack != "connected":
        print("Failed to connect to the server")
        return

    while True:
        hash = input("Enter MD5 hash: ")
        start = input("Enter start: ")
        stop = input("Enter stop: ")

        command = f"{hash},{start},{stop}"

        soc.sendall(command.encode())

        res = soc.recv(1024).decode()
        print(res)

if __name__ == "__main__":
    start_client()