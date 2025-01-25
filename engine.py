import hashlib
import socket
import multiprocessing
import os
import signal

HOST = '127.0.0.1'
PORT = 22351

def break_MD5_process(hash, start, stop, result_container):
    current = start
    while current != stop:
        if hash == hashlib.md5(current.encode()).hexdigest():
            result_container.append(current)
            return
        current = nextOne(current)

def nextOne(password):
    i = len(password) - 1
    while password[i] == 'z':
        password = password[:i] + 'a' + password[i+1:]
        i = i - 1

    password = password[:i] + chr(ord(password[i]) + 1) + password[i+1:]
    return password

def start_engine():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        s.sendall(b'engine')

        ack = s.recv(1024).decode()
        if ack != "connected":
            print("Failed to connect to the server.")
            return

        procs = []
        container = multiprocessing.Manager().list()

        while True:
            data = s.recv(1024).decode()
            if not data:
                break

            if data == "terminate":
                for pid in procs:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except Exception as e:
                        print(f"Error: {e}")
                procs.clear()
                container[:] = []
                continue

            hash, start, stop = data.split(',')
            print(f"Starting to bruteforce hash: {hash} with {start}, {stop}")

            proc = multiprocessing.Process(target=break_MD5_process, args=(hash, start, stop, container))
            proc.start()
            procs.append(proc.pid)
            proc.join()

            if container:
                pswd = container[0]
                print(f"Found: {pswd}")
                s.sendall(f"found,{pswd}".encode())
                container[:] = [] # clear all
            else:
                s.sendall(b"failed")

if __name__ == "__main__":
    start_engine()