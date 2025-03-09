#!/usr/bin/env python3

#the shebang checks the first line for an interpreter directive  --> default is sh and must be changed to python3 to ensure it is compiled correctly
import socket
import sys
import time


if(len(sys.argv) > 2):
    print("Sorry, please enter one url to trace!")
    exit()

url = sys.argv[1]
try:
    destination_ip = socket.gethostbyname(url)
except socket.gaierror as e:
    print("Please enter a valid URL.")
    exit()

print(f"traceroute to {url} ({destination_ip}), 64 hops max, 32 byte packets")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   
HOPS = 1

#have to use dgram on mac
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
print("Listening for ICMP packets...")
addr = ["0.0.0.0"]

while addr[0] != destination_ip:
    try:
        curr = time.time()
        client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, HOPS)   #sets the time to live to 1 HOPS OMG WAI SO DO I KEEP INCREMENTING THIS?
        client_socket.sendto(b"hi",(url, 33435))
        packet, addr = sock.recvfrom(1024)  
        sock.settimeout(5)
        print(f"{HOPS} {socket.gethostbyaddr(addr[0])[0]} ({addr[0]})  {round((time.time()-curr)*1000, 3)} ms")
    except socket.timeout as e:
        print(f"{HOPS} * * *")
    except socket.herror as e:
        print(f"{HOPS} {addr[0]} ({addr[0]})  {round((time.time()-curr)*1000, 3)} ms")

    HOPS += 1





