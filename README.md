# CSE142/L MemoryTrace

See https://github.com/NVSL/CSE141pp-Explorer/blob/master/README.md
 for original tutorials.

## Getting Started

First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Tool-MemoryTrace

cd CSE141pp-Tool-MemoryTrace
```

Build the Docker image and name it `memorytrace`.
```
docker build -t memorytrace .
```

<a name="port"></a>Start a detached docker container named `memtrace`. Take note of the `XXXX:8888` in the command. the `XXXX` will be your port number for running the notebook. The port number will be `8080` here but can be changed if there are any conflicts.
```
docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

**Windows:** Run the following instead:
```
MSYS_NO_PATHCONV=1 docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

Connect to the container.
```
docker exec -it memtrace bash
```

**Windows:** You may need add `winpty` if prompted:
```
winpty docker exec -it memtrace bash
```

# Program Tagging Usage
Copy these two lines below the `#include` statements at the top of your code file:
```
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START_TAG(const char* tag, int* begin, int* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP_TAG(const char* tag) {}
```
#### Parameters:
**tag:** A string name to identify the trace  
**begin:** The address of the first element of the data structure (Array Example: `&arr[0]`)  
**end:** The address of the last element of the data structure (Array Example: `&arr[arr.size()-1]`)  
  
Use `DUMP_ACCESS_START_TAG` and `DUMP_ACCESS_STOP_TAG` to identify the range you want to trace. Examples can be found in `memorytrace/Examples/src`.

# Memory Trace Tool Usage

You should be in the `memorytrace` directory. If not, `cd` to the directory
```
cd ~/work/memorytrace/
```
Run the notebook.  
**Note:** `vaex.plot_widget` only works for Jupyter notebook.
```
jupyter notebook --allow-root
```
You should see two links appear. Go to your preferred web browser and paste the second link. It should look something like this.  
**Note:** You will have to replace the `8888` with the [port you specified](#port) when setting up the Docker image. 
```
http://127.0.0.1:8888/?token=...
```
You should see a file called "LinkedSelectors.ipynb". Open the file, select the first cell and press `Shift+Enter`. You should see input boxes appear like below. Input your desired values and press `Run`.
![](https://i.gyazo.com/0537edfe66db0d05d5d7e013a8d95b56.png "Memory Trace Tool")
<br/>

**Cache Lines:** The number of lines in our fully-associative cache model (Default: 4096)  
**Lines to Output:** The maximum number of memory accesses to record. Larger numbers will take longer to run. (Default: 100,000,000)  
**Block Size:** The size of each cache line. (Default: 64 Bytes)  
**Executable Path:** Path to the executable to trace (Default: "./Examples/build/sorting")  

## For Devs Only

TODO

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
g++ -shared hdf5_pin.o -o libhdf5_pin.so -L/usr/lib/x86_64-linux-gnu/hdf5/serial -I/usr/include/hdf5/serial -lhdf5 -Wl,--hash-style=both -O3
```
#### Adding libhdf5_pin to the makefile rules
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
