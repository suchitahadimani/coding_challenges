#!/usr/bin/env python3

import asyncio
import sys
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional
import time


if(len(sys.argv) == 3):
    PORT = int(sys.argv[2])
else:
    PORT = 11211

HOST = "127.0.0.1"


class Values(BaseModel):
    flags: str
    exptime: int
    storetime: int
    datasize: int
    noreply: bool
    data: Optional[str]  


cached: dict[str, Values] = {}
#p = Person("Bob", 25, 5.9)
#print(p.name, p.age, p.height) 


#reader and writer will always the parameters for the function passed into start_server
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr}")

    while True:
        data = await reader.read(100)  # Read up to 100 bytes
        if not data:
            break
        req = data.decode()
        print(f"Received: {req} from {addr}")


        response = await handle_request(req, reader)

        writer.write(response.encode())  
        await writer.drain()  

    print(f"Closing connection from {addr}")
    writer.close()
    await writer.wait_closed()


async def handle_request(req, reader):
    # get, set, stats

    # <command name> <key> <flags> <exptime> <byte count> [noreply]\r\n
    #    <data block>\r\n
    arr = req.split()
    if(arr[0] == "set"):
        try:
            if(len(arr) == 5):
                nr = True
            else:
                nr = bool(arr[5] != "noreply")
            
            v = Values(flags=arr[2], exptime=int(arr[3]), storetime= int(time.time()), datasize=int(arr[4]), noreply=nr, data="")
             
            data = await reader.read(v.datasize)
            if not data:
                return "Error: Data block not received properly.\n"
            
            v.data = data.decode()
            cached[arr[1]] = v

            if not v.noreply:
                return ""
            
            return "STORED\n"
        
        except: 
            return "Invalid Set\n"
    

    #VALUE <data block> <flags> <byte count>
    if(arr[0] == "get"):
        if(arr[1] in cached):
            v = cached[arr[1]]
            if(v.exptime < 0):
                cached.pop(arr[1])
                return "END\n"
            
            if(v.exptime > 0 and time.time() - v.storetime > v.exptime):
                cached.pop(arr[1])
                return "END\n"
                
            return "VALUE" + str(v.data) + str(v.flags) + str(v.datasize) + '\n'
        
        return "END\n"
    
    return req

async def main(): 

    server = await asyncio.start_server(handle_client, HOST, PORT)

    async with server:
        await server.serve_forever()



if __name__ == "__main__":
    asyncio.run(main())
