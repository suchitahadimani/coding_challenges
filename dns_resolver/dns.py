import struct
import socket
from io import BytesIO

# PART ONE SETTING UP DNS


def create_dns_header():
    #dns header, > for big endian and H is an unsigned short aka two bytes or 16 bits which is the lenght of each part (eg qdcount is 2 bytes)
    dns_header_format = ">HHHHHH"

    #random? shouldn't matter? 
    transaction_id = 22  
    # 1000 0000 0000 0000 since only qr is set
    flags = 0x0100
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

    return dns_header

#ok applying similiar logic to the dns_question field, the only thing is that the url can be variable-length

def convert_qname(qname):
    parts = qname.split(".")
    return b"".join(len(part).to_bytes(1, "big") + part.encode() for part in parts) + b"\x00"  #to_bytes "big" for big endian.

#qname will need a special function
def create_dns_question(url):
    qname = convert_qname(url)
    qtype = 1
    qclass = 1

    #s is for char[] or strings essentially
    dns_question_format = f"!{len(qname)}sHH"
    dns_question = struct.pack(
        dns_question_format,
        qname,
        qtype,
        qclass
    )
    return dns_question

# PART TWO ACTUALLY SENDING IT USING SOCKETS
#now that the dns is in shape, all thats needed is sending it across a socket to a server

def send_and_receive_dns(dns_query):

    HOST = "8.8.8.8"   #googles port and ip
    PORT = 53  

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)
    client_socket.sendto(dns_query,(HOST, PORT))

    response = client_socket.recv(1024)
    client_socket.close()
    return response

def parse_data(reader):
    parts = []
    length = reader.read(1)[0]  # Read the first length byte, indexing a byte converts it into an integer. could also use from bytes, just like there's a to_bytes
    #print(b"\x03"[0])
    while length != 0:
        if length & 0b1100_0000:
            parts.append(decompress(length, reader))
            break
        else:
            parts.append(reader.read(length).decode("utf-8"))
        
        length = reader.read(1)[0]
    
    return ".".join(parts)

    #print(b".".join(parts)) #parts are still in bytes, so when you do the join, you have to convert the "." to bytes too -- you have to take out the decode statement above though, 
    #print(".".join(parts)) #  or you could convert to string?

#don't need the original parse data now????
def parse_compressed_data(reader):
    parts = []
    length = reader.read(1)[0]
    while length != 0:
        if length & 0b1100_0000:
            parts.append(decompress(length, reader))
            break
        else:
            parts.append(reader.read(length).decode("utf-8"))
        
        length = reader.read(1)[0]
    return ".".join(parts)

def decompress(length, reader):
    #length = (reader.read(1)[0] ^ (3 << 6) )
    print("here")
    pointer_bytes = bytes([length & 0b0011_1111]) + reader.read(1) #this returns a pointer to the actual position where the information is located
    pointer = struct.unpack("!H", pointer_bytes)[0]
    current_pos = reader.tell()
    reader.seek(pointer)
    resp = parse_data(reader)
    reader.seek(current_pos)

    return resp



# PART THREE EXTRACT THE RESPONSE AND DETERMINE THE IP RESPONSE

def extract_response(response):
    reader = BytesIO(response)

    #This is the DNS header, garunteed to be 12 bytes long
    items = struct.unpack("!HHHHHH", reader.read(12)) 
    print(items)
    num_answers = items[3]
    num_auth = items[4]
    num_add = items[5]


    #DNS QUESTION SECTION -- in the format of length of subpart followed by part.
    parse_data(reader) # don't need to do anything with this actually

    #qname and qtype are garunteed to be next,
    data = reader.read(4)
    type_, class_ = struct.unpack("!HH", data)   # ! and > are both used to represent big-endianness but ! is a fixed sized used in networking the other one is platform-dependent sizing.

    #DNS RESPONSE FINALLY
    #because its compressed, the actual length starts after the first 2. 
    print(parse_data(reader)) 

    #the rest of the record type
    data = reader.read(10)
    type_, class_, ttl, data_len = struct.unpack("!HHIH", data) 
    print(type_,class_,ttl,data_len)







#PART FOUR -- GENERALIZE, PUT EVERYTHING INTO METHODS, MAKE IT REUSABLE

def perform_dns():
    dns_query = create_dns_header() + create_dns_question("dns.google.com")
    extract_response(send_and_receive_dns(dns_query))

perform_dns()
