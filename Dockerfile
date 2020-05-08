FROM jupyter/scipy-notebook:dc9744740e12

USER root
RUN apt-get update -y
RUN apt-get install -y vim
RUN apt-get install -y libhdf5-dev

WORKDIR /setup

# Install pintool and add to PATH
RUN wget -q https://software.intel.com/sites/landingpage/pintool/downloads/pin-2.14-71313-gcc.4.4.7-linux.tar.gz -O pintool.tar.gz
RUN tar -xzf pintool.tar.gz
RUN echo "This may take a while..." && mv pin-2.14-71313-gcc.4.4.7-linux pintool
RUN rm pintool.tar.gz


# Make directories for pintool executable and outfiles
RUN mkdir /setup/converter
RUN mkdir /setup/converter/outfiles
ADD Setup/trace_tool.so /setup/converter


ENV PIN_ROOT=/setup/pintool
RUN echo "alias pin='/setup/pintool/pin.sh -ifeellucky -injection child'" >> ~/.bashrc

# Fix PIN compilation: https://chunkaichang.com/tool/pin-notes/
ADD Setup/pin_makefile.unix.config /setup/pintool/source/tools/Config/makefile.unix.config
# Use HDF5 library with PINtool
ADD Setup/pin_makefile.default.rules /setup/pintool/source/tools/Config/makefile.default.rules

# Install python libraries
ADD requirements.txt /setup
RUN pip install -r requirements.txt

WORKDIR /home/jovyan/work/memorytrace
