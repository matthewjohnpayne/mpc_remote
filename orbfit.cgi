#!/usr/bin/env python3

try:
  import sys
  import cgi
  import json 
  import sockets_class as sc

  # Need this before any print statements ...
  print("Content-Type: text/plain\n")

  # This gets the contents as supplied to the url by the requesting service/server
  input = sys.stdin
  
  # If there is input, then pass it on to the OrbFit client to get a fit done by the server
  if input:

    # The input is / can-be a TextIOWrapper : so need to read from it to get the contents ...
    input_str        = input.read()

    # If we have an input string of non-zero length, let's try to use it as input to an orbit-fit    
    if input_str:  

      # Instantiate client
      # - In the future, I could call with different ports to get the data directed to different servers 
      #   E.g. if I want to have a version of this cgiu script that sends to mpchecker instead/as-well as orbfit
      OC               = sc.Client()

      # Call client-connect func with a dict
      result_dict = OC.connect(json.loads(input_str))

    else:
      result_dict = {'exception':'Empty input...' , 'file':'orbfit.cgi'}

except Exception as e :
  result_dict = {'exception':f'{e}' , 'file':'orbfit.cgi' }

# This should cause the result to be returned to the submitter ...
print( json.dumps( result_dict ) )
