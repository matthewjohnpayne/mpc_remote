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

    default_server_host = '131.142.192.107' # ''# '127.0.0.1' # '131.142.195.56' == mpcweb1(CDP)  # '131.142.192.107'=='mpcdb1'
    default_server_port = 54321
    default_timeout = 111

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
        if VERBOSE:
            print("message_data to-be-sent \t\t...",message_data)
        pickled = pickle.dumps(message_data)
            
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

class OrbfitServer(Server):
    '''
    Set up a server SPECIFIC to ORBIT-FITTING
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


class OrbfitClient(Client):
    '''
    Client specific to ORBIT-FITTING
    '''

    def __init__(self, host=None, port=None):
        Client.__init__(self,)
    
    def _demo_orbfit_via_pickle(self,):
        '''
        A demonstration of the *_pickleclient* function
        Passes a list of dictionaries
        '''
        message_data = [{'msg' : 'Hello World!' }]
        return self._pickleclient(message_data, VERBOSE = True )
        

if __name__ == "__main__":
    Server().listen(startup_func = True )
