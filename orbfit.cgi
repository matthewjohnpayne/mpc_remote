#!/usr/bin/env python3

import sys
import cgi
import sockets_class as sc 
import json 

# Need this before any print statements ...
print("Content-Type: text/plain\n")

# This gets the contents as supplied to the url by the requesting service/server
input = sys.stdin

# If there is input, then pass it on to the OrbFit client to get a fit done by the server
if input:
  # Instantiate client  
  #OC               = sc.Client()

  # Call client-connect func with a dict 
  #orbit_fit_result = OC.connect(json.loads(input))
 
  try:
    d = {'x':'yz' , 't': [i for i in range( int(1e1) )]}
    assert False 
  except Exception as e :
    d = {'exception':f'{e}' , 'file':'orbfit.cgi' }

  # This should cause the result to be returned to the submitter ...
  print( json.dumps( d ) )
