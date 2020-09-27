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

Lastly, we have the click zoom and stats panels. The click zoom panel shows the result of using the click zoom toggle. The stats panel shows the hit rates of the overall plot and the current view.

## Important Notes

 - Throughout this README, you will see Pin referenced a few times. Pin is the instrumentation tool that we used to read and interpret memory accesses at runtime. It runs in the background whenever you generate traces and produces the trace files for your program.

 - After connecting to the Docker container, you should be in the `~/work/moneta` directory. This is Moneta's base directory. When using Moneta, any relative paths you input into the text boxes will be relative to this directory.

 - A number of example programs are available under the `~work/moneta/Examples/src` directory. These programs were used by the developers to test Moneta's capabilities and have been left here to use as sample programs for exploring the tool. If you would like to use these programs, you will need to compile them first by running `make` in the `~/work/moneta` directory (or `make filename` without the `.cpp` to compile individual programs). Note that the Makefile compiles the programs with `-O0`. The resulting executables will be located in the `~/work/moneta/Examples/build` directory. 

 - **Know your port number.** The port number was set when you ran the Docker commands to build the container (see main `README`). If you do not remember your port number, open a new terminal and run `docker port moneta` (do **not** connect to the Moneta container). You will see an output like the one below. The `####` is your port number. **You will need this to connect to the Jupyter Notebook.**
 ```
 8888/tcp -> 0.0.0.0:####
 ```
 
 - You can delete one or more traces by selecting them and hitting the `Delete Trace` button.
 
 - `FLUSH_CACHE()` can be used in your program to reset the cache and start again with compulsory misses.
 
 - The plot point colors show the general memory access pattern in that region. Since there are a large number of plot points, multiple plot points are aggregated into a small area of the plot and displayed based on a weighting. Each memory access type (hit, miss, read, write) is given an internal weighting, with misses being weighted higher than the other access types, and the plot displays the point of the highest weight. For the most accurate display of memory access type, we recommend zooming in more.
