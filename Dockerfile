FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim

WORKDIR /setup

# Install pintool and add to PATH
RUN wget -q https://software.intel.com/sites/landingpage/pintool/downloads/pin-3.13-98189-g60a6ef199-gcc-linux.tar.gz -O pintool.tar.gz
RUN tar -xzf pintool.tar.gz
RUN mv pin-3.13-98189-g60a6ef199-gcc-linux pintool
RUN rm pintool.tar.gz
ENV PATH=$PATH:/setup/pintool

# Install python libraries
ADD requirements.txt /setup
RUN pip install -r requirements.txt

WORKDIR /
