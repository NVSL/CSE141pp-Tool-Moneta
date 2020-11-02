# Moneta Tutorial

Moneta is a tool that takes executables and records all accesses to memory as the executable runs. This record will from now on be referred to as a trace. You can create it, plot it, analyze it, and delete it. In this tutorial, you will learn the basics of using Moneta by running and tracing an example program.


## Starting Moneta

To start off, first open the link to Moneta in your preferred web browser. You should see a list of files in your browser. Then, on the top-right, choose `New > Terminal` to open a Terminal in a new tab. After this, go back to the previous tab with all the files and select `Moneta.ipynb`. A new tab will open for Moneta. You should have 3 tabs open (not including this README), which we will refer to as the **Home**, **Terminal**, and **Moneta** tabs respectively.

In the **Moneta** tab, you will see a cell with the following text:
```
%run main/moneta
```
Click on the cell and either press `SHIFT + ENTER` on your keyboard, or click the `Run` button on the topmost navbar.

## Your First Trace

Now that Moneta has started up, let's run your first memory trace. Switch to the **Terminal** tab. You should be in the `~/work/moneta` directory (`cd` if you are not). This is also the directory you see in the **Home** tab. We will refer to this as the `moneta` directory.

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

Go back to the **Moneta** tab. You will see a few customization options for generating a trace.

The **Cache Lines** and **Block Size** will change depending on your cache size. For this tutorial, you can leave these values as the defaults. 

The **Max Accesses** determines the maximum memory accesses Moneta will trace before stopping. `intro.cpp` should have fewer than 10,000,000 memory accesses, so you can leave this value as the default as well. 

All paths and directories in Moneta are relative to the `moneta` directory. Since `intro` is located at `moneta/tutorial/intro`, enter `tutorial` as the **Working Directory** and `intro` as the **Executable Path** 


For the **Name for Trace**, you can enter any name you want. We will use the name `intro_trace` for this tutorial.

For the toggles, switch the first toggle from **Tagged trace** to **Full trace**. Leave the second toggle as is.

The inputs should be as follows:

<img src="../../../assets/TutorialFullInputs.png" alt="Tutorial Full Inputs" width="750px"> 

Click the **Generate Trace** button and wait for the trace to finish generating. You should see `intro_trace` appear under the **Full Trace** box on the right. Select the `intro_trace` and click **Load Trace**. You should see a plot appear. 

>Some Side Notes:
>
>For larger and/or longer running programs (i.e. programs with more than 10,000,000 memory accesses), you may need to increase **Max Accesses** so your target memory region is traced before Moneta stops. But, do note that larger values will load slower and can potentially crash Jupyter's notebook kernel. 
>
>Leaving **Working Directory** empty and putting `tutorial/intro` as the **Executable Path** also works since `intro` doesn't need to run specifically in the **Working Directory**

### Exploring the Memory Access Plot

You can use the navigation features in the plot's top toolbar to move around and zoom in/out of the plot. For now, disregard all the sidebar dropdowns except **Click Zoom**.

 * **Pan/Zoom:** Click & drag to move and scroll to zoom
 * **Zoom to Selection:** Click & drag a square area to zoom into
 * **Click Zoom:** Click & drag a square area, creates a zoomed mini-plot under the **Click Zoom** sidebar dropdown using the bottom right corner of the square
 * **Reset Zoom:** Resets zoom to show everything
 * **Undo/Redo:** Undo/redo last move/zoom

Spend at **most** minute or two to test and familiarize yourself with the zoom/navigation options. You've probably noticed quite quickly that many memory accesses are cluttering the plot!


## Tagging the Trace

Since we only care about vector memory accesses, we will need to tag the program to mark only the accesses we care about.

Moneta uses the following tagging functions to determine what, where, when, and how to trace:
```c++
DUMP_START(const char* tag, const void* begin, const void* end, bool create_new)
DUMP(const char* tag, bool create_new) //Shorthand for DUMP_START if tag already exists
DUMP_STOP(const char* tag)
FLUSH_CACHE()
```

To use the functions, you will need to `#include` the `pin_tags.h` (this is done for you in `intro.cpp`). This file is in the `moneta` directory:
```c++
#include "../pin_tags.h" // intro.cpp is in "tutorial", ".." brings you to "moneta"
```

You can use `DUMP_START` to specify an address range to trace. For this, you will need to include a tag name/label, the beginning and ending addresses of the memory range to trace, and a boolean flag appending an index counter to the tag. 

For this tutorial, we will use the vectors' variable names as tag names: `A`, `B`, etc. Since vectors are contiguous, the start and end memory addresses are simply the addresses of the first and last elements of the vector: `&vector.front()` and `&vector.back()` respectively. `&vector[0]` and `&vector[SIZE-1]` works as well. We do not need the tags to be indexed by when they are called, so we can set the flag as `false`.

Go to the **Terminal** tab and open `intro.cpp`. In `main`, surround mystery functions `A` to `H` with a `DUMP_START()` call and a corresponding `DUMP_STOP()` call with the same tag. The first few have been done for you in `intro.cpp`:
```c++
DUMP_START("A", &A.front(), &A.back(), false);
mystery_a(A);
DUMP_STOP("A");

DUMP_START("B", &B.front(), &B.back(), false);
mystery_b(B);
DUMP_STOP("B");
//And so on...
```

Save and exit, compile `intro.cpp` with `04`, and save the executable as `intro_tagged`.
```bash
g++ intro.cpp -04 -o intro_tagged
```

Return to the **Moneta** tab and generate a new trace with the following options. Make sure to toggle from **Full trace** to **Tagged trace**:

<img src="../../../assets/TutorialTaggedInputs.png" alt="Tutorial Tagged Inputs" width="750px"> 

Click the "Generate Trace" button and wait for the trace to finish generating. Once generated, you should see `intro_tagged_trace` appear under the **Tagged Trace** box on the right. Select and load this trace. 

## Exploring the Memory Access Plot, But Better This Time

Once loaded, you can see that there's much less data points cluttering our vectors!

### Finding the Vector Region

As you can see from the plot, you are already zoomed into the vector region and already finished the first task for finding the vectors. The tagging did all the work for you!

### X Marks the Spot

Now, you need to find the `X` access pattern hidden in one of the vectors. Since you tagged memory regions of interest, you can zoom directly to these regions through the **Tags** dropdown in the sidebar. Open **Tags** and zoom to the various vectors using the zoom button next to each tag until you find the `X` and complete the second goal.

### Display Specific Accesses

For your final goal, you need to display only the writes and read-hits of `A`, `C` and `D`. For this task, you will need the **Accesses** and **Tags** section of the sidebar.

First, zoom back out so that you can see all the vectors again. This can be done using the **Reset Zoom** button in the toolbar.

In the **Tags**, you may have already noticed the checkboxes. These checkboxes allow you to choose whether the tag is displayed on the plot or not. Using these checkboxes, make it so that the plot only displays vectors/tags `A`, `C` and `D`. A few notes:
 * You should not need to touch `Stack` or `Heap` (if they appear) for this
 * For tags with overlapping address ranges, disabled checkboxes take priority (there is an overlapping tag in this program)

In the **Accesses** section, you also have the ability to show/hide certain access types. Using these checkboxes, display all writes, but only the read-hits to finish the last task. You can find out what each icon means by hovering over their corresponding checkbox.

### Solutions
 - The hidden `X` is in vector `B`.
 - In **Tags**, everything should be unchecked except `Stack` (if it appears), `Heap`, `vectors`, `A`, `C` and `D`.
 - In **Accesses**, everything in the **Writes** columns should be checked, and only the checkbox intersecting **Reads** and **Hits** should be checked.
