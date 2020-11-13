# Import third-party packages
# --------------------------------------------------------------
import numpy as np
import sys, os
import pytest
import threading
import socket
import pickle
from datetime import datetime
import subprocess

# Import neighboring packages
# ---------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))))
import sockets_class as sc
import remote


    
# Some tests of ...
# ---------------------------------------------------------------

def test_client():
    '''
    
    Need to have the socket-server running on the target compute machine ...
    '''
    
    C = sc.Client()
    
    # Get sample input data
    R = remote.RemoteOrbitFit()
    json_string = R.sample_input_json_string_empty()
    print("json_string", json_string)
    # Compress the data, as that's what the orbit-server expects ..
    B = sc.Base()
    compressed = B.compress_json_string(json_string)
    
    # send to server and get response
    response = C.connect(compressed)
    
    # decompress (because the orbit-server is set-up to send compressed data)
    response = B.decompress_json_string(response)
    
    # check ...
    O = sc.Orbfit()
    O._check_json_from_server(response)

    print(f"response={response}")
    


def test_remote():
    '''
    Need to have the socket-server running on the compute machine ...
    Need to have some API access point available
    '''
    
    # launch client
    R = remote.RemoteOrbitFit()
    
    # Get sample input data
    R = remote.RemoteOrbitFit()
    json_string = R.sample_input_json_string_empty()

    # use the *request_orbit_extension* function to get an orbit-fit/extension done
    # - the intent is that this is on a remote machine, but it can be anywhere for this test
    json_result = R.request_orbit_extension_json(json_string)
    
    # check ...
    O = sc.Orbfit()
    O._check_json_from_server(response)

    print(f"json_result={json_result}")


