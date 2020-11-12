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


    
# Some tests of MPC-specific socker server/client
# These tests need to be pointed at a/the "OrbfitServer"
# - This can be launched with sockets_class.launch_orbit_fitting_socket_server()
# ---------------------------------------------------------------
def test_request_orbit_extension_json():
    '''
    This tests the "Client" class written by MJP for MPC
    This tests requires that there be a server up-and-running
    This can be launched with sockets_class.launch_orbit_fitting_socket_server()
    '''
    
    # launch client
    OC = sc.OrbfitClient()
    
    # Make test data
    input_json_string = OC.sample_input_json_string()
    
    # use the *request_orbit_extension* function to get an orbit-fit/extension done
    # - the intent is that this is on a remote machine, but it can be anywhere for this test
    result_json = OC.request_orbit_extension_json(input_json_string)
    
    # test format of returned result_json ...
    OC._check_json_from_server(result_json)
    
  
