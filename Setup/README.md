# Setup

**Summary**: All the files used by the DockerFile to set up image

### pin_macros.h
Header file defining the functions users call to tag their program.

### pin_makefile.default.rules
Line 170 is changed from default to include the C++ library for Hdf5.

>TOOL_LIBS += -lhdf5 -lhdf5_cpp

Copied from main README: 
#### Using a custom library with PIN
Libraries can be added in `makefile.default.rules` lines 168-170.

By default it looks like this:
```
TOOL_CXXFLAGS += -I/usr/include/hdf5/serial
TOOL_LPATHS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial
TOOL_LIBS += -lhdf5
```

As an example, we can make our own hdf5_pin library and link it with the pintool by doing the following:

##### Compiling hdf5_pin.cpp to libhdf5_pin.so
```
g++ -c -L/usr/lib/x86_64-linux-gnu/hdf5/serial -I/usr/include/hdf5/serial hdf5_pin.cpp -lhdf5 -o hdf5_pin.o -fPIC -O3
g++ -shared hdf5_pin.o -o libhdf5_pin.so -L/usr/lib/x86_64-linux-gnu/hdf5/serial -I/usr/include/hdf5/serial -lhdf5 -Wl,--hash-style=both -O3
```
##### Adding libhdf5_pin to the makefile rules
Assume that we have `hdf5_pin.h` located in `/folder1`, and `libhdf5_pin.so` which is located in `/folder2`.

Change the makefile config, lines 168-170 to the following:
```
TOOL_CXXFLAGS += -I/usr/include/hdf5/serial -I/folder1
TOOL_LPATHS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial -L/folder2
TOOL_LIBS += -lhdf5 -lhdf5_pin
```
Add `libhdf5_pin.so` to the LD_LIBRARY_PATH:
```
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/folder2
```
Now we can use the library in a pintool:
```
#include "hdf5_pin.h"
```

### pin_makefile.unix.config
We use Pin 2.14. To use hdf5 in the pintool, the file specifies the change based on this article:
> https://chunkaichang.com/tool/pin-notes/

### requirements.txt
A list of library requirements to be downloaded by docker upon creation of the image.

### trace_tool.cpp
The main pintool called by ~/work/memorytrace/main.py to generate the data for the trace.

### trace_tool.so
Compiled version of pintool to be moved to appropriate directory upon creation of image.

### vaex_extended_setup/
Directory contains changes to vanilla vaex.  
vaex_extended is used to plot the traces and format widgets/controls on that plot.
