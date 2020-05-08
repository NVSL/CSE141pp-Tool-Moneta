#!/bin/sh

mkdir /setup/converter
mkdir /setup/converter/outfiles
mkdir /setup/lib_pin_hdf5


cp ./converter/* /setup/converter/
cp ./lib_pin_hdf5/* /setup/lib_pin_hdf5/
cp makefile.default.rules /setup/pintool/source/tools/Config/
