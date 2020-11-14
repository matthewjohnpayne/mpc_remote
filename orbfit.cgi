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
    input_str        = input.read()
    
    if input_str:  
      # Instantiate client
      OC               = sc.Client()

      # Call client-connect func with a dict
      input_str        = input.read()
      result_dict = OC.connect(json.loads(input_str))

    else:
      result_dict = {'exception':'Empty input...' , 'file':'orbfit.cgi'}

except Exception as e :
  result_dict = {'exception':f'{e}' , 'file':'orbfit.cgi' }

# This should cause the result to be returned to the submitter ...
print( json.dumps( result_dict ) )
