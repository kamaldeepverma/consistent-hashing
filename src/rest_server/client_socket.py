#!/usr/bin/python3           # This is client.py file
import time
import socket,pickle,sys,json
from message_struct import MessageStruct
import threading

path = '~/object_store/uploads/'
port = 9995

resp=[0]*3
flag = False

class SocketDynamoClient:
    def __init__(self, node_ip, message):
        self.node_ip = node_ip
        self.message = message

    def send(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                           
        try:
            s.connect((self.node_ip, port))
            message_string = pickle.dumps(self.message)
            
            if self.message.operation==3:
                
                s.send(message_string)
                data = s.recv(1024)
                ack=str(data.decode('ascii'))
                if ack =='f':
                    return False,{}                

                s.send('ack'.encode('ascii'))
                data = s.recv(1024)
                vector_clock = json.loads(data.decode('ascii'))
                

                if(self.message.flag == False):
                    file_path=path+self.message.bucket_key+'/'+self.message.file_name
                else:
                    file_path = "~/object_store/buckets/hinted/"+self.message.file_name


                f = open(file_path,'rb')
                l = f.read(1024)
                while (l):
                    s.send(l)
                    l = f.read(1024)
                f.close()
                
                s.close()
                return True,vector_clock

            elif self.message.operation == 6:
                s.send(message_string)
                data = s.recv(1024)
                file_path=path+self.message.bucket_key+'/'+self.message.file_name
                f = open(file_path,'rb')
                l = f.read(1024)
                while (l):
                    s.send(l)
                    l = f.read(1024)
                f.close()
                s.close()
                return True,{}

            elif self.message.operation == 8:
                s.send(message_string)
                data = s.recv(1024)
                s.close()
                return True,{}


            elif self.message.operation ==11:
                s.send(message_string)
                data = s.recv(1024)
                path2 = "~/object_store/buckets/"
                file_path_2=path2+self.message.bucket_key+'/'+self.message.file_name
                f = open(file_path_2,'rb')
                l = f.read(1024)
                while (l):
                    s.send(l)
                    print('Sent ',repr(l))
                    l = f.read(1024)
                f.close()
                s.close()
                return True,{}


            else:
                s.send(message_string)
                data = s.recv(1024)
                s.close()
                return True,{}
        
        except  socket.error as err:
            return False,{}
        except Exception as err:
            return False,{}


def share_v_clock(bucket_name, operation_number, temp_folder, file_name, pref_list, hinted_operation, failed_nodes, flag):
    message = MessageStruct(operation_number,bucket_name, file_name, hinted_operation, failed_nodes, pref_list,'','','',[],'','',temp_folder,False)
    message.operation=5
    time.sleep(0.1)
    for node_ip in pref_list:
        message.self_node=node_ip
        socketDynamoClient = SocketDynamoClient(node_ip,message)
        socketDynamoClient.send()
        time.sleep(0.1)

def socket_thread(idx,node_ip,message):
    socketDynamoClient = SocketDynamoClient(node_ip,message)
    resp[idx],vclock=socketDynamoClient.send()
    vector_clock_list.append(vclock)
    

def bucket_creation_1(bucket_name, operation_number, temp_folder, file_name, pref_list, hinted_operation, failed_nodes, flag):

    message = MessageStruct(operation_number,bucket_name, file_name, hinted_operation, failed_nodes, pref_list,'','','',[],'','',temp_folder,False)
    vector_clock_list=[]
    idx=0
    for node_ip in pref_list:
        message.self_node=node_ip
        socketDynamoClient = SocketDynamoClient(node_ip,message)
        resp[idx],vclock=socketDynamoClient.send()
        vector_clock_list.append(vclock)
        idx=idx+1


    unique_vector_clocks=[]
    for dict in vector_clock_list:
        vector_string=''
        for k,v in dict.items():
            vector_string=vector_string+k+' : '+str(v)+' , '
        if vector_string:
            unique_vector_clocks.append(vector_string[:-2])

    unique_vector_clocks = set(unique_vector_clocks)
    
    return resp,unique_vector_clocks

def check_failed_Node(node_ip, bucket_name, operation_number, file_name):
    flag = True
    message = MessageStruct(operation_number,bucket_name, file_name, 0, '', [],'','','',[],'','','',True)
    message.self_node =  node_ip 
    socketDynamoClient = SocketDynamoClient(node_ip,message)
    x = socketDynamoClient.send()
    return x
def create_down_system(node_ip, node_down_system, bucket_name, operation_number, file_name):
    
    message = MessageStruct(operation_number,bucket_name, file_name, 3, '', [],'','','',[],'',node_down_system,'',False)
    
    socketDynamoClient = SocketDynamoClient(node_ip,message)
    x = socketDynamoClient.send()
    return x

def check_failed_Node_2(node_ip, bucket_name, operation_number, file_name):
    
    message = MessageStruct(operation_number,bucket_name, file_name, 0, '', [],'','','',[],'','','',False)

    socketDynamoClient = SocketDynamoClient(node_ip,message)
    x = socketDynamoClient.send()
    return x

