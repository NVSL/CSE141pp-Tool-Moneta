#
# Copyright (C) 2004-2013 Intel Corporation.
# SPDX-License-Identifier: MIT
#

default: trace2hdf5 make-tool
.PHONY: make-tool
make-tool:
	mkdir -p obj-intel64
	$(MAKE) obj-intel64/trace_tool.so

trace2hdf5: trace2hdf5.cpp moneta_trace.hpp
	g++ -c -Wall -Werror -I/usr/include/hdf5/serial  -Werror trace2hdf5.cpp -o  trace2hdf5.o
	g++ trace2hdf5.o -L/usr/lib/x86_64-linux-gnu/hdf5/serial  -lhdf5 -lhdf5_cpp -o  $@

clean: my-clean

.PHONY: my-clean
my-clean:
	rm -rf trace2hdf5 trace2hdf5.o obj-intel64/*

##############################################################
#
#                   DO NOT EDIT THIS AREA!
#
##############################################################

# If the tool is built out of the kit, PIN_ROOT must be specified in the make invocation and point to the kit root.
ifdef PIN_ROOT
CONFIG_ROOT := $(PIN_ROOT)/source/tools/Config
else
CONFIG_ROOT := ../Config
endif
include $(CONFIG_ROOT)/makefile.config
include makefile.rules
include $(TOOLS_ROOT)/Config/makefile.default.rules

##############################################################
#
#                   DO NOT EDIT THIS AREA!
#
##############################################################
