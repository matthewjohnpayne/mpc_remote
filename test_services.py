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
    for n, sample_dict in enumerate( [  sample_data.sample_input_dict_empty(),
                                        sample_data.sample_input_dict()]):
        print()
        # send to server and get response
        response = C.connect(sample_dict)
    
        # check ...
        sc.Orbfit()._check_data_format_from_server(response)

        print(f"{n}: response={response}")
    
def test_cluster_orbitfit():
    '''
    Test call to the orbit-fitting function (direct from the cluster machine itself)
    '''
    
    # Get sample data
    sample_dict = sample_data.sample_input_dict()
    
    # Call MPan's  /sa/orbit_pipeline/update_existing_orbits.py function
    sys.path.append("/sa/orbit_pipeline")
    import update_existing_orbits as update
    outputdict = update.update_existing_orbits(sample_dict)
    
    

def test_remote():
    '''
    Need to have the socket-server running on the compute machine ...
    Need to have some API access point available
    '''
        
    # Loop over sample input data ...
    for n, sample_json in enumerate( [  sample_data.sample_input_json_string_empty(),
                                        sample_data.sample_input_json_string()]):

        # use the *request_orbit_extension* function to get an orbit-fit/extension done
        # - the intent is that this is on a remote machine, but it can be anywhere for this test
        json_result = remote.RemoteOrbitFit().request_orbit_extension_json(sample_json)

        # check ...
        #O = sc.Orbfit()._check_json_from_server(json_result)

        #print(f"json_result={json_result}")


