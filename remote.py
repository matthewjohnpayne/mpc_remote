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


# Interface for a remote-machine to request an orbit-fit
# --------------------------------------------------------------
class RemoteOrbitFit(sc.OrbfitServer):
    '''
    Interface for a remote-machine to request an orbit-fit
    from a dedicated orbit-fitting server

    Expected usage:
    ----------------
    R = remote.RemoteOrbitFitClient()
    R.request_orbit_extension_json(supplied_json)

    '''

    def __init__(self, host=None, port=None):
        sc.OrbfitServer.__init__(self,)

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

        # Do checks on the input format
        self._check_json_from_client(input_json_string)
                
        # Request orbit-fit via API
        try:
            url = "http://131.142.195.56/cgi-bin/cgipy/orbfit.cgi"
            r = requests.get(url, params=input_json_string )
        except Exception as e:
            print("e=", e)
            r = {}
        else:
            print(f"r={r}")
            print(f"type(r)={type(r)}")
            json_result = json.loads(r)
            print(f"json_result={json_result}")

        # check the returned data is as expected & return ...
        self._check_json_from_server(json_result)
        return json_result
        
            
