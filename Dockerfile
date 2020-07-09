FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim
RUN apt-get install -y less
RUN apt-get install -y curl
RUN apt-get install -y libhdf5-dev
RUN apt-get install -y screen

ARG DIR_MONETA=/home/jovyan/work/moneta
ARG DIR_MONETA_FILES=/home/jovyan/work/moneta_files
ARG DIR_PINTOOL_FILES=${DIR_MONETA_FILES}/pintool_files
ARG DIR_SETUP=${DIR_MONETA_FILES}/setup

WORKDIR /

# Install pintool and COPY to PATH
ADD moneta_files/pintool_files/moneta_pintool.tar.gz /

ENV PIN_ROOT=/pintool

# Fix PIN compilation: https://chunkaichang.com/tool/pin-notes/
COPY moneta_files/pintool_files/pin_makefile.unix.config ${PIN_ROOT}/source/tools/Config/makefile.unix.config
# Use HDF5 library with Pintool
COPY moneta_files/pintool_files/pin_makefile.default.rules ${PIN_ROOT}/source/tools/Config/makefile.default.rules


# Install python libraries
COPY moneta_files/setup/requirements.txt ${DIR_SETUP}/
WORKDIR ${DIR_SETUP}
RUN pip install -r requirements.txt

# Create aliases for Pin and Moneta
COPY moneta_files/setup/bashrc_aliases ${DIR_SETUP}/
RUN sed -i 's/\r$//' bashrc_aliases
RUN cat bashrc_aliases >> ~/.bashrc

WORKDIR ${DIR_MONETA}

