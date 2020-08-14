# Using Moneta

Instructions on how to run and use Moneta

## Important Notes

Throughout this README, you will see Pin referenced a few times. Pin is the instrumentation tool that we used to read and interpret memory accesses at runtime. It runs in the background whenever you generate traces and produces the trace files for your program.

After connecting to the Docker container, you should be in the `~/work/moneta` directory. This is Moneta's base directory. When using Moneta, any relative paths you input into the text boxes will be relative to this directory.

A number of example programs are available under the `~work/moneta/Examples/src` directory. These programs were used by the developers to test Moneta's capabilities and have been left here to use as sample programs for exploring the tool. If you would like to use these programs, you will need to compile them first by running `make` in the `~/work/moneta` directory (or `make filename` without the `.cpp` to compile individual programs). Note that the Makefile compiles the programs with `-O0`. The resulting executables will be located in the `~/work/moneta/Examples/build` directory. 

**Know your port number.** The port number was set when you ran the Docker commands to build the container (see main `README`). If you do not remember your port number, open a new terminal and run `docker port moneta` (do **not** connect to the Moneta container). You will a result that looks like the following:
```
8888/tcp -> 0.0.0.0:####
```
The `####` is your port number. **You will need this to connect to the Jupyter Notebook.**


## Tagging Programs

`pin_tags.h` is the header file containing the functions to tag memory traces for your program. By default, it is located in the `~/work/moneta` directory, but you are free to copy this file to any directory that you find convenient. The functions in this file will indicate to Pin when it should start and stop writing memory accesses to file, and which memory address ranges it should trace.

To use `pin_tags.h` you will need to add `#include "PATH_TO_FILE/pin_tags.h"` (Default: `#include "/home/jovyan/work/moneta/pin_tags.h`) to the top of your C++ file. 

### Pin Tag Functions
The following three functions can be used to tag your code:
```
DUMP_ACCESS_START_TAG(const char* tag, void* begin, void* end)
DUMP_ACCESS_STOP_TAG(const char* tag)
FLUSH_CACHE()
```

#### Parameters:
>**tag:** A string name to identify the trace
>
>**begin:** Identifies the memory address lower bound to trace (Array/Vector Example: `&arr[0]`)
>
>**end:** Identifies the memory address upper bound to trace (Array/Vector Example: `&arr[arr.size()-1]`)

#### Usage:

`DUMP_ACCESS_START_TAG` and `DUMP_ACCESS_STOP_TAG` is used to indicate to Pin the lines of code and the memory regions to trace.

Although the Pintool only writes to file where specified, it starts caching memory accesses the moment the program starts running. Use `FLUSH_CACHE` to flush the contents of the tool's simulated cache.

For example usage of these tag functions, open any of the example C++ programs in `~/work/moneta/Examples/src`.

## Running Moneta

Run `moneta` from any directory to start the local Jupyter Notebook server where the Moneta Jupyter Notebook will be hosted on.

You should see a list of URLs appear. Go to your preferred web browser and paste the link that looks like the following:

<pre>
http://127.0.0.1<b>:8888</b>/?token=...
</pre>

**Notice the 8888 in the link. If you used a port number other than 8888 when creating the Docker container, replace 8888 with your port number.**

**Note For Docker Toolbox**: If you are using Docker Toolbox (this is different from Docker Desktop) as your Docker environment, you will also have to replace `127.0.0.1` with `192.168.99.100` to access the link.

<pre>
http://192.168.99.100<b>:8888</b>/?token=...
</pre>

If you were able to successfully connect, you will see a Jupyter tab on your browser with a list of the files/subdirectories in the `~/work/moneta` directory. Open the `Moneta.ipynb` file.


## Tracing a Program with Moneta

We will use `sorting.cpp` to demonstrate how to use Moneta to trace a program. Make sure you have run either `make` or `make sorting` in the `~/work/moneta` directory beforehand. 

This program is pre-tagged with the `pin_tag.h` functions. The code is tagged as follows:
```
DUMP_ACCESS_START_TAG("Bubble", &bubble[0], &bubble[SIZE-1]);
bubbleSort(bubble, SIZE);
DUMP_ACCESS_STOP_TAG("Bubble");
	
DUMP_ACCESS_START_TAG("Insertion", &insertion[0], &insertion[SIZE-1]);
insertionSort(insertion, SIZE);
DUMP_ACCESS_STOP_TAG("Insertion");

DUMP_ACCESS_START_TAG("Heap sort", &heap[0], &heap[SIZE-1]);
heapSort(heap, SIZE);
DUMP_ACCESS_STOP_TAG("Heap sort");

DUMP_ACCESS_START_TAG("Selection", &selection[0], &selection[SIZE-1]);
selectionSort(selection, SIZE);
DUMP_ACCESS_STOP_TAG("Selection");
```

More implementation details can be found by viewing the source code (Path: `~/work/moneta/Examples/src/sorting.cpp`).

### Generating a Trace
After opening `Moneta.ipynb`, select the first cell and press `SHIFT + ENTER`, or click the `Run` button on the top menu bar.

You should see input boxes appear like below:

![](https://via.placeholder.com/150 "Moneta Inputs")

Once you have inputted your desired values, click the `Generate Trace` button to generate the trace. Trace files can be found in the `~/work/moneta/.output` directory.

#### Input Details

>**Cache Lines:** The number of lines in our fully-associative cache model (Default: 4096)
>
>**Block Size (Bytes):** The size of each cache line in bytes. (Default: 64 Bytes)
>
>**Lines to Output:** The maximum number of memory accesses to record to the HDF5 file. Note that larger numbers will take longer to run. (Default: 10,000,000)
>
>**Working Directory (Optional):** The directory that the exectuable program will run in. If nothing is inputted, it will default to the current directory (Default: `~/work/moneta`)
>
>**Executable Path and Args:** The path to the exectuable (executable name included). Relative paths will be relative to the directory specified in the `Working Directory` input.
>
>**Name for Output:** The name to save the trace as
>
>**Trace Everything:** Disregard all `pin_tag.h` function specifications and trace the entire program for all memory accesses.

#### Example Inputs

>**Cache Lines:** 4096
>
>**Block Size (Bytes):** 64
>
>**Lines to Output:** 10,000,000
>
>**Working Directory (Optional):** ./Examples/build
>
>**Executable Path and Args:** ./sorting (This will run as if you `cd` into `./Examples/build` and then ran `./sorting`)
>
>**Name for Output:** trace_sorting
>
>**Trace Everything:** Unchecked

### Loading a Trace

If the trace generated successfully, you should see `trace_sorting` appear in the Trace box to the right of the input boxes. Select `trace_sorting` and then click `Load Trace`.

If you find that the trace is taking a very long time to load, or the kernel is consistently dying, try reducing `Lines to Output`.

### Analyzing a Trace

If the trace loaded successfully, you should see a memory access plot appear like the one below:

![](https://via.placeholder.com/150 "Sorting Plot")

#### Moneta Plot Features



### Deleting a Trace

From the Trace box, select the traces you want to delete. Note that you can select multiple traces by holding `SHIFT` or `CTRL` while clicking. Clicking `Delete Trace` will permanently remove all files related to the selected traces.







The plot plots all data points in the trace with time/index on the x-axis and memory address on the y-axis

The top menubar contains zooming controls. From left to right:  
**x,y checkboxes:** When enabled, allows panning and zooming in the corresponding directions (Both means normal zooming/panning)  
**Pan & Zoom:** When selected, allows panning and zooming  
**Zoom to Selection:** When selected, zooms to window chosen by click and drag  
**Reset Zoom:** Move window back to original limits determined by all data in trace

Legend contains checkboxes to turn on/off corresponding points  
The frequency of each type of access is display near each point  

The green line on the left depicts the cache size - a product of cache lines * block size  

A list of checkboxes allow you to turn on/off certain tags/data structures/access types in the trace.  

The Zoom to Selection buttons next to each checkbox displays the minimum window containing all accesses to said data structure  

**Refresh Stats:** (WIP) Recalulates and displays the Hit/Miss rate stats for the current plot window.  
**Generate Independent Subplot:** Copies the current plot window into a new plot (created below the original), NOT affected by the checkboxes  
**Generate Dependent Subplot:** Copies the current plot window into a new plot (created below the original), affected by the checkboxes
