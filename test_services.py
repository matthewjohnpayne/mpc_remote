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


    
# Low level tests of connectivity
# ---------------------------------------------------------------

def test_basic_client():
    '''
    Need to have the socket-server running on the target compute machine (e.g. Marsden)
    This test to be run from externally accessible entry point (e.g. MPCWEB1)
    '''
    print("test_client...")

    C = sc.Client()
    
    # Loop over sample input data ...
    for n, sample_dict in enumerate( [  sample_data.sample_test_dict() ]):
        
        # check that this sample_dict is actually correctly formatted
        sc.Testing()._check_data_format_from_client(sample_dict)

        # send to server and get response
        response = C.connect(sample_dict)
    
        # check that the response is as expected
        sc.Testing()._check_data_format_from_server(response)

    
    print("test_client...SUCCESS")


def test_basic_remote():
    '''
    Need to have the socket-server running on the compute machine (e.g. Marsden)
    Need to have some API access point available (e.g. on MPCWEB1)
    This test to be run from some third, remote machine (e.g. Laptop)
    '''
        
    # Loop over sample input data ...
    for n, sample_json in enumerate( [  sample_data.sample_test_json_string() ]):

        # use the *request_orbit_extension* function to get an orbit-fit/extension done
        # - the intent is that this is on a remote machine, but it can be anywhere for this test
        json_result = remote.Remote().request_test_json(sample_json)

        # check that the response is as expected
        sc.Testing()._check_data_format_from_server(json_result)
        print(f"test_basic_remote: json_result = {json_result}")


# Some tests of orbit-extension functionality
# ---------------------------------------------------------------
    
def test_orbfit_extension_server():
    '''
    Test call to the orbit-fitting function
    (direct from the cluster server machine itself, e.g. marsden)
    '''
    
    # Get sample data
    sample_dict = sample_data.sample_orbfit_extension_input_dict()
    
    # Call MPan's  /sa/orbit_pipeline/update_existing_orbits.py function
    sys.path.append("/sa/orbit_pipeline")
    import update_existing_orbits as update
    outputdict = update.update_existing_orbits(sample_dict)
    
    #
    print(f'outputdict:\n{outputdict.keys()}')
    
def test_orbfit_extension_client():
    pass 

def test_orbfit_extension_remote():
    pass


"""
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

"""
