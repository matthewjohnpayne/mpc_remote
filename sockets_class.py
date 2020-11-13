# -*- coding: utf-8 -*-

'''
    --------------------------------------------------------------
    Developing a sockets module.
    
    Nov 2020
    Matt Payne
    
    This module is intended to let me develop some knowledge of
    how to handle server-client connections
    
    It is intended to set up a server (e.g. on marsden) that will
    listen for requests for data from clients (either on marsden,
    and/or on some other machine such as mpcweb1, which is publically visible).

    It is expected that this will be of use in (e.g.) cheby_checker,
    orbit-fitting, ...
    
    --------------------------------------------------------------
'''


# Import third-party packages
# --------------------------------------------------------------
import sys, os
import pytest
import threading
import socket
from datetime import datetime
import time
import pickle
import numpy as np
import struct
import subprocess
import json
import zlib

# Import local module
# --------------------------------------------------------------
import sample_data

# Socket-Server-Related Object Definitions
# - This section has GENERIC / PARENT classes
# --------------------------------------------------------------


class Shared():
    '''
    Primarily used to provide shared methods
    to send & receive messages of arbitrary length/size
    https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
    
    '''

    default_server_host = {'local1':'' , 'local2':'127.0.0.1', 'mpcweb1':'131.142.195.56', 'mpcdb1':'131.142.192.107', 'marsden':'131.142.192.120'}["marsden"]
    default_server_port = 40001
    default_timeout = 11

    def __init__(self,):
        pass

    '''
    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)
        sock.sendall(msg)

    def recv_msg(self, sock):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(sock, msglen)

    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    '''
    def _send(self, s, data):
        ''' send data ...
        https://github.com/mdebbar/jsonsocket/blob/master/jsonsocket.py '''
        try:
            serialized = pickle.dumps(data)
        except Exception as e:
            raise error('You can only send pickleable data')
            
        # send the length of the serialized data first
        print(f"_send: len(serialized)={len(serialized)} , struct.pack('>I', len(serialized))={struct.pack('>I', len(serialized))}")
        s.send(struct.pack('>I', len(serialized)))
                
        # send the encoded serialized data
        s.sendall(serialized)

    def _recv(self, s):
    
        # read the length of the data, letter by letter until we reach EOL
        total = s.recv(4)
        total = struct.unpack('>I', total)[0]
        
        # use a memoryview to receive the data chunk by chunk efficiently
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            recv_size = s.recv_into(view[next_offset:], total - next_offset)
            next_offset += recv_size
        
        # deserialize from str to dict
        try:
            deserialized = pickle.loads( view.tobytes() )
            print("deserialized=",deserialized)
        except Exception as e:
            raise error('Data could not be unpickled')
        return deserialized


class Server(Shared):
    '''
    Class to help with setting up a socket-server that will listen for clients
    Intended to act as a parent to multiple types of MPC-server classes
     - (e.g. orbit-fitting, checking/attribution, ...)
    '''

    def __init__(self, host=None, port=None):
        
        self.host = host if host is not None else self.default_server_host
        self.port = port if port is not None else self.default_server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #  associate the socket with a specific network interface and port number
        self.sock.bind((self.host, self.port))


class Client(Shared):
    '''
    General class & method(s) for connecting to server
    '''

    def __init__(self, host=None, port=None):
        ''' specify host & port on initialization '''
        self.server_host = host if host is not None else self.default_server_host
        self.server_port = port if port is not None else self.default_server_port
        
    def connect(self, input_data, VERBOSE = False ):
        '''
        dumb client : just passes the data through & collects reply from the server
        NB : Assumes input_data ~ dict, and can be converted to json
        '''
        # Create a socket objects
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # How long to wait before timeout?
            s.settimeout(self.default_timeout)
            
            # Connect to the server
            s.connect((self.server_host, self.server_port))
            
            # Send data to the server
            #self.send_msg(s, input_data)
            self._send(s, input_data)

            # Read the reply from the server
            reply_dict = self._recv(s)
            print(f"decoded reply_dict from server ={reply_dict}")

        return reply_dict



# Socket-Server-Related Object Definitions
# - This section has classes SPECIFIC to ORBIT-FITTING
# -------------------------------------------------------------
class OrbfitServer(Server):
    '''
    Set up a server SPECIFIC to ORBIT-FITTING
    This is intended to be the production version
    '''

    def __init__(self, host=None, port=None):
        Server.__init__(self,)

    def _listen(self, startup_func = False ):
        '''
        Demo function to illustrate how to set-up server
        and to allow tests of various functionalities
        '''
        # listen() enables a server to accept() connections
        # NB "5" is the max number of connection requests to queue-up
        self.sock.listen(5)
        print('\nOrbfitServer is listening...')
        while True :
            
            # accept() blocks and waits for an incoming connection.
            # One thing that’s imperative to understand is that we now have a
            # new socket object from accept(). This is important since it’s the
            # socket that you’ll use to communicate with the client. It’s distinct
            # from the listening socket that the server is using to accept new
            # connections:
            client, address = self.sock.accept()
            client.settimeout(self.default_timeout)
            
            # Either of the below work ...
            #self._demoListenToClient(client,address)
            threading.Thread(target = self._listenToClient,
                             args = (client,address)).start()

    def _listenToClient(self, client, address):
        '''
        This will...
        (i) receive a message from a client
        (ii) check that the received data format is as expected
        (iii) do an orbit fit [NOT YET CONNECTED]
        (iv) send results of orbit fit back to client
        
        NB Note that it assumes it is being sent JSON DATA
        
        '''
        while True:
            if True:
                received   = self._recv(client)
                #received = client.recv(1024)
                if received:
                    print(f"Data recieved in _listenToClient: N_bytes = {sys.getsizeof(received)}")
                    print(f"received={received}, type() = {type(received)}")

                    # Check data format (expecting json_str)
                    self._check_data_format_from_client(received)

                    # Do orbit fit [NOT YET IMPLEMENTED]
                    returned_dict = self.fitting_function( received )

                    # Send the results back to the client
                    self._send(client,returned_dict)
                    
                else:
                    raise error('Client disconnected')
            else:
                client.close()
                return False
                


    def fitting_function(self, input_json ):
        ''' Do orbit fit [NOT YET IMPLEMENTED] '''
        # The returned quantities are expected to be ...
        # 'obslist', 'rwodict', 'eq0dict', 'eq1dict', 'badtrkdict'
        return sample_data.sample_output_dict_empty()
        
        
    def _check_json_from_client(self, json_string ):
        # Convert json-str to dict & then validate
        self._check_data_format_from_client( json.loads(json_string) )
    
    def _check_json_from_server(self, json_string ):
        # Convert json-str to dict & then validate
        self._check_data_format_from_server( json.loads(json_string) )

    def _check_data_format_from_client( self, data ):
    
        # check overall structure of data is a dict as required:
        # Outer dict, with desigs as keys, and dicts as values
        assert isinstance(data, dict)
        for v in data.values():
            assert isinstance(v, dict)
            
            # Each inner dict has keys: 'obslist', 'rwodict', 'eq0dict'
            assert len(v) == 3
            for k in ['obslist', 'rwodict', 'elsdict']:
                assert k in v, f"keys = {v.keys()}"
        
            # check each component
            assert isinstance( v["obslist"], (list,tuple)), f""
            for item in v["obslist"]:
                assert isinstance(item, dict)
                
            assert isinstance(v["rwodict"] , dict)
            
            assert isinstance(v["elsdict"] , dict)


    def _check_data_format_from_server(self, data):
        '''
        We expect ...
        data = {"K15HI1Q":
            {
                "obslist": returned_observations_list_of_dicts,
                "rwodict" : returned_rwo_dict
                "elsdict" : returned_mid_epoch_dict,
                "eq1dict" : returned_standard_epoch_dict,
                "badtrkdict" : return_quality_dict
            }
        }
        '''
        # check overall structure of data is a dict as required:
        # Outer dict, with desigs as keys, and dicts as values
        assert isinstance(data, dict)
        for v in data.values():
            assert isinstance(v, dict)

            # check overall structure of data is a dict as required
            assert len(v) == 5
            for k in ['obslist', 'rwodict', 'eq0dict', 'eq1dict', 'badtrkdict']:
                assert k in v
            
            # check components of the dict
            assert isinstance(v['obslist'], (tuple, list))
            
            for d in v['obslist']:
                assert isinstance(d, dict)
                
            for k in ['rwodict', 'eq0dict', 'eq1dict', 'badtrkdict']:
                assert isinstance(v[k] , dict)
   
