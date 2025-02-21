import socket
import threading

HOST = "127.0.0.1"  
PORT = 7007  

def listener(socket):
    while True:
        response = socket.recv(1024)   
        if not response:
            break
        print(f"{response.decode()}")




client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))  #YOU NEED TO CONNECT FOR TCP 
name = input("Enter your name:")
client_socket.sendall(name.encode())
client_thread = threading.Thread(target=listener, args=(client_socket,) , daemon=True)
client_thread.start()

while True:
    message = input()
    if message == "quit":
        break
    client_socket.sendall(message.encode())
    

client_socket.close()