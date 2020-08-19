import schedule
import time,json
import socket,pickle,sys,json,os,random,time,datetime
from message_struct import MessageStruct
from client_socket import SocketDynamoClient
from client_socket import check_failed_Node, create_down_system, check_failed_Node_2
data = []
path = "/home/HDUSER/clouda2/buckets/hinted/hinted.json"
path2 = "/home/HDUSER/clouda2/down_system.json"
peers_file_path='/home/HDUSER/clouda2/peers.txt'
gossip_file_path ='/home/HDUSER/clouda2/gossip.txt'
def retry_failing_nodes():
    with open(path,'r') as f:
        data = json.load(f)
        print("Running")
        print("data is ",data)
    for d in data:
        x = d.split("_")
        resp, vec_clock = check_failed_Node(x[0], x[1], int(x[2]), x[3])
        print("this is response", resp)
        substr = "_"+x[1]+"_"+x[2]+"_"+x[3]
        if(resp == True):
            data.remove(d)
            print(d,"has been removed from the hinted.json list")
            print("############################################")
            print(data)    
            print("#####################################")
            for d in data:
                if(d.find(substr)):
                    y = d.split("_")
                    print(y)
                    resp = create_down_system(x[0],y[0],y[1],8,y[3])
                    print(resp)
                    data.remove(d)
                    print("Similiar data have been removed from hinted.json file")
                    with open(path2,'w') as f:
                        json.dump(data,f)

        with open(path, 'w') as f:
            json.dump(data,f)
def retry_down_system():
    print("######################################################")
    with open(path2,'r') as f:
        data_down = json.load(f)
    for d in data_down:
        x = d.split("_")
        resp, vec_clock = check_failed_Node_2(x[0], x[1], 11, x[3])
        if(resp == True):
            data_down.remove(d)
            print(d,"has been removed from the down_system.json list")
            print("############################################")
            print(data_down)    
            print("#####################################")
        with open(path2, 'w') as f:
            json.dump(data_down,f)
def create_gossip(gossip):
    peers_list=[]
    with open(peers_file_path, 'r') as fp:
        peers_list= json.load(fp)
    x=[]
    x.append(random.choice(peers_list))
    message = MessageStruct(10,'','',0,[],[],'','','','','','','',False)
    message.preference_list=list(set(peers_list)-set(x))
    message.gossip=gossip
    with open(gossip_file_path, "a") as fg:
        fg.write(gossip)
    print(message.preference_list)
    print(x[0])
    socketDynamoClient = SocketDynamoClient(x[0],message)
    res, vclk = socketDynamoClient.send()
    # Failure Detection through gossip
    if res == False:
        with open(gossip_file_path, "a") as fg:
            gossp=x[0]+':Node is Unreachable'
            fg.write(gossp)

schedule.every(10).seconds.do(retry_failing_nodes)
schedule.every(25).seconds.do(retry_down_system)
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
msg = st+'File there is virus in demo file\n'
schedule.every(120).seconds.do(create_gossip, msg)
if __name__ =="__main__":
    while(1):
        schedule.run_pending()
        time.sleep(1)
