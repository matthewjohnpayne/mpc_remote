# MJP: 20210223
# Working towards a docker-image for "Checker/Ephemeris" code
# Based on training sample (https://github.com/ssneo/docker_training) from T.Linder



# Get ubuntu image. No reason to choose this other than that's what T.Linder was using
FROM ubuntu:18.04

# That's my name 
MAINTAINER Matthew Payne 

# Do some basic installs 
RUN apt-get update
RUN apt-get install -y vim
RUN apt-get update
RUN apt-get install -y git
RUN apt-get update
RUN apt-get install -y python3.8
RUN apt-get update
RUN apt-get install -y python3-pip 
RUN python3.8 -m pip install numpy

# Set up aliases 
RUN echo 'alias python="/usr/bin/python3.8"' >> /root/.bashrc
RUN echo 'alias pip="/usr/bin/pip3"' >> /root/.bashrc

# One can make directories ...
#RUN mkdir dap
#RUN mkdir dap_data

# Expose port 40001 in the container
EXPOSE 40001

# Clone mpc_remote from GitHub 
RUN git clone https://github.com/matthewjohnpayne/mpc_remote.git

# This is copying an external file (local compile dir only?) to internally (within the image)
#COPY pythonServer.py /pythonServer.py

# change permission of file
#RUN ["chmod", "+x", "/mpc_remote/pythonServer.py"]

# run command that executes a python script 
# - This python script just does a 	permanent loop, hence forcing the container to stay open/deployed/whatever 
#ENTRYPOINT ["python3.8", "/pythonServer.py"]


# Run socket-server on entry: this causes a constantly listening loop 
ENTRYPOINT ["python3.8", "/mpc_remote/deploy_server.py", "T"]

