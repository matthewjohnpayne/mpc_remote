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
import sample_data


    
# Some tests of ...
# ---------------------------------------------------------------

def test_client():
    '''
    
    Need to have the socket-server running on the target compute machine ...
    '''
    print("test_client...")

    C = sc.Client()
    
    # Loop over sample input data ...
    R = remote.RemoteOrbitFit()
    for n, json_string in enumerate( [  sample_data.sample_input_dict_empty(),
                                        sample_data.sample_input_dict()]):
        print(f"\n{n}: json_string={json_string}")

        # send to server and get response
        response = C.connect(json_string)
    
        # check ...
        sc.Orbfit()_check_data_format_from_client(response)

        print(f"\n{n}: response={response}")
    


def test_remote():
    '''
    Need to have the socket-server running on the compute machine ...
    Need to have some API access point available
    '''
    
    # launch client
    R = remote.RemoteOrbitFit()
    
    # Get sample input data
    json_string = sample_data.sample_input_json_string_empty()

    # use the *request_orbit_extension* function to get an orbit-fit/extension done
    # - the intent is that this is on a remote machine, but it can be anywhere for this test
    json_result = R.request_orbit_extension_json(json_string)
    
    # check ...
    O = sc.Orbfit()
    O._check_json_from_server(response)

    print(f"json_result={json_result}")


