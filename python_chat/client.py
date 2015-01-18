import re

class Client():
    
    def __init__(self):
        self.addr = None
        self.socket = None
        self.name = None
        self.buffer = ""
        self.new_line = "\r\n"
        self.new_line_b = b"\r\n"
        self.clients = {}
        self.lock = None
        self.url_queue = None
        self.handler = None

    def new_client(self, msg):
        if re.search(r"\s", msg):
            self.send_line("Jmeno nesmi obsahovat mezery!")
            self.send_line("")
            self.send_line("Zadejte jine jmeno:")
        else:
            for client in self.clients.values():
                if client.name is None:
                    continue
                if client.name.lower() == msg.lower():
                    self.send_line("Uzivatel s timto jmenem jiz existuje!")
                    #self.send_line("Zadejte jine jmeno:")            
                    self.handler.close()
                    break          
            else:                
                self.name = msg
                print('Pripojil se '+self.name)
                return True
                
    def private_message(self, fromClient, msg):
        self.send_line("")
        self.send_line(fromClient.name+" pise primo:")
        self.send_line(">> "+msg)
    
    def message(self, fromClient, msg):     
        if fromClient.addr != self.addr:   
            self.send_line("")
            self.send_line(fromClient.name+" pise:")
            self.send_line("> "+msg)
        
    def info_message(self, msg):        
        self.send_line("")
        self.send_line("INFO: "+msg)
    
    def send_line(self, line):
        self.socket.send(str.encode(line))  
        self.socket.send(self.new_line_b)