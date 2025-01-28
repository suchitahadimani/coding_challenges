import struct
import socket

# PART ONE SETTING UP DNS

#dns header, > for big endian and H is an unsigned short aka two bytes or 16 bits which is the lenght of each part (eg qdcount is 2 bytes)
dns_header_format = ">HHHHHH"

#random? shouldn't matter? 
transaction_id = 7   
# 1000 0000 0000 0000 since only qr is set
flags = (1 << 15) | (0 << 11) | (0 << 10) | (0 << 9) | (0 << 8) | (0 << 7) | (0 << 4)
qdcount = 1  
ancount = 0  
nscount = 0  
arcount = 0 

dns_header = struct.pack(
    dns_header_format,
    transaction_id,
    flags,
    qdcount,
    ancount,
    nscount,
    arcount
)

#ok applying similiar logic to the dns_question field, the only thing is that the url can be variable-length

#qname will need a special function

def convert_qname(qname):
    parts = qname.split(".")
    return b"".join(len(part).to_bytes(1, "big") + part.encode() for part in parts) + b"\x00"

qname = convert_qname("www.google.com")
qtype = 1
qclass = 1

#s is for char[] or strings essentially
dns_question_format = f">{len(qname)}sHH"
dns_question = struct.pack(
    dns_question_format,
    qname,
    qtype,
    qclass
)


dns_query = dns_header + dns_question
print("query: ", dns_query)



# PART TWO ACTUALLY SENDING IT USING SOCKETS
#now that the dns is in shape, all thats needed is sending it across a socket to a server

HOST = '8.8.8.8'   #googles port and ip
PORT = 53  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(dns_query)

response = client_socket.recv(1024)
client_socket.close()

print(f"Received from server: {response}")

# PART THREE EXTRACT THE RESPONSE AND DETERMINE THE IP RESPONSE



#PART FOUR -- GENERALIZE, PUT EVERYTHING INTO METHODS, MAKE IT REUSABLE