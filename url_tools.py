import re
import socket

def check_url(msg):
    url = re.findall('(www\.[\.a-z]+\.[a-z]{2,6})', msg)
    if url:
        print("Zachycena URL: "+url[0])
        return url[0]

def get_url_title(url_queue, run_list):
    while run_list[0] :
        url, clients = url_queue.get(True, None)
        
        if run_list[0]:        
            for (family, socktype, proto, canonname, sockaddr) in socket.getaddrinfo(url, 80, socket.AF_INET, socket.SOCK_STREAM):
            
                s = socket.socket(family, socktype, proto)         
                s.connect(sockaddr)
                s.settimeout(300)
                get = 'GET / HTTP/1.0\r\n\r\n'
                f = s.makefile(mode="rw")
                f.write(get)
                f.flush()            
                content = f.read()     
                
                if "<title>" in content.lower():
                    search="<title>(.+)</title>"
                    s = re.search(search,content,re.IGNORECASE)
                    title = s.group()[7:-8]
                    print("Prelozena URL: "+title)                
                
                    for client in clients.values():
                        if client.name:
                            client.info_message(title)     
        
    return


    