# CSE142/L MemoryTrace

See https://github.com/NVSL/CSE141pp-Explorer/blob/master/README.md
 for original tutorials.

## Getting Started

First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Tool-Moneta

cd CSE141pp-Tool-Moneta
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
Add `#include "/setup/pin_macros.h"` to the top of your code. Note that the include contains the full path to the header file. By default, the file is located in `/setup/pin_macros.h`. The following three functions will be used to tag your code:

```
void DUMP_ACCESS_START_TAG(const char* tag, void* begin, void* end)
void DUMP_ACCESS_STOP_TAG(const char* tag)
void FLUSH_CACHE()
```


#### Parameters:
**tag:** A string name to identify the trace  
**begin:** The address of the first element of the data structure (Vector Example: `&arr[0]`)  
**end:** The address of the last element of the data structure (Vector Example: `&arr[arr.size()-1]`)  
  
Use `DUMP_ACCESS_START_TAG` and `DUMP_ACCESS_STOP_TAG` to identify the range you want to trace. Use `FLUSH_CACHE` to flush the contents of the tool's simulated cache. Examples can be found in `memorytrace/Examples/src`.

# Memory Trace Tool Usage

The Dockerfile should, by default, put you in the `memorytrace` directory whenever you run the container. If not, `cd` to the directory
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
**Note:** If you are using Docker Toolbox as your docker environment, you will also have to replace 127.0.0.1 with 192.168.99.100 to access the link.
```
http://192.168.99.100:8888/?token=...
```

You should see a file called `MemoryTracer.ipynb`. This is the notebook that you will need to open.

# Generating a Trace

After opening `MemoryTracer.ipynb`, select the first cell and press `Shift+Enter`. 

You should see input boxes appear like below.
![](https://i.gyazo.com/03f415e4aa6f258b41a6d7c4fa62f3f3.png "Memory Trace Tool")
<br/>

**Cache Lines:** The number of lines in our fully-associative cache model (Default: 4096)  
**Block Size:** The size of each cache line. (Default: 64 Bytes)  
**Lines to Output:** The maximum number of memory accesses to record. Larger numbers will take longer to run. (Default: 100,000,000)  
**Executable Path:** Path to the executable to trace (Default: "./Examples/build/sorting")  
**Name for Output:** Name to save the trace as (Default: "Baseline")  
**Trace Everything:** Trace all memory accesses in the program  

Input your desired values and press `Generate Trace`. This will create a trace in the box using the name you specified. All files related to the trace can be found in the `/setup/converter/outfiles` directory.

If **Trace Everything** is enabled, the name of your trace can be found with parentheses surrounding it indicating that it's a full trace.

# Analyzing a Trace

From the box on the right, select your desired trace and press `Load Trace`.

If this is tagged trace and there are tags or it's full trace, a plot should display.

The plot plots all data points in the trace with time/index on the x-axis and memory address on the y-axis

The top menubar contains zooming controls. From left to right:  
x,y checkboxes - When enabled, allows panning and zooming in the corresponding directions (Both means normal zooming/panning)  
Pan & Zoom     - When selected, allows panning and zooming  
Zoom to Selection - When selected, zooms to window chosen by click and drag  
Square Selection  - When selected, only displays points in window chosen by click and drag  
Delete Selection  - When selected, display all points
Reset Zoom        - Move window back to original limits determined by all data in trace

Legend contains checkboxes to turn on/off corresponding points  
The frequency of each type of access is display near each point  

The green line on the left depicts the cache size - a product of cache lines * block size  

A list of checkboxes follow to turn on/off certain tags/data structures in the trace  
With zoom to selection buttons next to each to display the minimum window containing all accesses to said data structure  

TODO

# Deleting a Trace

From the box on the right, select the traces you want to delete. Note that you can select multiple traces by holding `Shift` or `Ctrl` while clicking. Clicking `Delete Trace` will permanently remove all files related to the selected traces.

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
