# CSE142/L MemoryTrace

See https://github.com/NVSL/CSE141pp-Explorer/blob/master/README.md
 for original tutorials.

## Getting Started

First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Tool-MemoryTrace

cd CSE141pp-Tool-MemoryTrace
```

Build the Docker image and name it "memorytrace".
```
docker build -t memorytrace .
```

Start a detached docker container named "memtrace".
```
docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

**NOTE:** If you are running on Windows, run the following instead:
```
MSYS_NO_PATHCONV=1 docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

Connect to the container.
```
docker exec -it memtrace bash
```

# Usage

## JupyterLab
### ~~JupyterLab extension~~ Ignore this section, we are using Jupyter notebook.
First install the memorytrace extension.
```
cd ~/work/memorytrace
jupyter labextension install . --no-build
```
### Run JupyterLab
Start the Jupyter Lab in the work directory.
```
cd ~/work/
jupyter lab --allow-root --watch
```
Copy the last URL into the browser (change port as needed).

## Binary Instrumentation with PIN
The pintool folder is installed at `/setup/pintool`. Currently using PIN 2.14.

The Makefile config is at `/setup/pintool/source/tools/Config/makefile.default.rules`.

### Example
```
cd /setup/pintool/source/tools/ManualExamples

make obj-intel64/pinatrace.so TARGET=intel64

pin -t obj-intel64/pinatrace.so -- /bin/ls

head pinatrace.out
```

### Using a custom library with PIN
Libraries can be added in `makefile.default.rules` lines 168-170.

By default it looks like this:
```
TOOL_CXXFLAGS += -I/usr/include/hdf5/serial
TOOL_LPATHS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial
TOOL_LIBS += -lhdf5
```

As an example, we can make our own hdf5_pin library and link it with the pintool by doing the following:

#### Compiling hdf5_pin.cpp to libhdf5_pin.so
```
g++ -c -L/usr/lib/x86_64-linux-gnu/hdf5/serial -I/usr/include/hdf5/serial hdf5_pin.cpp -lhdf5 -o hdf5_pin.o -fPIC -O3
g++ -shared -o libhdf5_pin.so hdf5_pin.o -Wl,--hash-style=both -O3
```
#### Adding libhdf5_pin to the makefile rules
Assume that we have `hdf5_pin.h` located in `/folder1`, and `libhdf5_pin.so` which is located in `/folder2`.

Change the makefile config, lines 168-170 to the following:
```
TOOL_CXXFLAGS += -I/usr/include/hdf5/serial -I/folder1
TOOL_LPATHS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial -L/folder2
TOOL_LIBS += -lhdf5 -lhdf5_pin
```

Now we can use the library in a pintool:
```
#include "hdf5_pin.h"
```
