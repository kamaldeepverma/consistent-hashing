PROBLEM STATEMENT

This is a Distributed System which provides REST-based APIs for an object-based storage service for
the following requirements.
-User should be able to create/delete a bucket
-User should be able to create/delete files in a given bucket

The API should returns the following in a JSON object:
-Success or failure
-Vector clocks of all replicas
-Node number where the write took place (in case of write)

The implementation of the object storage system should have the following characteristics as explained in
The Amazon's Dynamo paper.
-Data is partitioned and replicated using consistent hashing. Number of nodes (VMs) should be at
least 3.
-High availability for writes using vector clocks with reconciliation during reads. Consistency is
facilitated by object versioning using vector clocks and application-level conflict resolution in case
of conflicts
-Temporary failures in replicas is handled by sloppy quorum technique and hinted hand-off.
-Failures of nodes is detected by a gossip based distributed failure detection. 


==========================================================================================================
SYSTEM IMPLEMENTATION DETAILS

System Configuration: 
	Cluster of Physical Machines : 4
	Replication Factor: 3
	Read Quorum (R): 2
	Write Quorum (W): 2
	
File Description
	1. app.py ------------------------------------> Rest Service Source Code(Flask Application)
	2. consistent_hashing -------------------------> Consistent Hashing implementation source code
	3. sloppy_quorum_hinted_handoff.py --------------------------> Sloppy Quorum ,Hinted Hand Off and Gossip protocol Implementation
	4. message_struct ----------------------------> Object Message Structure passed over socket
	5. server_socket.py and client_socket.py------>	Vector Clock Handling,Bucket creation/Deletion,File creation/deletion implementation
							
How to Run the Application
1. Run the REST server through running run.py file. (python run.py)
2. Run all the socket servers on every node by running server_socket.py (python server_socket.py)
3. Run Sloppy Quorum & Hinted HandOff Schedular on every node by running sloppy_quorum_hinted_handoff.py (python sloppy_quorum_hinted_handoff.py)
4. REST Service END POINTS

	a) http://172.18.16.47:6003/buckets/<bucked_id>       methods = ['POST']
		where bucket_id is the name of bucket/folder. 
		Result: Buckets will be created in every up Node under '/home/<user>/object_store/buckets/'
		Status : 200 OK 
	b) http://172.18.16.47:6003/buckets/<bucked_id>       methods = ['DELETE']
		where bucket_id is the name of bucket/folder. 
		Result: Buckets will be deleted from every up Node under '/home/<user>/object_store/buckets/'
		Status : 200 OK 
	c) http://172.18.16.47:6003/buckets/<bucket_id>/files     methods = ['POST']
		I/P: place file under form_data, body section by selecting files.
		Output 1: If all nodes are up, Write the files and update the respective vector clock
		Sample Output: 
				{
				  "pref_list": [
				    "172.18.16.86",
				    "172.18.16.123",
				    "172.18.16.47"
				  ],
				  "replicas_written": [
				    "172.18.16.86",
				    "172.18.16.123",
				    "172.18.16.47"
				  ],
				  "vector_clock_list": [
				    "172.18.16.86 : 14 , 172.18.16.123 : 14 , 172.18.16.47 : 14 "
				  ]
				}
		
		Output 2: If two nodes are up, wrtie the files in respective two nodes. Place the down node into down_system.json file by calling operation number 8. 
		HintedHandoff will take care of whenever the node will be up, it will run retry_down_system and place the content into the node whenever it will give true
		response. Please Check HintedHandOff Terminal for Output.
		Sample Output:
				{
				  "down_system_data": [
				    "172.18.16.86"
				  ],
				  "pref_list": [
				    "172.18.16.86",
				    "172.18.16.123",
				    "172.18.16.47"
				  ],
				  "replicas_written": [
				    "172.18.16.123",
				    "172.18.16.47"
				  ],
				  "vector_clock_list": [
				    "172.18.16.86 : 15 , 172.18.16.123 : 15 , 172.18.16.47 : 15 "
				  ]
				}

		
		Output 3: If Only one node is up, write the files in respective node. Find the hintedNode. Place the file on hintedNode so that quorum can be reached. 
		A file will be created on hinted system named hinted.json which will contain the hints of the down nodes. Whenever any of the down node is up, its entry 
		is removed from hinted.json and another hint is sent to any of the up node from the preference list and down_system.json is updated there. Whenever the 
		node will be up, files will be sent through node which have hint about the down system. Please Check sloppy_quorum_hinted_handoff Terminal for Output.
		Sample Output:
				{
				  "hinted_system_data": "172.18.16.38",
				  "pref_list": [
				    "172.18.16.86",
				    "172.18.16.123",
				    "172.18.16.47"
				  ],
				  "replicas_written": [
				    "172.18.16.47"
				  ],
				  "vector_clock_list": [
				    "172.18.16.86 : 15 , 172.18.16.123 : 16 , 172.18.16.47 : 16 "
				  ]
				}
		
	d) http://172.18.16.47:6003/buckets/<bucket_id>/<file_id>	  methods = ['DELETE']
		where file_id is the name of file to be deleted.
		Result: File will be deleted from the respective bucket_id
		Status: 200 Ok

5. Additional Notes:
	1. Gossip Based Protocol:
		This will be run through sloppy_quorum_hinted_handoff.py which is basically a scheduler and calling create_gossip function periodically. We read from peer_list
		which contains node_list. Gossip is being created by any random node. We are picking any random node from node_list and sending gossip which will eventually
		create a gossip.txt file. We will keep doing this in iterative way so that gossip reaches to every node in the node list. 

