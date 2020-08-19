#!/usr/bin/python3           # This is server.py file
import socket,pickle,os,shutil, json,random

from message_struct import MessageStruct
from client_socket import SocketDynamoClient

path='/home/HDUSER/clouda2/buckets/'
# hinted_path=path+'hinted/'
peers_file_path='/home/HDUSER/clouda2/peers.txt'
gossip_file_path ='/home/HDUSER/clouda2/gossip.txt'

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
port = 9995                                           
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('', port))                                  
serversocket.listen(5)                                         
print("server in listening mode")

def create_vector_clock(vector_clock_path,vector_clock):
    with open(vector_clock_path,'w') as f:
        json.dump(vector_clock, f)

while True:
    # establish a connection
    clientsocket,addr = serversocket.accept()      

    print("Got a connection from %s" % str(addr))

    # message = MessageStruct(0,'','','','',0,[],False)
    message = MessageStruct(0, '', '', 0, [], [], '', '', '', [], '','','',False)
    message_string = clientsocket.recv(1024)
    message = pickle.loads(message_string)
   
    
    if message.operation==3:
        

        print(message.operation)
        print(message.bucket_key)

        try:

            file_path = path+message.bucket_key+'/'+message.file_name
            f = open(file_path, 'wb')
            clientsocket.send('s'.encode('ascii'))
            print('file opened')

            vector_clock_path=file_path+'.metadata'
            
            vector_clock={}
            if os.path.exists(vector_clock_path):
                with open(vector_clock_path, 'r') as fv:
                    vector_clock = json.load(fv)
            else:
                vector_clock = { x:1 for x in message.preference_list}
                print(vector_clock)
                
            serialized_vector_clock = json.dumps(vector_clock)
            
            version=int(vector_clock[message.self_node])
            version=version+1
            vector_clock_new=vector_clock
            vector_clock_new[message.self_node]=version
            

            create_vector_clock(vector_clock_path,vector_clock_new)
            print(vector_clock)
            data = clientsocket.recv(1024)
            clientsocket.send(serialized_vector_clock.encode('ascii'))
            #clientsocket.send(str(version).encode('ascii'))

            while True:
                print('receiving data...')
                data = clientsocket.recv(1024)
                print('data=%s', (data))
                if not data:
                    break
                f.write(data)
            
            f.close()
            
            print("file written")            
        


        except FileNotFoundError as e:
            clientsocket.send('f'.encode('ascii'))
            print("Error: %s - %s." % (e.filename, e.strerror))

        clientsocket.close()



    elif message.operation == 6:
        print("i am in equal to 6 case")
        print(message.operation)
        print(message.bucket_key)
        print(message.file_name)
        clientsocket.send('Acknowledgement'.encode('ascii'))
        print("test")
        file_path = path+message.temp_folder+'/'+message.file_name
        print(file_path)
        try:
            f = open(file_path, 'wb')
        except FileNotFoundError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        print('file opened')
        while True:
            print('receiving data...')
            data = clientsocket.recv(1024)
            print('data=%s', (data))
            if not data:
                break
            f.write(data)
            
        f.close()

        path2 = path +message.temp_folder+"/"+"hinted.json"
        print(path2)
        
        data =[]
        try:
            fh = open(path2,'r')
            
        except FileNotFoundError as e:
            print("File Not Found")
        data = json.load(fh)
        fh.close()
        with open(path2, 'w') as f:
            for system in message.failed_nodes:
                str1 = system + "_" + message.bucket_key+"_"+str(message.hinted_operation)+"_"+message.file_name
                if(str1 not in data):
                    data.append(str1)
            json.dump(data, f)
        print("file written")

        clientsocket.close()
        
    elif message.operation == 8:
        print("i am in equal to 8th case")
        clientsocket.send('Acknowledgement'.encode('ascii'))
        file_path = "/home/HDUSER/clouda2/down_system.json"
        data = []
        try:
            fh = open(file_path,'r')
            
        except FileNotFoundError as e:
            print("File Not Found")
        data = json.load(fh)
        fh.close()
        with open(file_path,'w') as f:
            str1 = message.node_down_system + "_" + message.bucket_key+"_" + str(message.hinted_operation)+"_"+message.file_name
            if(str1 not in data):
                data.append(str1)
            json.dump(data,f)
        print("down system file created")
        clientsocket.close()
    
    elif message.operation == 11:
        print("i am in equal to 11 case")
        print(message.operation)
        print(message.bucket_key)
        print(message.file_name)
        clientsocket.send('Acknowledgement'.encode('ascii'))
        print("test")
        file_path = path+message.bucket_key+'/'+message.file_name
        print(file_path)
        try:
            f = open(file_path, 'wb+')
        except FileNotFoundError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        print('file opened')
        while True:
            print('receiving data...')
            data = clientsocket.recv(1024)
            print('data=%s', (data))
            if not data:
                break
            f.write(data)
        f.close()
        clientsocket.close()

    else:
        

        print(message.operation)
        print(message.bucket_key)

        if message.operation==1:
            bucket_path=path+message.bucket_key
            try: 
                os.mkdir(bucket_path) 

            except OSError as e: 
                print("Error: %s - %s." % (e.filename, e.strerror))
            
            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()

        elif message.operation==2:
            bucket_path=path+message.bucket_key
            try:
                shutil.rmtree(bucket_path)
            except OSError as e:
                print ("Error: %s - %s." % (e.filename, e.strerror))
            
            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()

        elif message.operation==4:
            file_path=path+message.bucket_key+'/'+message.file_name
            if os.path.exists(file_path):
                os.remove(file_path)
                os.remove(file_path+'.metadata')
            else:
                print("The file does not exist")
            
            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()

        elif message.operation==5:
            
            print('preference_list:'+str(message.preference_list))
            print('self node:'+str(message.self_node))
            x=[]
            x.append(message.self_node)
            other_replica_nodes=list(set(message.preference_list)-set(x))
            print('other_replica_nodes:'+str(other_replica_nodes))
            file_path = path+message.bucket_key+'/'+message.file_name
            vector_clock_path=file_path+'.metadata'
            vector_clock={}
            
            with open(vector_clock_path, 'r') as fv:
                vector_clock = json.load(fv)
            
            message.my_node_ip=message.self_node
            message.my_vector=vector_clock[message.self_node]
            message.operation=7
            print(vector_clock)

            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()
            print('connection closed')

            for node_ip in other_replica_nodes:
                socketDynamoClient = SocketDynamoClient(node_ip,message)
                socketDynamoClient.send()

        
        elif message.operation==7:
            file_path = path+message.bucket_key+'/'+message.file_name
            vector_clock_path=file_path+'.metadata'
            vector_clock={}
            with open(vector_clock_path, 'r') as fv:
                vector_clock = json.load(fv)
            print(message.my_node_ip)
            print(message.my_vector)
            vector_clock[message.my_node_ip]=message.my_vector
            create_vector_clock(vector_clock_path,vector_clock)
            print(vector_clock)
            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()
            
        elif message.operation==9:
            x=[]
            x.append(message.self_node)
            peers_list=list(set(message.node_list)-set(x))

            with open(peers_file_path, 'w') as fp:
                json.dump(peers_list, fp)
            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()
        
        elif message.operation==10:
            with open(gossip_file_path, "a") as fg:
                fg.write(message.gossip)
            print('gossip written to file')
            clientsocket.send('Acknowledgement'.encode('ascii'))
            clientsocket.close()        
            x=[]
            res=True
            vclk={}
            if len(message.preference_list)==1:
                print(message.preference_list)
                x.append(message.preference_list[0])
                message.preference_list=[]
                print(message.preference_list)      
                socketDynamoClient = SocketDynamoClient(x[0],message)
                res,vclk=socketDynamoClient.send()

            
            elif len(message.preference_list)>=1:
                print(message.preference_list)
                x.append(random.choice(message.preference_list))      
                message.preference_list=list(set(message.preference_list)-set(x))
                socketDynamoClient = SocketDynamoClient(x[0],message)
                res,vclk=socketDynamoClient.send()

            # Failure Detection through gossip
            if res == False:
                with open(gossip_file_path, "a") as fg:
                    gossp=x[0]+':Node is Unreachable'
                    fg.write(gossp)


    # clientsocket.close()


serversocket.close()