from time import sleep
import socket,pickle,sys,json,os,random,time,datetime
from flask import Flask, url_for, send_from_directory
from werkzeug import secure_filename
from message_struct import MessageStruct
from client_socket import SocketDynamoClient

import logging, os
from flask import request, jsonify,Response
from flask import render_template
from consistentHashing import preference_list
from creating_bucket import create_bucket
from client_socket import bucket_creation_1, create_down_system,share_v_clock
from vectorclock import VectorClock
import json, random

peers_file_path='/home/HDUSER/clouda2/peers.txt'
gossip_file_path ='/home/HDUSER/clouda2/gossip.txt'

vec = VectorClock()
def createApp():
    resp_data = {}
    app = Flask(__name__)
    file_handler = logging.FileHandler('server.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
    UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
    UPLOAD_BUCKET_FOLDER = '/home/HDUSER/clouda2/uploads/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    if not os.path.exists(peers_file_path):
        node_list=['172.18.16.38','172.18.16.123','172.18.16.86','172.18.16.47']
        with open(peers_file_path, 'w') as fn:
            json.dump(node_list, fn)
        message = MessageStruct(9,'','',0,[],[],'','','',node_list,'','','',False)
        for node_ip in node_list:
            message.self_node=node_ip
            socketDynamoClient = SocketDynamoClient(node_ip,message)
            print(socketDynamoClient.send())

    def create_new_folder(local_dir):
        newpath = local_dir
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        return newpath
    
    
    
    @app.route('/buckets/<bucket_id>', methods = ['POST'])
    def bucket_creation(bucket_id):
        pref_list, node_list= preference_list(bucket_id)
        file_name = ""
        #print(pref_list)
        #print(bucket_id)
        operation_number = 1
        #print("Pref_list" , pref_list)
        resp,vector_clock_list = bucket_creation_1(bucket_id, operation_number,'', file_name, pref_list,0,[],False)
        
        replicas=[]
        #print("Response",resp)
        for i in range(len(pref_list)):
            if resp[i]:
                replicas.append(pref_list[i])
        
        is_bucket_created=False
        if len(replicas) >= 2:
            is_bucket_created=True

        resp_data['pref_list'] = pref_list
        resp_data['replicas_written']=replicas
        resp_data['is_bucket_created'] = is_bucket_created
        return jsonify(resp_data), 200
    
    @app.route('/buckets/<bucket_id>', methods = ['DELETE'])
    def bucket_delete(bucket_id):
        resp_data={}
        pref_list, node_list = preference_list(bucket_id)
        file_name = ""
        operation_number = 2
        
        is_bucket_deleted = False
        resp,vector_clock_list = bucket_creation_1(bucket_id, operation_number,'', file_name, pref_list,0,[],False)

        replicas=[]
        for i in range(len(pref_list)):
            if resp[i]:
                replicas.append(pref_list[i])

        if len(replicas) >= 2:
            is_bucket_deleted=True

        resp_data['pref_list'] = pref_list
        resp_data['replicas_deleted']=replicas        
        resp_data['is_bucket_deleted'] = is_bucket_deleted
        return jsonify(resp_data), 200   
    
    @app.route('/buckets/<bucket_id>/files', methods = ['POST'])
    def file_create_replace(bucket_id):
        vector_clock_list=[]
        resp_data={}
        file_content = request.files['file_content']
        file_name = secure_filename(file_content.filename)
        app.config['UPLOAD_BUCKET_FOLDER'] = UPLOAD_BUCKET_FOLDER+bucket_id
        create_new_folder(app.config['UPLOAD_BUCKET_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_BUCKET_FOLDER'], file_name)
        file_content.save(saved_path)
        pref_list, node_list = preference_list(bucket_id)
        #file_path = UPLOAD_BUCKET_FOLDER + bucket_id + file_name
        #print(file_path)
        operation_number = 3
        resp_data['pref_list'] = pref_list
        is_file_created = False
        resp = [] * 0
        resp, vector_clock_list = bucket_creation_1(bucket_id, operation_number, '',file_name, pref_list,0,[],False)
        share_v_clock(bucket_id, operation_number, '',file_name, pref_list,0,[],False)
        replicas=[]
        print(vector_clock_list)
        counter = 0
        data ={}
        with open('vec_clock.json', 'r') as f:
            data = json.load(f)
        print(data)
        resp_dict_vector = {}
        for i in range(len(pref_list)):
            if resp[i]:
                try:
                    print("hiiiiiiiiiiiiii")                
                    counter = data[pref_list[i]+"_"+bucket_id + "_"+file_name]
                    #print(pref_list[i]+"_"+bucket_id + "_"+file_name, counter)
                except Exception as e:
                    print(e)
                    counter = 0
                counter = counter+1
                #print(pref_list[i],counter)
                resp_dict_vector[pref_list[i] + "_" + bucket_id + "_" + file_name] = counter
                vec.update(pref_list[i]+"_" +  bucket_id + "_" + file_name, counter)
                replicas.append(pref_list[i])
                with open('vec_clock.json','w') as f:
                    json.dump(vec.clock, f)
        hinted_system=[]
        down_system = list(set(pref_list) - set(replicas))

        if len(replicas) == 1:
            temp_folder = "hinted"
            operation_number_hinted = 3
            operation_x =6
            hinted_system = list(set(node_list) - set(pref_list))
            #hinted_system = "172.18.16.47"
            print(file_name)
            resp = bucket_creation_1(bucket_id, operation_x, temp_folder, file_name, hinted_system, operation_number_hinted, down_system, False)
            if(resp):
                resp_data['hinted_system_data'] = hinted_system[0]

        if(len(replicas)==2):
            node_ip = random.choice(replicas)
            node_down_system = down_system[0]
            resp = create_down_system(node_ip, node_down_system, bucket_id, 8, file_name )
            if(resp):
                resp_data['down_system_data'] = down_system  
        print("downSystem is ",down_system)
    
        resp_data['pref_list'] = pref_list
        resp_data['replicas_written']=replicas        
        #resp_data['is_file_created'] = is_file_created
        resp_data['vector_clock_list'] = list(vector_clock_list)
        return jsonify(resp_data), 200 
    
    @app.route('/buckets/<bucket_id>/<file_id>', methods = ['DELETE'])
    def file_delete(bucket_id, file_id):
        resp_data={}
        pref_list = preference_list(bucket_id)
        #file_path = UPLOAD_BUCKET_FOLDER + bucket_id + file_name
        #print(file_path)
        operation_number = 4
        resp_data['pref_list'] = pref_list
        is_file_deleted = False
        resp,vector_clock_list = bucket_creation_1(bucket_id, operation_number, file_id, pref_list)
        
        
        replicas=[]
        for i in range(len(pref_list)):
            if resp[i]:
                replicas.append(pref_list[i])

        if len(replicas) >= 2:
            is_file_deleted=True

        resp_data['pref_list'] = pref_list
        resp_data['replicas_written']=replicas        
        resp_data['is_file_deleted'] = is_file_deleted

        return jsonify(resp_data), 200 
    
    @app.route('/checkServerStatus')
    def checkServer():
        return "Server Up and Running"

    return app
