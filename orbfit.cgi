#!/usr/bin/env python3

import sys
import cgi
import socket
import json


# Need this before any print statements ...
print("Content-Type: text/plain\n")

# This gets the contents as supplied to the url by the requesting service/server
input = sys.stdin

# If there is input, then pass it on to the OrbFit client to get a fit done by the server
if input:
  OC               = sockets_class.OrbfitClient()
  orbit_fit_result = OC.request_orbit_extension(input)

  # This should cause the result to be returned to the submitter ...
  print(orbit_fit_result)

