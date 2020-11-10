# -*- coding: utf-8 -*-

'''
    --------------------------------------------------------------
    Developing a prototype sockets module.
    
    Oct 2020
    Matt Payne
    
    This module is intended to let me develop some knowledge of
    how to handle server-client connections
    
    It is intended to set up a server (e.g. on marsden) that will
    listen for requests for data from clients (either on marsden,
    and/or on some other machines).
     - Later on, this could also be extended to Docker/ECS/EKS

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


# Import neighboring packages
# --------------------------------------------------------------
# None

# Convenience functions while developing
# --------------------------------------------------------------
def launch_orbit_fitting_socket_server():
    ''' Utility function to launch an example of the server-class defined below '''
    OS = OrbfitServer()
    print(f"Launched socket server: OS.host={OS.host}, OS.port={OS.port}")
    OS._listen( startup_func = True )

def launch_demo_orbit_fitting_socket_server():
    ''' Utility function to launch an example of the *Demo* server-class defined below '''
    OS = DemoOrbfitServer()
    print(f"Launched demo socket server: OS.host={OS.host}, OS.port={OS.port}")
    OS._demo_listen( startup_func = True )


# Socket-Server-Related Object Definitions
# - This section has GENERIC / PARENT classes
# --------------------------------------------------------------
class SharedSocket(object):
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

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
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



class Server(SharedSocket):
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


class Client(SharedSocket):
    '''
    General class & method(s) for connecting to server
    Intended to facilitate connection to different MPC servers
    Intended to act as a parent to multiple MPC-client classes
     - (e.g. orbit-fitting, checking/attribution, ...)
    '''

    def __init__(self, host=None, port=None):
        ''' specify host & port on initialization '''
        self.server_host = host if host is not None else self.default_server_host
        self.server_port = port if port is not None else self.default_server_port
    
    def _pickleclient(self, message_data , VERBOSE = False ):
        '''
        Does the work of sending message to server and receiving reply
        It assumes that the message to send is "pickleable"
        It assumes that the reply it recives is "pickled" and hence unpickles it
        '''

        # Pickle the provided data dictionary
        pickled = pickle.dumps(message_data)

        if VERBOSE:
            print("message_data to-be-sent \tRAW    :\t...",message_data)
            print("message_data to-be-sent \tPICKLED:\t...",pickled)

        # Create a socket objects
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # How long to wait before timeout?
            s.settimeout(self.default_timeout)
            
            # Connect to the server
            s.connect((self.server_host, self.server_port))
            
            # Send data to the server
            self.send_msg(s, pickled)
            
            # Read the reply from the server
            # and unpickle it
            data_string = self.recv_msg(s)
            unpickled   = pickle.loads(data_string)
            
            if VERBOSE:
                print("message-dict received (after unpickling)...",unpickled)
        
        return unpickled





# Socket-Server-Related Object Definitions
# - This section has classes SPECIFIC to ORBIT-FITTING
# --------------------------------------------------------------
class Orbfit():
    '''
    Mainly used to provide shared methods to OrbfitServer & OrbfitClient
    Mainly enforcing data echange standards ...
    '''
    def __init__(self,):
        pass
        
    def _check_data_format_from_client( self, data ):
    
        # check overall structure of data is a dict as required
        assert isinstance(data, dict)
        assert len(data) == 3
        for k in ["observations_list_of_dicts", "rwo_dict", "mid_epoch_dict"]:
            assert k in data
        
        # check components of the dict
        assert isinstance( data["observations_list_of_dicts"], (list,tuple))
        for item in data["observations_list_of_dicts"]:
            assert isinstance(item, dict)
        assert isinstance(data["rwo_dict"] , dict)
        assert isinstance(data["mid_epoch_dict"] , dict)
        
        # return componenets separated-out
        return data["observations_list_of_dicts"],data["rwo_dict"], data["mid_epoch_dict"]
        
    def _check_data_format_from_server(self, data):
        '''
        We expect ...
        data = {
            "observations_list_of_dicts": returned_observations_list_of_dicts,
            "rwo_dict" : returned_rwo_dict
            "standard_epoch_dict" : returned_standard_epoch_dict,
            "mid_epoch_dict" : returned_mid_epoch_dict,
            "quality_dict" : return_quality_dict
        }
        '''
        # check overall structure of data is a dict as required
        assert isinstance(data, dict)
        assert len(data) == 5
        for k in ["observations_list_of_dicts", "rwo_dict", "standard_epoch_dict","mid_epoch_dict","quality_dict"]:
            assert k in data
        
        # check components of the dict
        assert isinstance(data["observations_list_of_dicts"], (tuple, list))
        for d in data["observations_list_of_dicts"]:
            assert isinstance(d, dict)
        for k in ["rwo_dict", "standard_epoch_dict","mid_epoch_dict","quality_dict"]:
            assert isinstance(data[k] , dict)
            
        # return componenets separated-out
        return  data["observations_list_of_dicts"], \
                data["rwo_dict"], \
                data["standard_epoch_dict"], \
                data["mid_epoch_dict"], \
                data["quality_dict"]



class OrbfitServer(Server, Orbfit):
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
        
        Note this assumes that the supplied data from the client will be in the form of:
        a *pickled* set of data containing...
        
        (1) observations_list_of_dicts : list of dictionaries
        - all observations for a single object that is to be fitted
        - one dictionary per observation
        - each dictionary to contain ades fields from obs table in db
        
        (2) previous_rwo_dict : dictionary
        - contents of rwo_json field
        - will have been returned from previous orbit fit
        
        (3) previous_standard_epoch_dict : dictionary
        - contents of standard_epoch_json field
        - will have been returned from previous orbit fit


        '''
        while True:
            try:
                data        = self.recv_msg(client)
                if data:
                    print(f"data received in _listenToClient, within OrbfitServer : data-size = {sys.getsizeof(data)} bytes")
                    
                    # Check data format
                    data_object             = pickle.loads(data)
                    observations_list_of_dicts,previous_rwo_dict,previous_mid_epoch_dict = self._check_data_format_from_client(data_object)
                    
                    # Do orbit fit [NOT YET IMPLEMENTED]
                    returned_observations_list_of_dicts, returned_rwo_dict, returned_mid_epoch_dict,returned_standard_epoch_dict, return_quality_dict = self.fitting_function( )
                    
                    # Reformat the results for transmission
                    data_dict = {
                        "observations_list_of_dicts": returned_observations_list_of_dicts,
                        "rwo_dict" : returned_rwo_dict,
                        "mid_epoch_dict" : returned_mid_epoch_dict,
                        "standard_epoch_dict" : returned_standard_epoch_dict,
                        "quality_dict" : return_quality_dict
                        }
                    data_string = pickle.dumps(data_dict)
                    
                    # Send the results back to the client
                    self.send_msg(client, data_string)
                    
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False
                


    def fitting_function(self, ):
        ''' Do orbit fit [NOT YET IMPLEMENTED] '''
        # The returned quantities are expected to be ...
        # returned_observations_list_of_dicts, returned_rwo_dict, returned_mid_epoch_dict,returned_standard_epoch_dict, return_quality_dict
        return [{}],{},{},{},{}
        
"""
class DemoOrbfitServer(Server):
    '''
    Set up a server SPECIFIC to ORBIT-FITTING
    This is just a demo version that reflects back what it received
    This is *NOT* what you want to use in production
    Thi is JUST FOR TESTING !!!
    '''

    def __init__(self, host=None, port=None):
        Server.__init__(self,)


    def _demo_listen(self, startup_func = False ):
        '''
        Demo function to illustrate how to set-up server
        and to allow tests of various functionalities
        '''
    
        # Allow for doing a lengthy job on start-up
        # E.g. loading a big ephemeris file
        if startup_func:
            self._a_function_that_takes_a_few_seconds_to_evaluate(i=5)
            
        # listen() enables a server to accept() connections
        # NB "5" is the max number of connection requests to queue-up
        self.sock.listen(5)
        print('\nI are listen')
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
            threading.Thread(target = self._demoListenToClient,
                             args = (client,address)).start()

    def _demoListenToClient(self, client, address):
        '''
        Demonstration of a func that will...
        (i) receive a message from a client
        (ii) add "received" to every dictionary in the message
        (iii) send the data back to the client
        
        Note that this demo assumes that supplied data from the client will be in the form of:
        a *pickled* list-of-dictionaries
        
        '''
        while True:
            try:
                data        = self.recv_msg(client)
                if data:
                    # Demo function just adds "received" key to dict
                    # Instead of this one could do some useful work:
                    # E.g. call cheby_checker
                    data_string = self._add_received_to_data_in_list_of_dictionaries(data)
                    
                    # Set the response to echo back the data
                    # but with the addition of a received key
                    self.send_msg(client, data_string)
                    
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False
                
    def _add_received_to_data_in_list_of_dictionaries(self, data):
        '''
        Demo function.
        Assumes that the supplied data is a list-of-dictionaries
        Adds "received" to each dictionary
        Sends the updated list-of-dictionaries back
        '''
        
        # unpickle ...
        data_object             = pickle.loads(data)
        
        # Here I assume that the unpickled data is a *LIST OF DICTIONARIES*
        for d in data_object:
            d["received"] = True
            
        # re-pickle ...
        return                  pickle.dumps(data_object)
        
    def _a_function_that_takes_a_few_seconds_to_evaluate(self, i=1):
        '''
        Creates a 1e4 x 1e4 = 1e8-element array
        Takes a few seconds to do so
        There's no real point to this function:
         - I just want something numerically challenging for the machine to be doing
        '''
        print("\nDoing a lengthy calculation")
        for _ in range(i):
            n           = int(1e4)
            expected    = (n,n)
            actual      = np.random.random_sample((n,n)).shape
        return True
"""

class OrbfitClient(Client, Orbfit):
    '''
    Client specific to ORBIT-FITTING
    
    Expected usage:
    ----------------
    # Instantiate
    OC = sc.OrbfitClient()
    # Use to gett orbit-fit
    observations, rwo_dict, standard_epoch_dict, quality_dict = OC.request_orbit_extension(\
        observations_list_of_dicts,
        previous_rwo_dict,
        previous_standard_epoch_dict)

    '''

    def __init__(self, host=None, port=None):
        Client.__init__(self,)
        Orbfit.__init__(self,)

    def request_orbit_extension(  self,
                                  observations_list_of_dicts,
                                  previous_rwo_dict,
                                  previous_mid_epoch_dict):
        '''
        Request an orbit extension/refit for a previously known orbit
        
        inputs
        -------
        observations_list_of_dicts : list of dictionaries
        - all observations for a single object that is to be fitted
        - one dictionary per observation
        - each dictionary to contain ades fields from obs table in db
        
        previous_rwo_dict : dictionary
        - contents of rwo_json field
        - will have been returned from previous orbit fit
        
        previous_mid_epoch_dict : dictionary
        - contents of mid_epoch_json field
        - will have been returned from previous orbit fit

        returns
        -------
        
        '''
        message_dict = {
            "observations_list_of_dicts": observations_list_of_dicts,
            "rwo_dict" : previous_rwo_dict,
            "mid_epoch_dict" : previous_mid_epoch_dict
        }

        # Do checks on the input format
        self._check_data_format_from_client(message_dict)
        
        # Send data via *_pickleclient* function
        result = self._pickleclient(message_dict, VERBOSE = True )

        # check the returned data is as expected & return ...
        '''
        _check_data_format_from_server()
        ...
        return  data["observations_list_of_dicts"], \
                data["rwo_dict"], \
                data["standard_epoch_dict"], \
                data["mid_epoch_dict"], \
                data["quality_dict"]
        '''
        return self._check_data_format_from_server(result)
    
    def _demo_orbfit_via_pickle(self,):
        '''
        A demonstration of the *_pickleclient* function
        Passes a list of dictionaries
        '''
        message_data = [{'msg' : 'Hello World!' }]
        return self._pickleclient(message_data, VERBOSE = True )
        

if __name__ == "__main__":
    OS = OrbfitServer()
    print(f"Launched socket server: OS.host={OS.host}, OS.port={OS.port}")
    OS._listen( startup_func = True )
