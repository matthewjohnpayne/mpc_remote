# MJP: 2021-03-23
# This routine functions as a hack/quick way to execute the various 
# commands needs to create an image and fire-up a container of that image

import os

# commands to remove any extant running versions of the mpcremote image and/or container
os.system("docker stop mpcremotecontainer")
os.system("docker rm mpcremotecontainer")
os.system("docker image rm mpcremoteimage")

# build the image and name it "mpcremoteimage"
os.system("docker build . -t mpcremoteimage")

# allow access to local file-system: especially useful during development
# https://docs.docker.com/storage/bind-mounts/
# os.system("docker run -d -p 40001:40001 -v ~/Envs/mpc_remote:/mpc_remote --name mpcremotecontainer mpcremoteimage")

# run the image in a container and name the container as "mpcremotecontainer"
os.system("docker run -d --name mpcremotecontainer mpcremoteimage")

# execute interactively (so you get into the command-line)
os.system("docker exec -it mpcremotecontainer bash")


