# Moneta Tutorial

In this tutorial, you will learn the basics of using Moneta by running and tracing an example program.


## Starting Moneta

To start off, open the link to the Jupyter Notebook to Moneta in your preferred web browser. If you see a list of files, open `Moneta.ipynb`. You will see a cell with the following text:
```
%run main/moneta
```
Click on the cell and either press `SHIFT + ENTER` on your keyboard, or click the `Run` button on the topmost navbar.

## Your First Trace

Now that Moneta has started up, let's run your first memory trace. On the topmost navbar, select `File > Open...`. You should see a list of files and folders in a new window, one of which is called `example`. Open this folder. You should see a file called `example.cpp` inside. You will use this program for your first trace.

Open `example.cpp` and take a look at the code. Don't worry if you don't fully understand what the code does. Just know that each `mystery` function accesses the parameter vector in a certain pattern.

Throughout this tutorial, you will complete the following 3 tasks based off `example.cpp`:
 1. Find the region containing all the vectors
 2. Find the region containing the `X`
 3. Display only the writes and read-misses of `A`, `C`, and `D`.



### Generating Your Trace

Compile `example.cpp` with `04` and save the executable as `example`.
```
g++ example.cpp -04 -o example
```

Go back to the `Moneta` window. You will see a few customization options for generating a trace.

The "Cache Lines" and "Block Size" will change depending on your cache size. For this example, you can leave this value as the defaults. 

The "Lines to Output" determines the maximum memory accesses Moneta will trace before stopping. `example.cpp` should have fewer than 10,000,000 memory accesses, so you can leave this value as the default as well. For larger and/or longer running programs (i.e. programs with more than 10,000,000 memory accesses), you may need to increase this number so your target memory region is traced before Moneta stops. But, do note that larger values will load slower and can potentially crash Jupyter's notebook kernel.

All paths and directories are relative to the directory containing `Moneta.ipynb`. This is the directory that opens when you selected `File > Open`. This would mean that the `example` executable is located at `tutorial/example`. Enter `tutorial` as the "Working Directory" and `example` as the "Executable Path" (**Side Note:** Leaving "Working Directory" empty and putting `tutorial/example` as the "Executable Path" also works since `example` doesn't need to run specifically in the "Working Directory").

For the "Name for Trace", you can enter any name you want. We will use the name `example_trace` for this tutorial.

For the toggles, switch the first toggle from "Tagged trace" (we haven't tagged anything, so nothing will be recorded) to "Full trace". Leave the second toggle as is.

The inputs should be as follows:
<img src="../../assets/TutorialFullInputs.png" alt="Tutorial Full Inputs" width="400px"> 

Click the "Generate Trace" button and wait for the trace to finish generating.

### Exploring the Memory Access Plot

Once the trace finishes generating, you should see `example_trace` appear under the "Full Trace" box on the right. Select the `example_trace` and click "Load Trace". You should see a plot appear. 

For this example, we want to look at the memory accesses of all the vectors, but we especially want to find the hidden `X` in the accesses. You can use the navigation features in the plot's top navbar to move around and zoom in/out of the plot For this part, disregard everything in the Legend except "Click Zoom". If you want to use "Click Zoom", open the "Click Zoom" dropdown to view the graph. 

Try to locate and zoom into the area where the vectors are. Spend at **most** one minute. This is just to familiarize yourself with the zoom/navigation options. The answer will be revealed in the next sections. If you were able to find this area, move on to the second task and find the `X`.

A bit difficult, right? All the other memory accesses are cluttering the plot!


## Tagging the Trace

Since we only care about vector memory accesses, we will need to tag the trace to filter out the addresses.

On the topmost navbar, select `File > Open` again. You should see a `pin_tag.h` file. This file includes the following tagging functions:
```c++
DUMP_START_SINGLE(const char* tag, const void* begin, const void* end)
DUMP_START_MULTI(const char* tag, const void* begin, const void* end)
DUMP_STOP(const char* tag)
FLUSH_CACHE()
```

Let's use these tagging functions to filter the memory addresses accessed in `example.cpp` so Moneta only record the vectors. To use the functions, open up `example.cpp` and `#include` the `pin_tags.h` file in `example.cpp`:
```c++
#include "../pin_tags.h"
```

You can use `DUMP_START_SINGLE()` or `DUMP_START_MULTI()` to specify an address range to trace. Since we only need to trace the vector regions once, we will use `DUMP_START_SINGLE()` here. 

For `DUMP_START_SINGLE()`, include a tag name/label, and the beginning and ending addresses of the memory range to trace. 

For this example, we will use the vectors' variable names: `A`, `B`, etc. Since vectors are contiguous, the start and end memory addresses are simply the addresses of the first and last elements of the vector: `&vector.front()` and `&vector.back()` respectively. `&vector[0]` and `&vector[SIZE-1]` works as well.

Surround each vector's accesses with a `DUMP_START_SINGLE()` call and a corresponding `DUMP_STOP()` call with the same tag:
```c++
DUMP_START_SINGLE("A", &A.front(), &A.back())
mystery_a(A)
DUMP_STOP("A")
DUMP_START_SINGLE("B", &B.front(), &B.back())
mystery_b(B)
DUMP_STOP("B")
//And so on...
```

Then, compile `example.cpp` with `04` and save the executable as `example_tagged`.
```
g++ example.cpp -04 -o example_tagged
```

Return to Moneta and generate a new trace with the following options:
<img src="../../assets/TutorialTaggedInputs.png" alt="Tutorial Tagged Inputs" width="400px"> 

Click the "Generate Trace" button and wait for the trace to finish generating.

## Exploring the Memory Access Plot, But Better This Time

Once generated, you should see `example_tagged_trace` appear under the "Tagged Trace" box on the right. Select and load this trace. Theres a lot less data points cluttering our vectors!

### Finding the Vector Region

As you can see from the plot, you are already zoomed into the vector region and already finished the first task for finding the vectors. The tagging did all the work for you!

### X Marks the Spot

Now, you need to find the `X` access pattern hidden in one of the vectors. Since you tagged memory regions of interest, you can zoom directly to these regions through the "Tags" dropdown in the Legend. Open "Tags" and zoom to the various vectors until you find the `X` and complete the second goal.

### Display Specific Accesses

For your final goal, you need to display only the writes and read-hits of `A`, `C` and `D`. For this task, you will need the "Accesses" and "Tags" section of the Legend.

In the "Tags", you may have already noticed the checkboxes. These checkboxes allow you to choose whether the tag is displayed on the plot or not. Using these checkboxes, make it so that the plot only displays vectors/tags `A`, `C` and `D`.

In the "Accesses" section, you also have the ability to show/hide certain access types. Using these checkboxes, display all writes, but only the read-hits to finish the last task.

### Solutions
 - The hidden `X` is in vector `B`.
 - In "Tags", everything should be unchecked except `A`, `C` and `D`.
 - In "Accesses", everything in the "Writes" columns should be checked, and only the checkbox intersecting "Reads" and "Hits" should be checked.
