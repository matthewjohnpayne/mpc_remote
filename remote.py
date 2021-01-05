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
import json
import zlib
import requests


# Import neighboring packages
# --------------------------------------------------------------
import sockets_class as sc
import sample_data

# Interface for a remote-machine to request an orbit-fit
# --------------------------------------------------------------
class Remote():
    '''
    Interface for a remote-machine to request an orbit-fit
    (in particular, the extension of the arc of a known orbit)
    from a dedicated orbit-fitting server

    Expected usage:
    ----------------
    R = remote.Remote().request_orbit_extension_json(supplied_json)

    '''

    def __init__(self, host=None, port=None):
        pass
        
    # ------- REMOTE TEST : ORBIT EXTENSION ---------------------------------
    def request_test_json(  self, input_json_string , VERBOSE = False):
        '''
        Test method ...
        
        inputs
        -------
        json_data : json
         - data package to contain all necessary data to specify orbit-fitting.

        returns
        -------
        
        '''
        # Request orbit-fit via API
        url             = "http://131.142.195.56/cgi-bin/cgipy/remote_test.cgi"
        METHOD_OBJECT   = sc.Testing()
        result_dict     = self._request(input_json_string , url, METHOD_OBJECT )
        return result_dict
        

    
    # ------- ORBIT FITTING (1) : ORBIT EXTENSION ---------------------------------
    def request_orbit_extension_json(  self, input_json_string , VERBOSE = False):
        '''
        Request an orbit extension/refit for a previously known orbit
        
        inputs
        -------
        json_data : json
         - data package to contain all necessary data to specify orbit-fitting.

        returns
        -------
        
        '''
                
        # Request orbit-fit via API
        url             = "http://131.142.195.56/cgi-bin/cgipy/remote_orbfit.cgi"
        METHOD_OBJECT   = sc.IOD()
        result_dict     = self._request(input_json_string , url, METHOD_OBJECT )
        return result_dict
        


    # ------- ORBIT FITTING (2) : INITIAL ORBIT DETERMINATION  --------------------
    def request_iod_json(  self, input_json_string , VERBOSE = False):
        '''
        Request initial orbit determination for a set of observations
        
        inputs
        -------
        json_data : json
         - data package to contain all necessary data to specify orbit-fitting.

        returns
        -------
        result_dict: dict
        
        '''
                
        # Request orbit-fit via API
        url             = "http://131.142.195.56/cgi-bin/cgipy/remote_iod.cgi"
        METHOD_OBJECT   = sc.Orbfit()
        result_dict     = self._request(input_json_string , url, METHOD_OBJECT )
        return result_dict
        


    # ------- COMMON METHOD(s) ------------------------------------
    def _request(   self,
                    input_json_string , # json-serialized input dictionary
                    url,                # url to which the data will be sent
                    METHOD_OBJECT,      # an object that contains "_check..." methods
                    VERBOSE = False,    # allow for verbose print-outs
                    CHECKS = False ):   # indicate whether format/content checking should be done
        '''
        Common method used to send data packet to the requested url,
        and then turn the received reply into a dictionary
        '''
        try:
            # If desired, do checks on the input format
            if CHECKS:
                METHOD_OBJECT._check_json_from_client(input_json_string)

            # Send request to the above URL
            print(f'input_json_string={input_json_string}')
            r = requests.put(url, data=input_json_string )
            
            # Decode the reply
            decoded_content = r._content.decode()
            
            # Turn the reply into a dictionary
            result_dict = json.loads(decoded_content)

            # If desired, check the returned data is as expected
            if CHECKS:
                METHOD_OBJECT._check_data_format_from_server(result_dict)

        except Exception as e:
            result_dict = {'exception': f'{e}', 'file':'remote.py', 'function':'_request'}

        return result_dict
