FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim
RUN apt-get install -y less
RUN apt-get install -y curl
RUN apt-get install -y libhdf5-dev

ARG DIR_MONETA=/home/jovyan/work/moneta
ARG DIR_MONETA_FILES=/home/jovyan/work/moneta_files
ARG DIR_PINTOOL_FILES=${DIR_MONETA_FILES}/pintool_files
ARG DIR_SETUP=${DIR_MONETA_FILES}/setup



WORKDIR ${DIR_PINTOOL_FILES}

# Install pintool and COPY to PATH
COPY moneta_files/pintool_files/moneta_pintool.tar.gz /home/jovyan/work/moneta_files/pintool_files
RUN tar -xzf moneta_pintool.tar.gz
RUN rm moneta_pintool.tar.gz

ENV PIN_ROOT=${DIR_PINTOOL_FILES}/pintool

# Fix PIN compilation: https://chunkaichang.com/tool/pin-notes/
COPY moneta_files/pintool_files/pin_makefile.unix.config ${PIN_ROOT}/source/tools/Config/makefile.unix.config
# Use HDF5 library with Pintool
COPY moneta_files/pintool_files/pin_makefile.default.rules ${PIN_ROOT}/source/tools/Config/makefile.default.rules


# Install python libraries
COPY moneta_files/setup/requirements.txt ${DIR_SETUP}/
WORKDIR ${DIR_SETUP}
RUN pip install -r requirements.txt

ENV MONETA_PORT=8888

# Create aliases for Pin and Moneta
COPY moneta_files/setup/bashrc_addons ${DIR_SETUP}/
RUN cat bashrc_addons >> ~/.bashrc

WORKDIR ${DIR_MONETA}

