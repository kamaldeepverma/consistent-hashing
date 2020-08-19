class MessageStruct:
    def __init__(self, operation, bucket_key, file_name,hinted_operation,failed_nodes,preference_list,self_node,my_node_ip,my_vector,node_list,gossip,node_down_system,temp_folder,flag):
        self.operation = operation
        self.bucket_key = bucket_key
        self.file_name = file_name
        self.hinted_operation = hinted_operation
        self.failed_nodes = failed_nodes
        self.preference_list=preference_list
        self.self_node=self_node
        self.my_node_ip=my_node_ip
        self.my_vector=my_vector
        self.node_list=node_list
        self.gossip=gossip
        self.node_down_system = node_down_system
        self.temp_folder = temp_folder
        self.flag = flag
        

