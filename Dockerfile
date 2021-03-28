FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim less curl libhdf5-dev screen

ARG DIR_MONETA=/home/jovyan/work/moneta
ARG DIR_SETUP=/home/jovyan/work/setup
ARG DIR_PKG=/home/jovyan/work/moneta/packages

WORKDIR /

# Install pintool
# Fix PIN compilation (included in repo): https://chunkaichang.com/tool/pin-notes/
RUN git clone https://github.com/NVSL/CSE141pp-Tool-Moneta-Pin.git pin
ENV PIN_ROOT=/pin

# Install python libraries
COPY setup/requirements.txt ${DIR_SETUP}/
WORKDIR ${DIR_SETUP}
RUN pip install -r requirements.txt

# Create aliases for Pin and Moneta
COPY setup/bashrc_aliases ${DIR_SETUP}/

# Fix Windows to Linux file endings
RUN sed -i 's/\r$//' bashrc_aliases 
RUN cat bashrc_aliases >> ~/.bashrc

RUN echo ".container{width: 90%;}" >> /opt/conda/lib/python3.7/site-packages/notebook/static/custom/custom.css

COPY setup/compile_pin.py ${DIR_SETUP}/
COPY setup/trace_tool.cpp ${DIR_SETUP}/
RUN python compile_pin.py

# Make Moneta a package to add path for pytest to locate
COPY moneta/setup.py ${DIR_PKG}/
WORKDIR ${DIR_PKG}
RUN pip install -e .

WORKDIR ${DIR_MONETA}
