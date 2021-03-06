import sys
import socket
import hashlib
from pymargo.core import Engine
from pysdskv.client import *
import matplotlib.pyplot as plt
import numpy as np
import random 



class SeerClient:

    def __init__(self, transport, address, p_id, db_n):
        self.engine = Engine(transport)
        self.server_addr = address
        self.provider_id = p_id
        self.db_name = db_n

        # init the engine
        self.client = SDSKVClient(self.engine)
        self.addr = self.engine.lookup(self.server_addr)
        self.provider_handle = self.client.create_provider_handle(self.addr, self.provider_id)
        self.db = self.provider_handle.open(self.db_name)

        # create a dictionary for values
        self.command_dic = {}
        self.used_unique_ids = []
        self.count = 0

        self.addingKeys = False
  
        # Generate Hash
        ip_addr = self.__getIP()
        self.hash_val = self.__generateHash(ip_addr)
  
        # excluded keys
        self.removed_keys = []


    def __getIP(self):
        hostname = socket.gethostname()    
        IPAddr = socket.gethostbyname(hostname)  
        return str(IPAddr)


    def __generateHash(self, value):
        hash_object = hashlib.md5(value.encode())
        temp_str = str(hash_object.hexdigest())
        return ( temp_str[0:8] )


    # Some Utility functions
    def put_keyval(self, key, val):
        self.db.put(key, val)


    def del_key(self, key):
        if (self.db.exists(key)):
            self.db.erase(key)
        else:
            return "key " + key +" does not exist!"


    def get_val(self, key):
        if (self.db.exists(key)):
            return self.db.get(key)
        else:
            return "key " + key +" does not exist!"


    def exists(self, key):
        return self.db.exists(key)


    def list_keyVal(self):
        key,val = self.db.list_keyvals()
        return key,valvlist_keyvals


    def shutdown(self):
        self.client.shutdown_service(self.addr)
        
  
    
    # User Operations
    def list_keys(self):
        """List my keys and general ones"""
        keys,vals = self.list_keyVal()
  
        my_keys = []
        for k in keys:
            if k.startswith(self.hash_val) or k.startswith("00000000"): 
                if k not in self.removed_keys:
                    my_keys.append(k)
    
        return my_keys


    def list_my_keys_only(self):
        """List my keys only"""
        key,val = self.list_keyVal()
  
        my_keys = []
        for k in key:
            if k.startswith(self.hash_val):   #my keys only
                if k not in self.removed_keys:
                    my_keys.append(k)
    
        return my_keys
    
    
    def get_value_at_ts(self, key, timestep):
        num_ranks = self.get_val("numRanks")
        values = []
        for r in range( int(num_ranks) ):
            temp_key = self.hash_val + "@" + key + "#" + str(r) + "|" + str(timestep)
            values.append( self.get_val(temp_key) )
        
        return values
            
       
 
    def set(self, key, value):
        """Adds a command"""
  
        # Format of keys:
        #  NEW_KEY@HASH
        #  HASH@Type:Command%count
  
        self.command_dic[key + "%" + str(self.count)] = value
        self.count = self.count + 1
  
        # Append to the list of removed keys
        if key == "DEL":
            self.removed_keys.append(value)


    def commit(self):
        """Send commands to database"""
        new_key = "NEW_KEY@" + self.hash_val

        # Loop until you can add a new key
        while ( self.db.exists(new_key) ): 
            continue


        # Add keys to mochi DB
        key_list = []
        self.addingKeys = True

        for key,val in self.command_dic.items():
            key_padded = self.hash_val + "@" + key  # add unique tag to each
   
            self.db.put(key_padded, val)            # put key in mochi db

            key_list.append(key)                    # save the key for later deletion

            print("key: ", key_padded)
            print("val: ", val)

        self.db.put(new_key, self.hash_val)  # adding keys done
        self.addingKeys = False

        # Delete keys
        for k in key_list:              # delete keys that have been added to db
            del self.command_dic[k]




# Run:
"""
import sys
sys.path.insert(1, '/home/pascal/projects/InWrap/python-utils')
import InWrapMochi
conn = InWrapMochi.InWrapMochi("na+sm","na+sm://2584/0",1,"foo")

Darwin:
import sys
sys.path.insert(1,'/projects/insituperf/InWrap/InWrap/python-utils')
import InWrapMochi
conn = InWrapMochi.InWrapMochi("ofi+tcp","ofi+tcp://192.168.101.184:1234",1,"struc1")
"""
