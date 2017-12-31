#! /usr/bin/env python
#! -*- coding:utf-8 -*-
import socks,sys,connections
import uuid,random,time
import threading
from multiprocessing import Pool,Process
 
name=''
msgs_dict={}
 
def get_address():
    global name
    return name
 
def get_nats_info():
    fd = open('nats.txt','r')
    if fd:
       return fd.readlines()
 
nats=get_nats_info()
 
 
def communicate_nat( nat , command='getmsg' , address='' , sequence='' , msg='' ):
    global name
    #print(nat)
    ip = nat.split(':')[0]
    port = nat.split(':')[1]
    nat = socks.socksocket()
    nat.connect((str(ip), int(str(port))))
    connections.send(nat,'register',10)
    if address == '':
        address = name
    connections.send(nat,address,10)
    check_code = connections.receive(nat,10)
    #print("get check_code is %s"%check_code)
    connections.send(nat,check_code,10)
    result = connections.receive(nat,10)
    #print("get result is : %s"%result)
    if result != 'what can i do for you?':
        nat.close()
        print('reject by nat server %s'%nat)
    if command == 'getmsg':
        connections.send(nat,'getmsg',10)
        msg = connections.receive(nat,10)
        nat.close()
        return msg
    elif command == 'sendmsg':
        connections.send(nat,'sendmsg',10)
        connections.send(nat,address,10)
        connections.send(nat,sequence,10)
        connections.send(nat,msg,10)
        result = connections.receive(nat,10)
        nat.close()
        return result
 
 
def print_complete_msg():
    global msgs_dict
    #print(msgs_dict)
    del_sequence_list = []
    for sequence in msgs_dict.keys():
        #print(sequence)
        msgs = ''
        try:
            msg = {}
            i = 0
            #print(msgs_dict[sequence])
            while 100*(i+1) < int( msgs_dict[sequence][0][1] ):    
                msg[ msgs_dict[sequence][i][0] ] = msgs_dict[sequence][i][2]
                i = i+1
            msg[ msgs_dict[sequence][i][0] ] = msgs_dict[sequence][i][2]
            print("msg=",msg)
            j = 0
            while j <= i:
                msgs = msgs + msg[str(j)]
                j = j+1
            del_sequence_list.append(sequence)
        except Exception as e:
            print(e)
            continue
        else:
            print(msgs)
    for key in del_sequence_list:
        del(msgs_dict[key])
 
def get_msg( ):
    global nats
    for nat in nats:
        msgs_list =  communicate_nat( nat )
        msgs_list = eval( str(msgs_list) )
        for msg in msgs_list:
            if msg != '':
                sequence = msg[1].split('/')[2]
                index = msg[1].split('/')[0]
                length = msg[1].split('/')[1]
                data = msg[2]
                if sequence in msgs_dict.keys():
                    msgs_dict[sequence].append( (index , length , data )  )
                else:
                    msgs_dict[sequence] = [ (index , length , data ) ]   
        #print(msgs_dict)
 
 
def send_msg():
    global nats
    msg_dict={}
    address = input("please input peer address : ")
    if address == '':
        return
    msg = input("please input your msg to send : ")
    msg_size = len(msg)
    i=0
    msg_uuid=str(uuid.uuid4())
    while int( len(msg)/100 )  > 0:
        msg_dict[str(i)+'/'+ str(msg_size) +'/'+msg_uuid]=msg[0:99]
        msg = msg[100:]
        i = i+1
    msg_dict[str(i)+'/'+str(msg_size)+'/'+msg_uuid]=msg
    for sequence in msg_dict.keys():
        while True:
            result = communicate_nat( nats[random.randrange(len(nats))] , 'sendmsg' , address , sequence , msg_dict[sequence] )
            if result == 'ok':
                break
            else:
                continue  
 
 
if __name__ == '__main__':
    name = input("please input your name: ")
    while True:
        send_msg()
        get_msg()
        print_complete_msg()