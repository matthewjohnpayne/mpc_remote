'''
MJP : Dirt-simple script to help me deploy on machines ...

Usage:
$ python3 deploy.py W 
 - deploy on public-facing web-server, e.g. "mpcweb1"
$ python3 deploy.py M
 - deply on internal computation machine, e.g. "marsden" 

'''

import sys, os

if len(sys.argv) == 2 and sys.argv[1] in ["W","M"]:
  if sys.argv[1] == "W" : 
    print("Deploying code on web-server: This is currently a primitive script-copy")
    for script in ["orbfit.cgi"]:
      command = "cp %s /var/www/cgi-bin/cgipy" % script
      print("\t", command)
      os.system(command)
  elif sys.argv[1] == "M"
    OS = OrbfitServer()
    print(f"Launched socket server: OS.host={OS.host}, OS.port={OS.port}")
    OS._listen( startup_func = True )
else:
  print("input args not recognized ...", sys.argv)
