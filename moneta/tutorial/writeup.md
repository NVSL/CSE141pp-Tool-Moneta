# Moneta Tutorial

Moneta is a tool that takes executables and records all accesses to memory as the executable runs. This record will from now on be referred to as a trace. You can create it, plot it, analyze it, and delete it. In this tutorial, you will learn the basics of using Moneta by running and tracing an example program.


## Starting Moneta

To start off, first open the link to Moneta in your preferred web browser. You should a list of files in your browser. Then, on the top-right, choose `New > Terminal` to open a Terminal in a new tab. After this, go back to the previous tab with all the files and select `Moneta.ipynb`. A new tab will open for Moneta. You should have 3 tabs open, which we will refer to as the _Home_, _Terminal_, and _Moneta_ tabs respectively.

In the _Moneta_ tab, you will see a cell with the following text:
```
%run main/moneta
```
Click on the cell and either press `SHIFT + ENTER` on your keyboard, or click the `Run` button on the topmost navbar.

## Your First Trace

Now that Moneta has started up, let's run your first memory trace. Switch to the _Terminal_ tab. You should be in the `~/work/moneta` directory (`cd` if you are not). This is also the directory you see in the _Home_ tab. We will refer to this as the `moneta` directory.

In the `moneta` directory, you should see a folder called `tutorial`. `cd` to this folder and you should see a file called `intro.cpp` inside. You will use this program for your first trace. Open `intro.cpp` and take a look at the code (Don't worry if you don't fully understand what the code does. Just know that each `mystery` function accesses the parameter vector in a certain pattern).
```bash
cd tutorial # Alternate: cd ~/work/moneta/tutorial
vim intro.cpp
```

Throughout this tutorial, you will complete the following 3 tasks based off `intro.cpp`:
 1. Find the region in the plot containing all the vectors
 2. Find the region in the plot containing the `X`
 3. Display only the writes and read-misses of `A`, `C`, and `D`.



### Generating Your Trace

Exit the file, compile `intro.cpp` with `04`, and save the executable as `intro`.
```bash
g++ intro.cpp -04 -o intro
```

Go back to the _Moneta_ tab. You will see a few customization options for generating a trace.

The _Cache Lines_ and _Block Size_ will change depending on your cache size. For this tutorial, you can leave these values as the defaults. 

The _Lines to Output_ determines the maximum memory accesses Moneta will trace before stopping. `intro.cpp` should have fewer than 10,000,000 memory accesses, so you can leave this value as the default as well. For larger and/or longer running programs (i.e. programs with more than 10,000,000 memory accesses), you may need to increase this number so your target memory region is traced before Moneta stops. But, do note that larger values will load slower and can potentially crash Jupyter's notebook kernel.

All paths and directories in Moneta are relative to the `moneta` directory. Since `intro` is located at `moneta/tutorial/intro`, enter `tutorial` as the _Working Directory_ and `intro` as the _Executable Path_ (**Side Note:** Leaving _Working Directory_ empty and putting `tutorial/intro` as the _Executable Path_ also works since `intro` doesn't need to run specifically in the _Working Directory_).

For the _Name for Trace_, you can enter any name you want. We will use the name `intro_trace` for this tutorial.

For the toggles, switch the first toggle from _Tagged trace_ to _Full trace_. Leave the second toggle as is.

The inputs should be as follows:

<img src="../../../assets/TutorialFullInputs.png" alt="Tutorial Full Inputs" width="750px"> 

Click the _Generate Trace_ button and wait for the trace to finish generating.

### Exploring the Memory Access Plot

Once the trace finishes generating, you should see `intro_trace` appear under the _Full Trace_ box on the right. Select the `intro_trace` and click _Load Trace_. You should see a plot appear. 

You can use the navigation features in the plot's top navbar to move around and zoom in/out of the plot For this part, disregard all the Legend dropdowns except _Click Zoom_. If you want to use _Click Zoom_, a small zoomed graph will be displayed in the _Click Zoom_ dropdown when you use the corresponding navbar tool.

For this tutorial, we want to look at the memory accesses of all the vectors, but we especially want to find the hidden `X` in the accesses. Using the navbar zoom tools, try to locate and zoom into the area where the vectors are (it will be obvious when you find this area). Spend at **most** one minute. This is just to familiarize yourself with the zoom/navigation options. If you were able to find this area, use the remaining time to find the `X`.

A bit difficult, right? All the other memory accesses are cluttering the plot!


## Tagging the Trace

Since we only care about vector memory accesses, we will need to tag the program to mark only the accesses we care about.

Moneta uses the following tagging functions to determine what, where, when, and how to trace:
```c++
DUMP_START_SINGLE(const char* tag, const void* begin, const void* end)
DUMP_START_MULTI(const char* tag, const void* begin, const void* end)
DUMP_STOP(const char* tag)
FLUSH_CACHE()
```

To use the functions, you will need to `#include` the `pin_tags.h`(this is done for you in `intro.cpp`). This file is in the `moneta` directory:
```c++
#include "../pin_tags.h" // intro.cpp is in "tutorial", ".." brings you to "moneta"
```

You can use `DUMP_START_SINGLE()` or `DUMP_START_MULTI()` to specify an address range to trace. Since we only need to trace the vector regions once, we will use `DUMP_START_SINGLE()` here. For `DUMP_START_SINGLE()`, you will need to include a tag name/label, and the beginning and ending addresses of the memory range to trace. 

For this tutorial, we will use the vectors' variable names as tag names: `A`, `B`, etc. Since vectors are contiguous, the start and end memory addresses are simply the addresses of the first and last elements of the vector: `&vector.front()` and `&vector.back()` respectively. `&vector[0]` and `&vector[SIZE-1]` works as well.

In `main`, surround each mystery function with a `DUMP_START_SINGLE()` call and a corresponding `DUMP_STOP()` call with the same tag. The first few have been done for you in `intro.cpp`:
```c++
DUMP_START_SINGLE("A", &A.front(), &A.back())
mystery_a(A)
DUMP_STOP("A")

DUMP_START_SINGLE("B", &B.front(), &B.back())
mystery_b(B)
DUMP_STOP("B")
//And so on...
```

Save, go to the _Terminal_ tab, compile `intro.cpp` with `04`, and save the executable as `intro_tagged`.
```bash
g++ intro.cpp -04 -o intro_tagged
```

Return to the _Moneta_ tab and generate a new trace with the following options:

<img src="../../../assets/TutorialTaggedInputs.png" alt="Tutorial Tagged Inputs" width="750px"> 

Click the "Generate Trace" button and wait for the trace to finish generating.

## Exploring the Memory Access Plot, But Better This Time

Once generated, you should see `intro_tagged_trace` appear under the _Tagged Trace_ box on the right. Select and load this trace. There's a lot fewer data points cluttering our vectors!

### Finding the Vector Region

As you can see from the plot, you are already zoomed into the vector region and already finished the first task for finding the vectors. The tagging did all the work for you!

### X Marks the Spot

Now, you need to find the `X` access pattern hidden in one of the vectors. Since you tagged memory regions of interest, you can zoom directly to these regions through the _Tags_ dropdown in the Legend. Open _Tags_ and zoom to the various vectors using the zoom button next to each tag until you find the `X` and complete the second goal.

### Display Specific Accesses

For your final goal, you need to display only the writes and read-hits of `A`, `C` and `D`. For this task, you will need the _Accesses_ and _Tags_ section of the Legend.

First, zoom back out so that you can see all the vectors again. This can be done using the _Reset Zoom_ button in the navbar.

In the _Tags_, you may have already noticed the checkboxes. These checkboxes allow you to choose whether the tag is displayed on the plot or not. Using these checkboxes, make it so that the plot only displays vectors/tags `A`, `C` and `D`. A few notes:
 * You should not need to touch `Stack` or `Heap` for this
 * For tags with overlapping address ranges, they will be displayed according to the checkbox that last updated it (there should be no overlapping tags in this tutorial)

In the _Accesses_ section, you also have the ability to show/hide certain access types. Using these checkboxes, display all writes, but only the read-hits to finish the last task. You can find out what each icon means by hovering over them.

### Solutions
 - The hidden `X` is in vector `B`.
 - In _Tags_, everything should be unchecked except `Stack`, `Heap`, `A`, `C` and `D`.
 - In _Accesses_, everything in the _Writes_ columns should be checked, and only the checkbox intersecting _Reads_ and _Hits_ should be checked.