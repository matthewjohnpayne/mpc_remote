#!/usr/bin/env python3

'''
# CGI script for routing remote requests for processing through to marsden
# Uses socket-server methods
#
# Does/will support ...
# (i) socket_testing
# (ii) orbit-fitting (orbit extension)
# (iii) initial orbit determination
# () ...
#
# While this is pretty primitive, I'm not sure whether there is much value in
# creating anything more sophisticated, given that we probably don't want
# to use this approach for very long ...
'''

# Third-party imports
# -------------------
import json
import os 

# Local imports
# -------------------
import sockets_class as sc

# Dict to map allowed calling script to ...
allowed_calling_scripts = {
    'remote_test.py'    : 'test' ,
    'remote_iod.py'     : 'iod' ,
    'remote_orbfit.py'  : 'orbfit' ,
}

def process_cgi_string(input_str, calling_file):
    
    try:
        # Get the filename from the filepath ...
        calling_file = os.path.split(calling_file)[1]
        
        # Convert the string to a dictionary
        input_dict = json.loads(input_str)
    
        # Depending on the content of the input, route to the appropriate destination
        assert calling_file in allowed_calling_scripts, f'{calling_file} not in allowed_calling_scripts'
        
        # wrapping the input dict in a higher dict to pass in the type of request being made
        request_type = allowed_calling_scripts[calling_file]
        request_dict = {request_type:input_dict}
        
        # instantiate
        C = sc.Client(port=destination_port)

        # Call client-connect func with the content from the input dict
        result_dict = C.connect(request_dict)
    
    except Exception as e :
        result_dict = { 'exception':f'{e}' , 'file':__file__, 'calling_file':calling_file}

    return result_dict
