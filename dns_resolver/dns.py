import struct


#packing data

#the > means its big endian
format_string = '>I f 5s' 
binary_data = struct.pack(format_string, 42, 3.14, b'hello')
print(binary_data)  # Output: b'*\x00\x00\x00\xc3\xf5H@\x68\x65\x6c\x6c\x6f'


# unpacking the binary data
original_data = struct.unpack(format_string, binary_data)
print(original_data)  # Output: (42, 3.14, b'hello')




#dns header, > for big endian and H is an unsigned short aka two bytes or 16 bits which is the lenght of each part 
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