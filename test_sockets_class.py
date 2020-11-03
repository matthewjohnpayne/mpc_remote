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


# Some tests of *general* sockets methods
# - These do *NOT* test MJP's MPC-specific socker server/client
# - See secn below for tests of MPC-specific socker server/client
# ---------------------------------------------------------------
def run_fake_server(HOST = '127.0.0.1', PORT = 65432):
    # Run a server to listen for a connection and then close it
    # NB Don't run as-is : put in a thread, or something, to background-it
    server_sock = socket.socket()
    server_sock.bind((HOST,PORT))
    server_sock.listen(0)
    server_sock.accept()
    server_sock.close()
    assert True
    
def run_fake_client(HOST = '127.0.0.1', PORT = 65432):
    # This is our fake test client that is just going to attempt to connect and disconnect
    fake_client = socket.socket()
    fake_client.settimeout(1)
    fake_client.connect((HOST,PORT))
    fake_client.close()
    
def test_threading_server_and_client(HOST = '127.0.0.1', PORT = 65431):
    ''' Adapted from https://www.devdungeon.com/content/unit-testing-tcp-server-client-python '''

    # Start fake server in (background?) thread
    server_thread = threading.Thread(target=run_fake_server, args=(HOST,PORT))
    server_thread.start()

    # Test the clients basic connection and disconnection
    # *** If the above server is not running, then this will not connect ***
    run_fake_client(HOST=HOST, PORT=PORT)

    # Ensure server thread ends
    server_thread.join()
    
    

# Some tests of MPC-specific socker server/client
# ---------------------------------------------------------------

def test_demo_orbfit_via_pickle():
    '''
    This tests the "Client" class written by MJP for MPC
    This tests requires that there be a server up-and-running
    
    It is likely that I could automate launch as part of the test process.
    But I haven't worked out how to do that yet.
     - https://realpython.com/testing-third-party-apis-with-mock-servers/)
    
    For now, the simplest way to get a demo server running is to execute the following python command
    >>>python3
    >>>import sockets_class as sc
    >>>sc.launch_socket_server()

    Then the pytests can be run.
    Try to remember to kill the server afterwards ... "
    '''
    
    # launch client
    OC = sc.OrbfitClient()

    # Send default "Hello World" message
    # & collect returned signal from server
    try:
        received = OC._demo_orbfit_via_pickle()
    except Exception as e:
        print(e)

        MJPs_ERR_MSG = "\n".join( ["Exception occured in *test_demo_client_server_connect* ",
        "This is likely to be caused if/when a server is NOT RUNNING.",
        "A server needs to be launched BEFORE running these tests of the client.",
        "",
        "If you expected to be able to connect to a remote server, then either it is not up...",
        "... or the connection attempt failed for some reason",
        "",
        "If you just wanted to connect to a local server instance of your own as part of testing...",
        "...then you should check that such a server has been launched.",
        "It is likely that I could automate launch as part of the test process.",
        "But I haven't worked out how to do that yet."
        " (https://realpython.com/testing-third-party-apis-with-mock-servers/) "
        "",
        "For now, the simplest way to get a demo server running is to execute the following python command",
        ">>>python3",
        ">>>import sockets_class as sc",
        ">>>sc.launch_socket_server()",
        "",
        "Then the pytests can be run.",
        "Try to remember to kill the server afterwards ... "
        ] )
        
        # Force end
        assert False, MJPs_ERR_MSG
        
    # Check content of demo message
    # is as expected (hard-coded demo content)
    # NB:
    # - This test assumes that the server that is listening is going to implement
    #   _demoListenToClient & _add_received_to_data_in_iterable_of_dictionaries
    # - This does what it says on the tin
    # - So we need to test to see whether "received" is in the dictionary
    assert isinstance(received, list)
    for d in received:
        assert isinstance(d, dict)
        assert "msg" in d
        assert d["msg"] == 'Hello World!'
        assert "received" in d
        assert d["received"] == True


def test_demo_big_message_exchange_via_pickleclient():
    '''
    This tests the "OrbfitClient" class written by MJP for MPC
    In particular it tests the *_pickleclient* method inherited from Client

    This tests requires that there be a server up-and-running
     - We are implicitly testing the "OrbfitServer" which is assumed to be listening,
    and assumed to be running _demoListenToClient & _add_received_to_data_in_list_of_dictionaries
    on any data it receives
    '''
    
    # launch client
    OC = sc.OrbfitClient()
    
    # Send large message
    # & collect returned signal from server
    n = int(3e3)
    D = { "np" : np.random.random_sample( (n,n) ) }
    
    # Create some different data structures to send ...
    # NB:
    # - This test assumes that the server that is listening is going to implement
    #   _demoListenToClient & _add_received_to_data_in_list_of_dictionaries
    # - Hence in this demo / test we need to supply a list of dictionaries
    message_data_sets = (
        [D],            # List-of-dicts
        [D,D],          # List-of-Dicts
        )
    for message_data in message_data_sets:
    
        # Send-and-receive data using the *_pickleclient* method
        received = OC._pickleclient( message_data , VERBOSE=False)
        
        # Will run these tests on any dictionary received back ...
        def dict_asserts(d):
            assert isinstance(d, dict)
            assert "received" in d
            assert d["received"] == True
            assert "np" in d
            assert isinstance( d["np"], np.ndarray )
            assert d["np"].shape == (n,n)

        # check that all is as expected
        # - run various tests
        assert isinstance(received, type(message_data))
        if isinstance(received,dict):
            dict_asserts(received)
        elif isinstance(received, (list,dict) ):
            for d in received:
                dict_asserts(d)
        else:
            assert False, "Should not get here ..."


