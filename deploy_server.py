'''
MJP : Dirt-simple script to help me deploy on machines ...

Usage:
$ python3 deploy_server.py W
 - deply on internal computation machine, e.g. "marsden" or "docker"s

'''

# Import third-party packages
# --------------------------------------------------------------
import sys, os

# Import neighboring packages
# --------------------------------------------------------------
import sockets_class as sc



# This is for the compute cluster (e.g. marsden / container)...
# ... this is creating a socket-server to listen for incoming requests ...

# Launch a test server ...
if sys.argv[1] == "T":
    TS = sc.Server()
                    
# Launch an orbfit orbit-extension server ...
elif sys.argv[1] == "E":
    TS = sc.OrbfitExtensionServer()

# Launch an orbfit IOD server ...
elif sys.argv[1] == "I":
    TS = sc.OrbfitIODServer()

# don't know what's wanted
else:
    print(f"should not be able to see this error: sys.argv[1]={sys.argv[1]}")

