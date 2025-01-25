import socket
import threading

HOST = '127.0.0.1'
PORT = 22351

engines = []
clients = {}

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST, PORT))
soc.listen()

def char_to_num (string):
    stop_str = string[::-1]
    stop_num = 0
    for x,i in enumerate(stop_str):
        stop_num += (26**x) *(ord(i) - ord('a'))

    return stop_num

def num_to_char(num):
    str_num = ""
    # num%26, => num / 26  |||=> str= str[::-1]
    while num!=0:
        str_num=str_num + chr(num%26 + ord('a'))
        num= int (num/26)

    while len(str_num)<6:
        str_num=str_num + 'a'

    str_reverse = str_num[::-1]

    return str_reverse

# def splitting (s_start, s_stop):
#     total = char_to_num(s_stop) - char_to_num(s_start)
#     t_start = char_to_num(s_start)
#     t_stop = char_to_num(s_stop)
#     part = int (total / len(engines))
#     e_list = []
#     while (t_start+part)<t_stop:
#         e_list.append((num_to_char(t_start), num_to_char(t_start+part)))
#         t_start = t_start + part
#
#     if ((t_start + part) > t_stop):
#         e_list.append((num_to_char(t_start), num_to_char(t_stop)))
#
#     return e_list

def splitting(start, stop):
    start_dec = char_to_num(start)
    stop_dec = char_to_num(stop)

    total_range = stop_dec - start_dec
    range_size = (total_range + len(engines) - 1) // len(engines)

    ranges = []
    for i in range(len(engines)):
        chunk_start = start_dec + i * range_size
        chunk_end = min(chunk_start + range_size - 1, stop_dec)

        ranges.append(
            (
                num_to_char(chunk_start),
                num_to_char(chunk_end)
            )
        )

    if ranges[-1][1] != stop:
        ranges[-1] = (ranges[-1][0], stop)

    return ranges

def kill_engines():
    for engine in engines:
        try:
            engine.sendall(b"terminate")
        except Exception as e:
            print(f"Error: {e}")
            engines.remove(engine)

def handle_client(client_socket, client_address):
    print(f"Connected by {client_address}")

    client_type = client_socket.recv(1024).decode()
    if not client_type:
        client_socket.close()
        return

    if client_type == "engine":
        engines.append(client_socket)
        print(f"Engine #{len(engines)} connected with address {client_address}")
        client_socket.sendall(b"connected")
        threading.Thread(target=handle_engine, args=(client_socket,)).start()
    elif client_type == "client":
        print(f"Client connected using address {client_address}")
        client_socket.sendall(b"connected")
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            hash_to_break, cstart, cstop = data.split(",")

            print(f"Requested Hash: {hash_to_break}")
            clients[client_address] = (client_socket, hash_to_break)

            if(len(engines) == 0):
                client_socket.sendall(b"notfound")
                break

            ranges = splitting(str(cstart), str(cstop))
            for engine, (start, stop) in zip(engines, ranges):
                engine.sendall(f"{hash_to_break},{start},{stop}".encode())

        client_socket.close()
        print(f"Connection {client_address} closed")

def handle_engine(engine_socket):
    while True:
        try:
            message = engine_socket.recv(1024).decode()
            if not message:
                break

            if "found" in message:
                _, found_password = message.split(',', 1)
                print(f"Hash found: {found_password}")

                for client_address, (client_socket, requested_hash) in clients.items():
                    try:
                        if requested_hash:
                            client_socket.sendall(f"found,{found_password}".encode())
                            kill_engines()
                    except Exception as e:
                        print(f"Error: {e}")

                break
            elif "failed" in message:
                print("Engine failed")
        except Exception as e:
            print(f"Error: {e}")
            break

    engine_socket.close()
    engines.remove(engine_socket)

while True:
    client_socket, client_address = soc.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()