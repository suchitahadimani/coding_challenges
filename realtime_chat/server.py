import socket
import threading 


all_clients = []
lock = threading.Lock()


def send_chat(conn, addr):
    global all_clients
    with lock:
        all_clients.append(conn)
        #print(all_clients)
    
    print(f"Connected by {addr}")
    name = data = conn.recv(1024) 
    while True:
        data = conn.recv(1024)  # Reads up to 1024 bytes of data sent by the client.
        if not data:
            break
        message = (name.decode() + ": " + data.decode()+'\n')

        with lock:
            for c in all_clients:
                if c is not conn:
                    c.sendall(message.encode())

            #conn.sendall(data)  #sends back data sent by client, which defines it as an echo server
    with lock:
        all_clients.remove(conn)
    conn.close()


HOST = "127.0.0.1"  # (localhost)
PORT = 7007

#building a tcp server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.bind((HOST,PORT))
server_socket.listen()

while True:
    #to make this multithreaded you might have to create a new thread every time a new connection is established.
    conn, addr = server_socket.accept()  #returns ip and port of the client addresss
    client = threading.Thread(target=send_chat, args=(conn,addr,))
    client.start()



