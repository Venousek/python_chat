import asyncore
import socket
import threading
import queue
import re
from client import Client
from url_tools import check_url, get_url_title
from config import config_cmd, config_file

config = None
lock = None
url_thread = None
url_queue = None
clients = {}

NEW_LINE_RN = "\r\n"
NEW_LINE_RN_B = b"\r\n"
NEW_LINE_N = "\n"
NEW_LINE_N_B = b"\n"

class ChatHandler(asyncore.dispatcher_with_send):
    
    def handle_read(self):
        addr = self.getpeername()
        client = clients[addr]
        
        client.lock.acquire()
        data = self.recv(8192)
        client.lock.release()
        
        if not data:
            self.close()
        else:
            dataStr = ""
            try:
                dataStr = data.decode()
            except UnicodeDecodeError:
                return    
            
            if (NEW_LINE_RN not in dataStr) & (NEW_LINE_N not in dataStr):
                client.buffer += dataStr
            else:
                if NEW_LINE_RN in dataStr:
                    if client.new_line_b != NEW_LINE_RN_B:
                        client.new_line_b = NEW_LINE_RN_B
                        client.new_line = NEW_LINE_RN
                else:
                    if client.new_line_b != NEW_LINE_N_B:
                        client.new_line_b = NEW_LINE_N_B
                        client.new_line = NEW_LINE_N
                           
                msg = client.buffer              
                dataStrSplit = dataStr.split(client.new_line)                
                msg += dataStrSplit[0]
                client.buffer = dataStrSplit[1]
                
                if not client.name:
                    if client.new_client(msg):
                        info_message("Pripojil se "+msg)
                else:
                    message(addr, msg)                  
            
    def handle_close(self):        
        addr = self.getpeername()
        
        client = clients[addr]
        del clients[addr]
          
        if (client is not None) & (client.name is not None):
            print("Odpojil se "+client.name, addr)
            info_message("Odpojil se "+client.name)            
        else:
            print("Odpojil se", addr)         
            

class ChatServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(int(config['max_clients']))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:            
            sock, addr = pair
            if len(clients) < int(config['max_clients']):
                client = Client()
                client.socket = sock
                client.buffer = ""
                client.addr = addr
                client.clients = clients
                client.lock = lock
                client.url_queue = url_queue                
                clients[addr] = client                
                print('Nove spojeni: ', addr)
                handler = ChatHandler(sock)
                client.handler = handler
                client.send_line(config['welcome_str'])
                client.send_line("Zadejte prosim sve jmeno:")
            else:
                sock.send(b'Bohuzel byl prekrocen maximalni pocet pripojeni k serveru. :(')
                
                
def private_message(addr, names, msg):
    print("Soukroma zprava " + clients[addr].name + ': ' + msg)     
    lowerNames = [x.lower() for x in names] 
    recipients = {}           
    for client in clients.values():
        if (client.name is not None) & (client.name.lower() in lowerNames):
            client.private_message(clients[addr], msg)
            recipients[client.addr] = client
            
    url = check_url(msg)
    if url:
        recipients[addr] = clients[addr]
        url_queue.put_nowait((url, recipients))
           
            
def message(addr, msg):
    
    names = re.findall("(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z_]+[A-Za-z0-9_]+)", msg)
    if names:
        private_message(addr, names, msg)
    else:   
        print(clients[addr].name+': '+msg)                    
        for client in clients.values():
            if client.name:
                client.message(clients[addr], msg)
        url = check_url(msg)
        if url:
            url_queue.put_nowait((url, clients))
            
def info_message(msg):
    for client in clients.values():
        if client.name:
            client.info_message(msg)          
       
            
if __name__ == "__main__":       
    print("Spoustim server chatu!")
    
    commandline_config = config_cmd()
    file_config = config_file({"default_config.ini", "config.ini"})
    
    final_config = file_config._sections['server']
    final_config.update((k, v) for k, v in vars(commandline_config[0]).items() if (v is not None or k not in final_config.keys()))
    config = dict(final_config)
    
    print("Nastaveni:")
    print(config)    
    
    lock = threading.Lock()
    url_queue = queue.Queue()
    run_list = [True]
    url_thread = threading.Thread(target = get_url_title, args = (url_queue, run_list))
    url_thread.start()
    server = ChatServer(config['ip'], int(config['port']))
    try:
        asyncore.loop(timeout=1)
    except KeyboardInterrupt:
        print("Vypinam server.")
        for client in clients.values():
            client.info_message("Server byl ukoncen. Sbohem. :(")
            client.handler.close()
        run_list[0] = False
        url_queue.put_nowait((0,0))
        

