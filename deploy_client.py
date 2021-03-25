'''
MJP : Dirt-simple script to help me deploy on machines ...

Usage:
$ python3 deploy_client.py
 - deploy on public-facing web-server, e.g. "mpcweb1"

'''

# Import third-party packages
# --------------------------------------------------------------
import sys, os

# Import neighboring packages
# --------------------------------------------------------------


# This is for the web-server (e.g. mpcweb1) ...
#  - Apache listens for incoming requests and then my "client" passes
#    the data onto a server that is listening on marsden/docker/...
#
# NB. It needs to have some simple cgi script available ...
# ... and also I can't get the python scripts to play nice with the cgi-script unless I COPY them into the cgi-directory
#
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

