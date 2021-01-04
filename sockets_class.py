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
    
    N.B. It's not obvious whether to put much effort in to this:
     - If/when we switch to using (e.g.) AWS, then the whole socket-server
    part will become unnecessary, and only the front end remote.py
    module will retain any validity
    
    --------------------------------------------------------------
'''


# Import third-party packages
# --------------------------------------------------------------
import sys, os
import threading
import socket
from datetime import datetime
import time
import pickle
import numpy as np
import struct
import subprocess
import json

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

    default_server_host = { 'local1':'' ,
                            'local2':'127.0.0.1',
                            'mpcweb1':'131.142.195.56',
                            'mpcdb1':'131.142.192.107',
                            'marsden':'131.142.192.120'}["marsden"]
    default_server_port = 40001
    default_timeout = 11

    def __init__(self,):
        pass
        
    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def _send(self, s, data):
        ''' send data ...
        https://github.com/mdebbar/jsonsocket/blob/master/jsonsocket.py '''
        try:
            serialized = pickle.dumps(data)
        except Exception as e:
            raise error('You can only send pickleable data')
            
        # send the length of the serialized data first
        s.send(struct.pack('>I', len(serialized)))
                
        # send the encoded serialized data
        s.sendall(serialized)

    def _recv(self, s):
    
        # read the length of the data, letter by letter until we reach EOL
        raw_msglen = s.recv(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]

        # use a memoryview to receive the data chunk by chunk efficiently
        view = memoryview(bytearray(msglen))
        next_offset = 0
        while msglen - next_offset > 0:
            recv_size = s.recv_into(view[next_offset:], msglen - next_offset)
            next_offset += recv_size
        
        # deserialize from str to dict
        try:
            deserialized = pickle.loads( view.tobytes() )
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
        NB : Assumes input_data is pickleable
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

        return reply_dict


# Socket-Server-Related Object Definitions
# - This section has classes SPECIFIC to TESTING
# -------------------------------------------------------------
class Testing():
    ''' Convenience funcs/Utilities related to TESTING '''
    
    def _check_data_format_from_client( self, data ):
        ''' As test, just want a dict, nothing else examined '''
        assert isinstance(data, dict)

    def _check_data_format_from_server(self, data):
        ''' As test, just want a dict, nothing else examined '''
        assert isinstance(data, dict)
        
    def _function_to_be_evaluated(self, data_dict):
        return {'tested':data_dict}

# Socket-Server-Related Object Definitions
# - This section has classes SPECIFIC to ORBIT-FITTING
# -------------------------------------------------------------
class Orbfit():
    ''' Convenience funcs/Utilities related to ORBFIT-EXTENSION '''
    
    def __init__(self,):
        # Import the "orbit-extension" function
        import sys ; sys.path.append("/sa/orbit_pipeline")
        import update_existing_orbits


    def _check_data_format_from_client( self, data ):
    
        # check overall structure of data is a dict as required:
        # Outer dict, with desigs as keys, and dicts as values
        assert isinstance(data, dict)
        for v in data.values():
            assert isinstance(v, dict)
            
            # Each inner dict has keys: 'obslist', 'rwodict', 'eq0dict'
            assert len(v) == 3
            for k in ['obslist', 'rwodict', 'eq0dict']:
                assert k in v, f"keys = {v.keys()}"
        
            # check each component
            assert isinstance( v["obslist"], (list,tuple)), f""
            for item in v["obslist"]:
                assert isinstance(item, dict)
                
            assert isinstance(v["rwodict"] , dict)
            assert isinstance(v["eq0dict"] , dict)


    def _check_data_format_from_server(self, data):
        '''
        We expect ...
        data = {"K15HI1Q":
            {
                "obslist": returned_observations_list_of_dicts,
                "rwodict" : returned_rwo_dict
                "eq0dict" : returned_mid_epoch_dict,
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
            assert len(v) >= 4
            for k in ['obslist', 'rwodict', 'eq0dict', 'eq1dict']:#, 'badtrkdict']:
                assert k in v
            
            # check components of the dict
            assert isinstance(v['obslist'], (tuple, list))
            
            for d in v['obslist']:
                assert isinstance(d, dict)
                
            for k in ['rwodict', 'eq0dict', 'eq1dict']:#, 'badtrkdict']:
                assert isinstance(v[k] , dict)
   

    def _function_to_be_evaluated(self, data_dict):
        # Do orbit fit
        returned_dict = update_existing_orbits.update_existing_orbits(sample_dict)
        return returned_dict

class IOD():
    ''' Convenience funcs/Utilities related to Initial Orbit Determination '''
    
    def _check_data_format_from_client( self, data ):
        ''' ... '''
        assert isinstance(data, dict)

    def _check_data_format_from_server(self, data):
        ''' ... '''
        assert isinstance(data, dict)
        
    def _function_to_be_evaluated(self, data_dict):
        return {}


"""
class OrbfitServer(Server, Orbfit):
    '''
    Set up a server SPECIFIC to ORBIT-FITTING
    This is intended to be the production version
    '''

    def __init__(self, host=None, port=None):
    
        # Get access to relevant class methods
        Server.__init__(self,)
        Orbfit.__init__(self,)
        
        # Import the "orbit-extension function
        import sys ; sys.path.append("/sa/orbit_pipeline")
        import update_existing_orbits as update
        
        

    def _listen(self, startup_func = False ):
        '''
        Set-up server
        Allow functionality call(s)
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
            try:
                received   = self._recv(client)
                if received:
                    print(f"Data received in _listenToClient...")

                    # Check data format (expecting json_str)
                    self._check_data_format_from_client(received)
                    desigkeys = list(received.keys())
                    print(f"\t... {desigkeys}" )
                    
                    # Do orbit fit
                    returned_dict = update.update_existing_orbits(sample_dict)

                    # Send the results back to the client
                    self._send(client,returned_dict)
                    
                else:
                    print('Client disconnected')
                    raise
            except:
                client.close()
                return False
                
"""

# Socket-Server-Related Object Definitions
# - This section has class(es) able to call a variety of functions, ...
#   ... depending on the supplied input data
# -------------------------------------------------------------

class FunctionServer(Server):
    '''
    Set up a server able to call a number of functions, depending on the provided input
    This is intended to be the production version
    '''
    
    def __init__(self, host=None, port=None):
        '''
        This server gets instantiated once/rarely:
         - so we do a one-off import / instantiate all of the things we might need
        '''
        
        # Dictionary to hold possible classes
        # - These are used to
        # (i) define the tests of the required formats
        #(ii) define the main functional call to "evaluate" any supplied data
        dict_of_classes = {
            'test'      :   Testing() ,
            'orbfit'    :   Orbfit() ,
            'IOD'       :   IOD,
        }

        # Get access to relevant class methods
        Server.__init__(self,)
        

    def _listen(self, startup_func = False ):
        '''
        Set-up server
        Allow functionality call(s)
        '''
        # listen() enables a server to accept() connections
        # NB "5" is the max number of connection requests to queue-up
        self.sock.listen(5)
        print('\nFunctionServer is listening...')
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
            try:
                received   = self._recv(client)
                if received:
                    print(f"Data received in _listenToClient...")
                    
                    # Check received data is a dictionary
                    assert isinstance(received, dict) and len(received) == 1
                    
                    # Get request type & get the supplied data out of the dict ...
                    request_type    = list(received.keys())[0]
                    data_dict       = received[request_type]
                    assert isinstance(data_dict, dict)

                    # The class we'll use to access testing & evaluation functions ...
                    # - This is being determined using the "request_type"
                    C = dict_of_classes[request_type]

                    # Check data
                    C._check_data_format_from_client(data_dict)
                    
                    # Call the function to be evaluated from the class
                    returned_dict = C._function_to_be_evaluated(data_dict)
                    print(f'returned_dict={returned_dict}')
                    # Send the results back to the client
                    self._send(client,returned_dict)
                    
                else:
                    print('Client disconnected')
                    raise
            except:
                client.close()
                return False


    # The 2 funcs below may be useful for general validation purposes ...
    # ... the detailed functions for *DICTIONARIES* will be defined in individual classes

    def _check_json_from_client(self, json_string ):
        # Convert json-str to dict & then validate
        self._check_data_format_from_client( json.loads(json_string) )
    
    def _check_json_from_server(self, json_string ):
        # Convert json-str to dict & then validate
        self._check_data_format_from_server( json.loads(json_string) )
