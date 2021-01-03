#!/usr/bin/env python3

#
# CGI script for routing remote requests for processing through to marsden
# Uses socket-server methods
#
# I am *DELIBERATELY* duplicating cgi scripts so that the remote.py
# module has (apparantly) different end-points on mpcweb2 to call
# There will be identical scripts named remote_*.cgi:
# E.g. remote_test.cgi, remote_iod.cgi, ...
#
# While this is all pretty primitive, I'm not sure whether there is much value in
# creating anything more sophisticated, given that we probably don't want
# to use this approach for very long ...

try:
  import sys
  import cgi
  import json 
  import remote_general as rg

  # Need this before any print statements ...
  print("Content-Type: text/plain\n")

  # This gets the contents as supplied to the url by the requesting service/server
  input = sys.stdin
  
  # If there is input, then pass it on to the client to get a fit done by the server
  if input:

    # The input is / can-be a TextIOWrapper : so need to read from it to get the contents ...
    input_str        = input.read()

    # If we have an input string of non-zero length, let's try to use it as input to an appropriate socket-server
    # The specific socket_server that will be called is all dealt with in "remote_general.py"
    if input_str:
        result_dict = rg.process_cgi_string(input_str, __file__)

except Exception as e :
  result_dict = {   'exception':f'{e}' ,
                    'file':'remote.cgi' }

# This should cause the result to be returned to the submitter ...
print( json.dumps( result_dict ) )
