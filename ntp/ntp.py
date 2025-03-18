import struct
import socket
from io import BytesIO
import time

TIME1970 = 2208988800 
ntp_server = "pool.ntp.org"
PORT = 123
HOST = socket.gethostbyname(ntp_server)


def create_header(t):
    #B8 H16 I32 Q64
    ntp_header_format = "!B B B B I I I Q Q Q Q"
    
    #000011011 
    first_byte = (0 << 0) | (3 << 3) | 3 
    stratum = 0  
    poll = 7  
    precision = 18  

    root_delay = 0
    root_dispersion = 0
    reference_id = 0

    timestamp = 0
   
    ntp_header = struct.pack(
        ntp_header_format,
        first_byte,
        stratum,
        poll,
        precision,
        root_delay,
        root_dispersion,
        reference_id,
        int(t),  # Reference Timestamp
        timestamp,  # Origin Timestamp (same as reference)
        timestamp,  # Receive Timestamp (same as reference)
        timestamp
    )

    return ntp_header



t0 = time.time()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(5)
client_socket.sendto(create_header(t0),(HOST, PORT))
response = client_socket.recv(1024)
client_socket.close()

t3 = time.time()

reader = BytesIO(response)
items = struct.unpack("!BBBBIIIIIIIIIII", reader.read(48)) 

if(items[1] == 0):
    print("KISS OF DEATH")

t1 = items[11] + (items[12] / 2.0 ** 32.0) - TIME1970
t2 = items[13] + (items[14] / 2.0 ** 32.0) - TIME1970

offset = ((t1 - t0) + (t2 - t3)) / 2
delta = ((t3 - t0) - (t2 - t1)) / 2

print(f"Offset: {offset}")
print(f"Delta: {delta}")
print(f"Local Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}")
print(f"Adjusted Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + offset))}")