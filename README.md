# Moneta

Generate and visualize billions of memory accesses with this project built on PIN and HDF5.

## Table of Contents

   * **Getting Started**
      * [Building the Image](#getting-started)
      * [Building the Container](#building-the-container)
   * **Using Moneta**
      * [Important Notes](#using-moneta)
      * [Tagging Programs](#tagging-programs)
      * [Running Moneta](#running-moneta)
      * [Tracing a Program with Moneta](#tracing-a-program-with-moneta)
         * [Generating a Trace](#generating-a-trace)
         * [Loading a Trace](#loading-a-trace)
         * [Analyzing a Trace](#analyzing-a-program)
         * [Moneta Plot Features](#moneta-plot-features)
         * [Deleting a Trace](#deleting-a-trace)
   * **Developers**
      * [View](#Developers)

## Getting Started

### Building the Image
First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Tool-Moneta
cd CSE141pp-Tool-Moneta
```

Build the Docker image and name it `moneta-img`.
```
docker build -t moneta-img .
```


### Building the Container

Due to the way Windows interprets paths, these next few instructions may differ slightly depending on your operating system. If you are using Windows, [skip to this section](#windows).

<a name="port"></a>Start a detached docker container named `moneta`. **Take note of the `####:8888` in the command.** The `####` will be your **port number** for running the notebook. The port number will be `8888` here but can be changed if there are any conflicts. **Note that you will have to change the Jupyter Notebook URL port to the port set here when you run the `moneta` command.**
```
docker run --detach --name moneta -p 8888:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes moneta-img bash -c "while true; do sleep 10;done"
```

Connect to the container.
```
docker exec -it moneta bash
```

#### <a name="windows"></a>Windows: Run the following instead

```
MSYS_NO_PATHCONV=1 docker run --detach --name moneta -p 8888:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes moneta-img bash -c "while true; do sleep 10;done"
```

To connect to the container, you may need be prompted to use `winpty`:
```
winpty docker exec -it moneta bash
```
# Using Moneta

Instructions on how to run and use Moneta

## Important Notes

 - Throughout this README, you will see Pin referenced a few times. Pin is the instrumentation tool that we used to read and interpret memory accesses at runtime. It runs in the background whenever you generate traces and produces the trace files for your program.

 - After connecting to the Docker container, you should be in the `~/work/moneta` directory. This is Moneta's base directory. When using Moneta, any relative paths you input into the text boxes will be relative to this directory.

 - A number of example programs are available under the `~work/moneta/examples/src` directory. These programs were used by the developers to test Moneta's capabilities and have been left here to use as sample programs for exploring the tool. If you would like to use these programs, you will need to compile them first by running `make` in the `~/work/moneta` directory (or `make filename` without the `.cpp` to compile individual programs). Note that the Makefile compiles the programs with `-O0`. The resulting executables will be located in the `~/work/moneta/examples/build` directory. 

 - **Know your port number.** The port number was set when you ran the Docker commands to build the container (see main `README`). If you do not remember your port number, open a new terminal and run `docker port moneta` (do **not** connect to the Moneta container). You will see an output like the one below. The `####` is your port number. **You will need this to connect to the Jupyter Notebook.**
 ```
 8888/tcp -> 0.0.0.0:####
 ```


## Tagging Programs

`pin_tags.h` is the header file containing the functions to tag memory traces for your program. By default, it is located in the `~/work/moneta` directory, but you are free to copy this file to any directory that you find convenient. The functions in this file will indicate to Pin when it should start and stop writing memory accesses to file, and which memory address ranges it should trace.

To use `pin_tags.h` you will need to add `#include "PATH_TO_FILE/pin_tags.h"` (Default: `#include "/home/jovyan/work/moneta/pin_tags.h`) to the top of your C++ file. 

### Pin Tag Functions
The following three functions can be used to tag your code:
```
DUMP_START(const char* tag, const void* begin, const void* end, bool create_new)
DUMP_STOP(const char* tag)
START_TRACE()
FLUSH_CACHE()
```

#### Parameters:
**tag:** A string name to identify the trace

**begin:** Identifies the memory address lower bound to trace (Array/Vector Example: `&arr[0]`)

**end:** Identifies the memory address upper bound to trace (Array/Vector Example: `&arr[arr.size()-1]`)

**create_new:** 
- If the tag name has not been used before, then create_new is ignored. 

- If the tag name has been used before then,
    - If create_new is true, then the tags will start having an index, tag0, tag1, ...
    - If create_new is false, then the tracing will add the information to the last tag of the same name, so the same tag.
#### Usage:

`DUMP_START` and `DUMP_STOP` is used to indicate to Pin the lines of code and the memory regions to trace.

Although the Pintool only writes to file where specified, it starts caching memory accesses the moment the program starts running. Use `FLUSH_CACHE` to flush the contents of the tool's simulated cache.

By default tracing will start at the main function, however this can be changed by specifying a new function in `Function to start trace at:`. If Moneta cannot find the function specifed, such as the case of inline functions, than an explicit use of `START_TRACE` is required. Tracing will then begin at this point. In addition you must also set `Function to start trace at:` to gibberish that won't be called, as it has priority over `START_TRACE`. Only use `START_TRACE` if you do not want to rely on `Function to start trace at:`. If you don't fill in `Function to start trace at:` tracing will begin at main by default even if you use `START_TRACE`.

For example usage of these tag functions, open any of the example C++ programs in `~/work/moneta/examples/src`.

## Running Moneta

Run `moneta` from any directory to start the local Jupyter Notebook server where the Moneta Jupyter Notebook will be hosted on.

You should see a list of URLs appear. Go to your preferred web browser and paste the link that looks like the following:

<pre>
http://127.0.0.1<b>:8888</b>/?token=...
</pre>

**Notice the `8888` in the link. If you used a port number other than `8888` when creating the Docker container, replace `8888` with your port number.**

**Note For Docker Toolbox**: If you are using Docker Toolbox (this is different from Docker Desktop) as your Docker environment, you will also have to replace `127.0.0.1` with `192.168.99.100` to access the link.

<pre>
http://192.168.99.100<b>:8888</b>/?token=...
</pre>

If you were able to successfully connect, you will see a Jupyter tab on your browser with a list of the files/subdirectories in the `~/work/moneta` directory. Open the `Moneta.ipynb` file.


## Tracing a Program with Moneta

We will use `sorting.cpp` to demonstrate how to use Moneta to trace a program. Make sure you have run either `make` or `make sorting` in the `~/work/moneta` directory beforehand. 

This program is pre-tagged with the `pin_tag.h` functions. The code is tagged as follows:
```
DUMP_START("Bubble", &bubble[0], &bubble[SIZE-1], false);
bubbleSort(bubble, SIZE);
DUMP_STOP("Bubble");
	
DUMP_START("Insertion", &insertion[0], &insertion[SIZE-1], false);
insertionSort(insertion, SIZE);
DUMP_STOP("Insertion");

DUMP_START("Heap sort", &heap[0], &heap[SIZE-1], false);
heapSort(heap, SIZE);
DUMP_STOP("Heap sort");

DUMP_START("Selection", &selection[0], &selection[SIZE-1], false);
selectionSort(selection, SIZE);
DUMP_STOP("Selection");
```

More implementation details can be found by viewing the source code (Path: `~/work/moneta/examples/src/sorting.cpp`).

### Generating a Trace
After opening `Moneta.ipynb`, select the first cell and press `SHIFT + ENTER`, or click the `Run` button on the top menu bar.

You should see input boxes appear like below:

![](https://i.gyazo.com/21ad23f58b629498a9afc96984d3235b.png "Moneta Inputs")

Once you have inputted your desired values, click the `Generate Trace` button to generate the trace. Trace files can be found in the `~/work/moneta/.output` directory.

#### Input Details

**Cache Lines:** The number of lines in our fully-associative cache model (Default: 4096)

**Block Size (Bytes):** The size of each cache line in bytes. (Default: 64 Bytes)

**Max Accesses:** The maximum number of memory accesses to record to the HDF5 file. **Warning: Larger numbers will take longer to run and can potentially crash the kernel.** If this happens, lower the Max Accesses and, if possible, modify the executable accordingly to reduce iterations and execution time. (Default: 10,000,000)

**Working Directory (Optional):** The directory that the exectuable program will run in. If nothing is inputted, it will default to the current directory (Default: `~/work/moneta`)

**Executable Path and Args:** The path to the exectuable (executable name included). Relative paths will be relative to the directory specified in the `Working Directory` input.

**Name for Trace:** The name to save the trace as

**Function to start trace at:** Specify a function to begin recording of traces. If left blank the default function is main. May be used in conjunction with `START_TRACE` tag.

#### Example Inputs

**Cache Lines:** 4096

**Block Size (Bytes):** 64

**Lines to Output:** 10,000,000

**Working Directory (Optional):** ./examples/build

**Executable Path and Args:** ./sorting (This will run as if you `cd` into `./examples/build` and then ran `./sorting`)

**Name for Output:** trace\_sorting


### Loading a Trace

If the trace generated successfully, you should see `trace_sorting` appear in the Trace box to the right of the input boxes. Select `trace_sorting` and then click `Load Trace`.

If you find that the trace is taking a very long time to load, or the kernel is consistently dying, try reducing `Lines to Output`.

## Analyzing a Program
Now to visualize those accesses for your program. We need to run the pintool and plot the accesses. The jupyter notebook encompasses this functionality.


After opening `Moneta.ipynb`, select the first cell and press `SHIFT + ENTER`, or click the `Run` button on the top menu bar.  
If the trace loaded successfully, you should see input boxes appear like below:
![Start Cell](../assets/StartCell.png?raw=true)

**Inputs:**  
- `Cache Lines`: The number of lines in our fully-associative cache model (4096)  
- `Block Size`: Size of each cache line in bytes (64) - So default cache size is (4096 * 64 bytes - a 256 KB cache)  
- `Lines to Output`: Maximum number of memory accesses to record (10,000,000) **Large numbers can crash the kernel**  
- `Working Directory (opt)`: Directory the executable is run in (`~/work/moneta/`)  
- `Executable Path and Args`: Executable to run such as `/usr/bin/ls` and `./add 1 2`  
- `Name for Output`: Name your trace as it will appear on the right  
- `Tagged Trace/Full Trace`: Tagged - Only accesses between tag calls are recorded. Otherwise, everything is recorded
- `Track from Beginning/Track main`: Beginning - Trace from first tagged/normal access. Main - Start recording once main is called

Let's go with the defaults for now and enter the path to your executable. Name it `hello_world`. Then, hit `Generate Trace`  
![Generate Trace](../assets/Generate.png?raw=true)
On success, `hello_world` shows up in the trace list. Select it and hit `Load Trace`  
![Load Trace](../assets/Load.png?raw=true)

### Moneta Plot Features

### Axes, Plot Points, and Cache Line

The x-axis is the access number. The memory addresses are plotted in the order in which they are accessed.
The y-axis is bytes. It is always fixed to start at 0 and shows the number of bytes from one point to another.
You can notice the 10 diagonals each with 10 points or 5 unique accesses that our nested loop iterates through.

The plot point colors show the general memory access pattern in that region. Since there are a large number of plot points, multiple plot points are aggregated into a small area of the plot and displayed based on a weighting. Each memory access type (hit, miss, read, write) is given an internal weighting, with misses being weighted higher than the other access types, and the plot displays the point of the highest weight. For the most accurate display of memory access type, we recommend zooming in more.

The plot displays a cache line on the left side of the plot (the lime green line by default). The cache line size is based off the cache lines and block size inputs and is used as a scale bar to visualize how the plotted accesses fit in the cache. Right now, it's larger than the address range of the array!

### Toolbar
<img src="../assets/Toolbar.png" alt="Toolbar" width="400px">  
At init, we start off with being able to pan and zoom around the plot ("hand"). The middle button enables zoom to selection where dragging and selecting a region moves plot to any points in that region with a hard limit of 128 on each dimension. The right button ("mouse") activates click zoom, which zooms in by 10x.

The refresh button resets plot to limits on load. Undo/redo are triggered by any panning and zooming with a history of 50 udpates.

The x and y checkboxes enable panning and zooming in their respective dimensions.

### Legend
Another way to explore your program is checking the type of each access.  
<img src="../assets/Accesses.png" alt="Legend Accesses" width="400px">  
This panel allows you to turn on/off any combination of reads and writes against hits, capacity misses, and compulsory misses.  
Each access in the loop has a read hit (dark blue) and write hit (light blue).  The color picker next to each dark blue checkbox allows you to configure the colors. You can even modify the cache specifier's color plus reset all the colors to their defaults.

<img src="../assets/Tags.png" alt="Legend Tags" width="400px">  
In this panel, we see the tags we added to our program just like we expected! Try (de)selecting each of the tags and see if they update the expected part of the trace.

Each tag comes with a button which on hover shows detailed information of the tag including accesses and hit rate. You can click on the button to zoom in to just the tag you want to see.

Lastly, we have the click zoom and stats panels. The click zoom panel shows the result of using the click zoom toggle. The stats panel shows the hit rates of the overall plot and the current view.


### Deleting a Trace

From the Trace box, select the traces you want to delete. Note that you can select multiple traces by holding `SHIFT` or `CTRL` while clicking. Clicking `Delete Trace` will permanently remove all files related to the selected traces.


## Developers
 - Amithab Arumugam
 - Ashwin Rao
 - Christie Lincoln
 - Elvis Tran
 - Jad Barrere
 - Kevin Tang
 - Sam Liu
 - Stephanie Hernandez
