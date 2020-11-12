'''
MJP : Dirt-simple script to help me deploy on machines ...

Usage:
$ python3 deploy.py W 
 - deploy on public-facing web-server, e.g. "mpcweb1"
$ python3 deploy.py M
 - deply on internal computation machine, e.g. "marsden" 

'''

# Import third-party packages
# --------------------------------------------------------------
import sys, os

# Import neighboring packages
# --------------------------------------------------------------
import sockets_class as sc

if len(sys.argv) == 2 and sys.argv[1] in ["W","M"]:

  # This is for the web-server ...
  # ... it needs to have some simple cgi script available ...
  if sys.argv[1] == "W" : 
    print("Deploying code on web-server: This is currently a primitive script-copy")
    for script in ["orbfit.cgi"]:
      command = "sudo cp %s /var/www/cgi-bin/cgipy" % script
      print("\t", command)
      os.system(command)

  # This is for the compute cluster ...
  # ... this needs to have a socket-server to receive incoming requests ...
  elif sys.argv[1] == "M":
    OS = sc.OrbfitServer()
    print(f"Launched socket server: OS.host={OS.host}, OS.port={OS.port}")
    OS._listen( startup_func = True )

  else:
    print("should not be able to see this error")

else:
  print("input args not recognized ...", sys.argv)
