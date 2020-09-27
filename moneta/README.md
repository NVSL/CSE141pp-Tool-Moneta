# Using Moneta

Instructions on how to tag and analyze programs with Moneta

## Tagging Programs
A tag represents a part of the execution of a program bounded by a lower and upper memory address. There are several functions defined in `~/work/moneta/pin_tags.h` that can be used to create a tag. The pintool looks for these calls to manage tags.

`DUMP_START_SINGLE(const char* tag, void* begin, void* end)` - Create a tag for the memory region [begin, end] (inclusive) from when this function is called to when the corresponding `DUMP_STOP` is called.  
`DUMP_START_MULTI(const char* tag, void* begin, void* end)` - Same as Single except each start call with the same tag name results in a separate tag (ex. `tag1`, `tag2`, etc.)  
`DUMP_START(const char* tag)` - Shorthand for the above two calls after they've been called already automatically using the same address range and single/multi option since **the same tag cannot be redefined with a different address range**  
`DUMP_STOP(const char* tag)` - Stops tracing the tag

### Example
```c++
...
#include 'pin_tags.h'
int main() {
    int arr [5] = {0}; // An array of 5 ints
    DUMP_START_SINGLE("acc_array", arr, arr+4); // arr is the address of first element, arr + 4 == fifth element's address
    ... // Do stuff with array such as
    std::cout << "Hello world! " << arr[0] << "\n";
    DUMP_STOP("acc_array");
    ...
    DUMP_START_MULTI("loop_array", arr, arr+4); // new tag to indicate different part of the program, multi so shows up as loop_array0
    for (int i = 0; i < 10; i++) {
        DUMP_START("loop_array"); // using shorthand, same address range of [arr, arr+4]
        for (int j = 0; j < 5; j++) { // being a multi tag, each inner loop will fall into `loop_array1`, `loop_array2`, ..., `loop_array10`
	    arr[j]+=i;
	}
	DUMP_STOP("loop_array"); // stop each loop tag
    }
    DUMP_STOP("loop_array"); // remember to stop the initial call as well!!
    return 0;
}
```
See `~/work/moneta/Examples/src/` for more examples  
Make sure to compile your program at `-O0` initially, so nothing is optimized out!

## Analyzing the Program
Now to visualize those accesses for your program. We need to run the pintool and plot the accesses. The jupyter notebook encompasses this functionality.


After opening `Moneta.ipynb`, select the first cell and press `SHIFT + ENTER`, or click the `Run` button on the top menu bar.  
You should see input boxes appear like below:
![Start Cell](../../assets/StartCell.png?raw=true)

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
![Generate Trace](../../assets/Generate.png?raw=true)
On success, `hello_world` shows up in the trace list. Select it and hit `Load Trace`  
![Load Trace](../../assets/Load.png?raw=true)

With Access Number on the x-axis and the addresses on the y-axis, you can notice the 10 diagonals each with 10 points or 5 unique accesses that our nested loop iterates through. The green line on the left shows how large the cache is. Right now, it's larger than the address range of the array!

### Toolbar
<img src="../../assets/Toolbar.png" alt="Toolbar" width="400px">  
At init, we start off with being able to pan and zoom around the plot ("hand"). The middle button enables zoom to selection where dragging and selecting a region moves plot to any points in that region with a hard limit of 128 on each dimension. The right button ("mouse") activates click zoom.

The refresh button resets plot to limits on load. Undo/redo are triggered by any panning and zooming with a history of 50 udpates.

The x and y checkboxes enable panning and zooming in their respective dimensions.

### Legend
Another way to explore your program is checking the type of each access.  
<img src="../../assets/Accesses.png" alt="Legend Accesses" width="400px">  
This panel allows you to turn on/off any combination of reads and writes against hits, capacity misses, and compulsory misses.  
Each access in the loop has a read hit (dark blue) and write hit (light blue).  The color picker next to each dark blue checkbox allows you to configure the colors. You can even modify the cache specifier's color plus reset all the colors to their defaults.

<img src="../../assets/Tags.png" alt="Legend Tags" width="400px">  
In this panel, we see the tags we added to our program just like we expected! Try (de)selecting each of the tags and see if they update the expected part of the trace.

Each tag comes with a button which on hover shows detailed information of the tag including accesses and hit rate. You can click on the button to zoom in to just the tag you want to see.

## Important Notes

 - Throughout this README, you will see Pin referenced a few times. Pin is the instrumentation tool that we used to read and interpret memory accesses at runtime. It runs in the background whenever you generate traces and produces the trace files for your program.

 - After connecting to the Docker container, you should be in the `~/work/moneta` directory. This is Moneta's base directory. When using Moneta, any relative paths you input into the text boxes will be relative to this directory.

 - A number of example programs are available under the `~work/moneta/Examples/src` directory. These programs were used by the developers to test Moneta's capabilities and have been left here to use as sample programs for exploring the tool. If you would like to use these programs, you will need to compile them first by running `make` in the `~/work/moneta` directory (or `make filename` without the `.cpp` to compile individual programs). Note that the Makefile compiles the programs with `-O0`. The resulting executables will be located in the `~/work/moneta/Examples/build` directory. 

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
DUMP_ACCESS_START_TAG(const char* tag, void* begin, void* end)
DUMP_ACCESS_STOP_TAG(const char* tag)
FLUSH_CACHE()
```

#### Parameters:
**tag:** A string name to identify the trace

**begin:** Identifies the memory address lower bound to trace (Array/Vector Example: `&arr[0]`)

**end:** Identifies the memory address upper bound to trace (Array/Vector Example: `&arr[arr.size()-1]`)

#### Usage:

`DUMP_ACCESS_START_TAG` and `DUMP_ACCESS_STOP_TAG` is used to indicate to Pin the lines of code and the memory regions to trace.

Although the Pintool only writes to file where specified, it starts caching memory accesses the moment the program starts running. Use `FLUSH_CACHE` to flush the contents of the tool's simulated cache.

For example usage of these tag functions, open any of the example C++ programs in `~/work/moneta/Examples/src`.

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

![](https://i.gyazo.com/21ad23f58b629498a9afc96984d3235b.png "Moneta Inputs")

Once you have inputted your desired values, click the `Generate Trace` button to generate the trace. Trace files can be found in the `~/work/moneta/.output` directory.

#### Input Details

**Cache Lines:** The number of lines in our fully-associative cache model (Default: 4096)

**Block Size (Bytes):** The size of each cache line in bytes. (Default: 64 Bytes)

**Lines to Output:** The maximum number of memory accesses to record to the HDF5 file. **Warning: Larger numbers will take longer to run and can potentially crash the kernel.** If this happens, lower the Lines of Output and, if possible, modify the executable accordingly to reduce iterations and execution time. (Default: 10,000,000)

**Working Directory (Optional):** The directory that the exectuable program will run in. If nothing is inputted, it will default to the current directory (Default: `~/work/moneta`)

**Executable Path and Args:** The path to the exectuable (executable name included). Relative paths will be relative to the directory specified in the `Working Directory` input.

**Name for Output:** The name to save the trace as

**Trace Everything:** Disregard all `pin_tag.h` function specifications and trace the entire program for all memory accesses.

#### Example Inputs

**Cache Lines:** 4096

**Block Size (Bytes):** 64

**Lines to Output:** 10,000,000

**Working Directory (Optional):** ./Examples/build

**Executable Path and Args:** ./sorting (This will run as if you `cd` into `./Examples/build` and then ran `./sorting`)

**Name for Output:** trace\_sorting

**Trace Everything:** Unchecked

### Loading a Trace

If the trace generated successfully, you should see `trace_sorting` appear in the Trace box to the right of the input boxes. Select `trace_sorting` and then click `Load Trace`.

If you find that the trace is taking a very long time to load, or the kernel is consistently dying, try reducing `Lines to Output`.

### Analyzing a Trace

If the trace loaded successfully, you should see a memory access plot appear like the one below:

**TODO: UPDATE IMAGE WHEN LEGEND SCROLLBARS ARE FIXED**
![](https://via.placeholder.com/150 "Sorting Plot")

#### Moneta Plot Features

##### Axes, Plot Points, and Cache Line

The x-axis is the access number. The memory addresses are plotted in the order in which they are accessed.

The y-axis is bytes. It is always fixed to start at 0 and shows the number of bytes from one point to another.

The plot point colors show the general memory access pattern in that region. Since there are a large number of plot points, multiple plot points are aggregated into a small area of the plot and displayed based on a weighting. Each memory access type (hit, miss, read, write) is given an internal weighting, with misses being weighted higher than the other access types, and the plot displays the point of the highest weight. For the most accurate display of memory access type, we recommend zooming in more.

The plot displays a cache line on the left side of the plot (the lime green line by default). The cache line size is based off the cache lines and block size inputs and is used as a scale bar to visualize how the plotted accesses fit in the cache.

##### Top Menubar

The top menubar contains zooming controls. From left to right:

**x/y checkboxes:** When unchecked, prevent clicking/dragging and zooming in that direction

**Pan & Zoom:** When selected, click and drag to pan the plot and scroll to zoom in/out

**Zoom to Selection:** When selected, click and drag a square area to zoom into

**Reset Zoom:** When clicked, resets the plot's location and zoom to it's initial load state

**Undo/Redo:** When clicked, undos/redos the last pan or zoom (Max Undos/Redos: 50)

##### Legend

The legend matches memory access type with the plot colors and allows toggling the display of memory access types. From top to bottom:

**Hit/Miss Checkboxes:** When checked, shows the corresponding hit/capacity miss/compulsory miss on the graph. Can be combined with Read/Write Checkboxes

**Read/Write Checkboxes:** When checked, shows the corresponding read/write on the graph. Can be combined with Hit/Miss Checkboxes

**Colorpickers:** When clicked, displays a menu of colors that you can choose from. The corresponding access type will be displayed in your selected color on the plot

**Reset Colorpickers:** When clicked, resets the colors of the Colorpickers and the plot to their original colors

##### Tags

**Checkboxes:** When checked, plots memory accesses that fall within the address range specified by the tag name

**Zoom To Tag/Hover Tooltip Stats:** When clicked, zooms to the memory address ranges specified by the tag name. When hovered, displays memory access stats about the tag


### Deleting a Trace

From the Trace box, select the traces you want to delete. Note that you can select multiple traces by holding `SHIFT` or `CTRL` while clicking. Clicking `Delete Trace` will permanently remove all files related to the selected traces.
