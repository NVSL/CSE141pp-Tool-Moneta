FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim
RUN apt-get install -y less
RUN apt-get install -y curl
RUN apt-get install -y libhdf5-dev

ARG DIR_MONETA_TOOL /home/jovyan/work/moneta_tool
ARG DIR_MONETA_FILES /home/jovyan/work/moneta_files
ARG DIR_PINTOOL_FILES ${DIR_MONETA_FILES}/pintool_files
ARG DIR_SETUP ${DIR_MONETA_FILES}/setup

WORKDIR ${DIR_PINTOOL_FILES}

# Install pintool and add to PATH
RUN tar -xzf moneta_pintool.tar.gz
RUN rm moneta_pintool.tar.gz
RUN git update-index --assume-unchanged moneta_pintool.tar.gz

ENV PIN_ROOT=${DIR_PINTOOL_FILES}/pintool

# Fix PIN compilation: https://chunkaichang.com/tool/pin-notes/
ADD ${DIR_PINTOOL_FILES}/pin_makefile.unix.config ${PIN_ROOT}/source/tools/Config/makefile.unix.config
# Use HDF5 library with PINtool
ADD ${DIR_PINTOOL_FILES}/pin_makefile.default.rules ${PIN_ROOT}/source/tools/Config/makefile.default.rules

# Install python libraries
WORKDIR ${DIR_SETUP}
RUN pip install -r requirements.txt

# Create aliases for Pin and Moneta
RUN echo "alias pin=\"${PIN_ROOT}/pin.sh -ifeellucky -injection child\"" >> ~/.bashrc
RUN echo "alias moneta=\"jupyter notebook --allow-root ${DIR_MONETA_TOOL}\"" >> ~/.bashrc

WORKDIR ${DIR_MONETA_TOOL}
