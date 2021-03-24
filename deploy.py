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

if len(sys.argv) >= 2 and sys.argv[1] in ["W","C"]:

    # This is for the web-server (e.g. mpcweb1) ...
    # ... it needs to have some simple cgi script available ...
    # ... and also I can't get the python scripts to play nice with the cgi-script unless I COPY them into the cgi-directory
    if sys.argv[1] == "W" :
        print("Deploying code on web-server: This is currently a primitive copy-to-directory script ...")
        for script in [ "remote_test.cgi",
                        "remote_orbfit.cgi",
                        "remote_iod.cgi",
                        "remote_comet.cgi",
                        "remote_checker.cgi",
                        "remote_general.py",
                        "sockets_class.py",
                        "sample_data.py"]:
            # copy the script over
            command = "sudo cp %s /var/www/cgi-bin/cgipy" % script
            print("\t", command)
            os.system(command)
            
            # ensure the permissions are correct
            command = "sudo chmod 777 /var/www/cgi-bin/cgipy/%s " % script
            print("\t", command)
            os.system(command)


    # This is for the compute cluster (e.g. marsden / container)...
    # ... this needs to have a socket-server to receive incoming requests ...
    elif sys.argv[1] == "C":
        import sockets_class as sc
        
        # Launch a test server ...
        if sys.argv[2] == "T":
            TS = sc.Server()
                            
        # Launch an orbfit orbit-extension server ...
        elif sys.argv[2] == "E":
            TS = sc.OrbfitExtensionServer()

        # Launch an orbfit IOD server ...
        elif sys.argv[2] == "I":
            TS = sc.OrbfitIODServer()

        # don't know what's wanted
        else:
            print(f"should not be able to see this error: sys.argv[2]={sys.argv[2]}")

        # Tell the server to start listening
        print(f"Launched socket server: TS.host={TS.host}, TS.port={TS.port}")
        TS._listen()
                            
    else:
        print(f"should not be able to see this error: sys.argv[1]={sys.argv[1]}")

else:
    print("input args not recognized ...", sys.argv)
