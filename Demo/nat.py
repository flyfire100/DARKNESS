#! /usr/bin/env python
#! -*- coding:utf-8 -*-
import socketserver,sys,time,connections
import random,threading
msgbox={}
msgbox_lock = threading.Lock()
 
 
def pop_msg(address):
    print("pop msg %s"%address)
    if msgbox_lock.acquire(timeout=5) == True:
       try:
           if address in msgbox.keys():
               return msgbox.pop(address)
           return ''
       except:
           return ''
       finally:
           msgbox_lock.release()
    else:
       raise 'oh , pop_msg exception'
    
def insert_msg(address,msg):
    print(msg)
    if msgbox_lock.acquire(timeout=5) == True:
        try:
            if address not in msgbox.keys():
                msgbox[address]=[]
            msgbox[address].append(msg)
            return 'ok'
        except:
            return 'insert failed'
        finally:
            msgbox_lock.release()
    else:
        raise 'oh , insert_msg exception'   
 
def gen_check_code(address):
    #from ledger.db get address's publick key
    #then encode the check_code
    return random.randrange(10000000000000,9999999999999999)
 
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self): # server defined here
        global address_dict
        peer_ip = self.request.getpeername()[0]
        timeout_operation = 120
        timer_operation = time.time()
        try:
            #receive register
            data = connections.receive(self.request, 10)
            if data != 'register':
                raise 'client is not register'
            #receive address
            address = connections.receive(self.request, 10)
            check_code =  gen_check_code(address)
            connections.send(self.request, check_code , 10)
            data = connections.receive(self.request, 10)
            if data != check_code :
                connections.send(self.request, 'you are fake' , 10)
                raise 'client are fake'
            connections.send(self.request, 'what can i do for you?' , 10)
            data = connections.receive(self.request, 10)
            if data == 'sendmsg':
                address = connections.receive(self.request, 10)
                sequence = connections.receive(self.request, 10)
                msg = connections.receive(self.request, 10)
                timestamp =  time.time()
                result = insert_msg( address , (timestamp,sequence,msg) )
                connections.send(self.request, result , 10)
            elif data == 'getmsg':
                msg = pop_msg(address)
                connections.send(self.request, msg , 10)
               
        except Exception as e:
            print(e)
        finally:
            if self.request:
                self.request.close()
 
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
 
 
if __name__ == "__main__":
    try:
        HOST, PORT = "0.0.0.0", int(sys.argv[1])
        ThreadedTCPServer.allow_reuse_address = True
        ThreadedTCPServer.daemon_threads = True
        ThreadedTCPServer.timeout = 60
        ThreadedTCPServer.request_queue_size = 100
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        ip, port = server.server_address
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        while True:
            print(msgbox)
            time.sleep(5)
        server.shutdown()
        server.server_close()
    except Exception as e:
        print(e)
        print("server startup failed!")
        sys.exit()