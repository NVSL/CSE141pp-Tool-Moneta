FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim
RUN apt-get install -y less
RUN apt-get install -y curl
RUN apt-get install -y libhdf5-dev
RUN apt-get install -y screen

ARG DIR_MONETA=/home/jovyan/work/moneta
ARG DIR_SETUP=/home/jovyan/work/setup

WORKDIR /

# Install pintool and COPY to PATH
# Fix PIN compilation (included in tar ball): https://chunkaichang.com/tool/pin-notes/
ADD setup/moneta_pintool.tar.gz /

ENV PIN_ROOT=/pin

# Install python libraries
COPY setup/requirements.txt ${DIR_SETUP}/
WORKDIR ${DIR_SETUP}
RUN pip install -r requirements.txt

# Create aliases for Pin and Moneta
COPY setup/bashrc_aliases ${DIR_SETUP}/

COPY moneta/setup.py ${DIR_MONETA}/

# Fix Windows to Linux file endings
RUN sed -i 's/\r$//' bashrc_aliases 
RUN cat bashrc_aliases >> ~/.bashrc

RUN echo ".container{width: 90%;}" >> /opt/conda/lib/python3.7/site-packages/notebook/static/custom/custom.css

COPY .setup/compile_pin.py ${DIR_SETUP}/
COPY .setup/trace_tool.cpp ${DIR_SETUP}/
RUN python compile_pin.py

WORKDIR ${DIR_MONETA}
# Make Moneta a package to add path for pytest to locate
RUN pip install -e .

