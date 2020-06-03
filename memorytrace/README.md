# Our Project lies here

Compile the program you want to trace  
Start up the notebook and run it after specifying the full path to the executable that is to be analyzed.

# Running an Example

After setup is complete, you can run an example from the "Examples" directory. Here is a sample using Examples/src/sorting.cpp

The cpp file must be compiled prior to running the tool. The sorting.cpp file has already been compiled and is stored as Examples/build/sorting. Launch Jupyter Notebook with the following command. 

```
jupyter notebook --allow-root
```

Running this command should print a file link which should be opened in a browser.
Note: you may need to change 8888 to 8080 after "http://127.0.0.1:" in the link.

Select LinkedSelectors.ipynb to open the notebook.

Once LinkedSelectors.ipynb is open, run the first cell so that options for Cache Lines, Lines to Output, Block Size (Bytes), and Executable Path appear after the bottom of the cell. Cache Lines, Lines to Output, Block Size (Bytes) should have default values that can be edited. 

Fill in "Executable Path" with "./Examples/build/sorting" then click the run button. This should generate an interactable Vaex plot with options of checking and unchecking different data structures, reads, writes, hits, and misses.

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
