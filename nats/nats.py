#!/usr/bin/env python3

import asyncio
import sys

if(len(sys.argv) == 2):
    PORT = int(sys.argv[1])
else:
    PORT = 4222

HOST = "127.0.0.1"

topics = dict()

#creates a subscriber object to allow for broadcastings
class Subscriber:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.sid = set()
        self.map = dict()

        #topic:id
        #id

    def add_sid(self, id, topic):
        if(id in self.sid):
            return False
        
        if topic in self.map:
            r = self.map[topic]
            self.sid.remove(r)


        self.sid.add(id)
        self.map[topic] = id
        return True

    def remove_sid(self, id):
        if(id not in self.sid):
            return None
        
        topic = None
        for i, j in self.map.items():
            if j == id:
                topic = i
                break

        if topic:
            self.map.pop(topic)
            self.sid.discard(id)

        return topic


#constantly reads data from client connections
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    
    writer.write("Connected to localhost. \nType 'exit' to quit.\n".encode())  
    await writer.drain() 
    writer.write(f"INFO: HOST: {addr[0]}  PORT: {addr[1]}\n".encode())  
    await writer.drain() 

    me = Subscriber(reader, writer)

    #check for initial connection
    run = True
    try:
        data = await asyncio.wait_for(reader.read(100), timeout=10)
        if not data:
            run = False
        req = data.decode().split()
        if req[0].lower() != "connect" and req[0].lower() != "connect{}":
            writer.write("'Unknown Protocol Operation'\n".encode())
            await writer.drain()
            run = False
        else:
            writer.write("+OK\n".encode())  
            await writer.drain() 
    except asyncio.TimeoutError:
        run = False
        print("Timed out")


    
    while run:
        try:
            data = await asyncio.wait_for(reader.read(100), timeout=30)
            if not data:
                break
            req = data.decode().strip()
            print(f"Received: {req} from {addr}")
            
            #PING RESPONSE
            if(req.upper() == "PING"):
                writer.write("PONG\n".encode())  
                await writer.drain()  
            
            #EXIT RESPONSE
            if(req.upper() == "EXIT"):
                run=False 
            
            commands = req.split()
            
            #PUB SUB AND UNSUB REPONSES
            if(len(commands) > 1):

                if(commands[0].upper() == "PUB"):
                    await do_pub(commands, reader, writer)

                if(commands[0].upper() == "SUB"):
                    if(me.add_sid(commands[2], commands[1])):
                        topics.setdefault(commands[1], []).append(me)
                        writer.write("+OK\n".encode())  
                        await writer.drain()
                    else:
                        writer.write("ID already used\n".encode())  
                        await writer.drain()
                
                if(commands[0].upper() == "UNSUB"):
                    t = me.remove_sid(commands[1])
                    if t:
                        if me in topics[t]:
                            topics[t].remove(me)
                        writer.write("+OK\n".encode())  
                        await writer.drain()

                    else:
                        writer.write("ID not found\n".encode())  
                        await writer.drain()

        except Exception as e:
            run = False
            print(f"Exception occurred: {e}")
            writer.write("Stale Connection..\n".encode())  
    
    #REMOVES SUBSCRIBER FROM ALL TOPICS BEFORE CLOSING TO PREVENT ANY ISSUES
    for topic in topics.values():
        if me in topic:
            topic.remove(me)

    writer.write("Closing..\n".encode())  
    await writer.drain()

    print(f"Closing connection from {addr}")
    writer.close()
    await writer.wait_closed()


#ASYNC METHOD FOR DEALING WITH PUBS
async def do_pub(commands, reader, writer):
    topic = commands[1]
    size = int(commands[2])

    if topic not in topics or not topics[topic]:
        writer.write("Topic Unavailable\n".encode())
        await writer.drain()
        return

    data = await asyncio.wait_for(reader.read(size), timeout=10)
    if not data:
        return 
    
    req = data.decode().strip()
    writer.write("+OK\n".encode())  
    await writer.drain()



    for client in topics.get(topic, []):
        if topic in client.map:
            client.writer.write(f"MSG {topic} {client.map[topic]} {size}\n{req}\n".encode())  
            await client.writer.drain()



#keeps creating connections
async def main(): 
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()



if __name__ == "__main__":
    asyncio.run(main())
