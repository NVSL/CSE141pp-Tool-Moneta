# Developer Guide: Intro to CSE142 Pintool
## General Workflow:
1.	student annotates their program with macros and tags data structures of interest
2.	Student compiles their program as an executable
3.	Student opens the notebook, sets values for Cache Lines, Lines to Output, Block Size, and Executable Path, then hits run
4.	The notebook first runs CSE142 version of the pintool on the executable and outputs  all data in the form of an HDF5 file
5.	This file is then opened using a python library called Vaex which plots the data as an interactive widget.
6.	Student is able to analyze their program by interacting with the plot and selecting what type of accesses they want to examine and for which data structures.

## The Pintool – How to Run and Modify:
* The pintool is run from the runPintool.py script. This file verifies the user input from the notebook is valid, then runs the pintool via command line with the following command format:
`$ /setup/pintool/pin.sh -ifeellucky -injection child -t /setup/converter/trace_tool.so -o /setup/converter/outfiles -c CACHE_SIZE -m NUM_LINES -l BLOCK_SIZE -- EXECUTABLE`
  * The first argument is the path to the executable pin.sh. This is standard with PIN and is what will run the precompiled CSE142 version pintool. 
  * The next two flags -ifeellucky and -injection child allow the version of PIN in the docker image to run with newer versions of Linux. We are using an older version of PIN, therefore not including these flags will raise an error about an incompatible version of Linux.
  * The -t flag specifies the path to the CSE142 version of the pintool in the form of a compiled shared library. In order to run the tool, this .so file must already be compiled. The specified library, trace_tool.so, is what specifies to PIN which memory access to track and outputs all collected data to an HDF5 file. 
  * The -o flag specifies the directory that the output files should go. For, all outputs are directed to /setup/converter/outfiles so that the subsequent python scripts can locate and load the output files into Vaex. 
  * The following flags (-c, -m, -l) are set by the user in the notebook or a developer can add the inputs directly if running from the command line.
  * Following –- should be the absolute path to the student’s precompiled executable. (A developer can also specify the relative path to the executable from /setup/pintool/ , but it is best to stick with absolute paths.)
  * Note: in the Dockerfile, “pin” is set as an alias for “/setup/pintool/pin.sh -ifeellucky -injection child” in the ~./bashrc file so if running from command line, the following command is equivalent to the command above:
`$ pin -t /setup/converter/trace_tool.so -o /setup/converter/outfiles -c CACHE_SIZE -m NUM_LINES -l BLOCK_SIZE -- EXECUTABLE`

* The file that trace_tool.so is built from can be found at CSE141pp-Tool-MemoryTrace/Setup/trace_tool.cpp
  * To edit this file then convert it to a .so, first copy the .cpp to /setup/pintool/source/tools/ManualExamples/ 
  * Run the following commands:
        `$make
        $make obj-intel64/trace_tool.so
        $cp obj-intel64/trace_tool.so /setup/converter`
  *	You can now use the command from above to execute the pintool with the updated .so file

## The Pintool – What Is It Doing:
* Intel’s PIN allows a user to instrument a program to analyze many aspects of the execution. We are using a subset of PIN’s functionality in order to track memory accesses throughout a student’s executable. For more information about PIN, visit https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/ for a User Guide. 
  *	Note: We are using Pin 2.14, an older version of pin in order to be able to link necessary libraries to write to HDF5 files via our tool. The newest version ( Pin 3.2 ) makes it very difficult to link other libraries to the tool. For our purposes, the two versions of Pin are generally the same considering the modest extent of functionality of Pin that we are using. 
  *	In trace_tool.cpp, a fully associative cache is simulated and is used to determine if the memory access is a hit or a miss. This is important to remember that Pin cannot tell us if the access is a hit or miss in the real cache. 

*	Starting at main in trace_tool.cpp, first PIN_InitSymbols() and PIN_Init() are called. These are both from the PIN API and must be called prior to PIN_StartProgram() in order for Pin to be able to read symbols and verify the arguments passed to the pintool are valid. 
      * More info: https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/group__PIN__CONTROL.html#ga8cf4aca0b0bdbc7fc0ae965883d8e3c2
*	The values that were passed in as flags to the command line are checked and default values are set if none are specified or if they are out of bounds. 
      *	If debug mode is on, then these values are printed to std err
 *	Two hdf5 files are created: 
      *	trace.hdf5 tracks the accesses with tagged addresses and the type of access (Read, Write, Hit, Miss)
      *	cache.hdf5 tracks all of the accesses, regardless if it was tagged to see what fills up the cache
 *	IMG_AddInstrumentFunction() registers the specified FindFunc method as a call back when loading an image
      *	FindFunc is used to locate the Start and Stop macros that are in the student’s executable so pin knows when to start and stop tracking memory accesses.
      *	Set max output?
      *	Info on IMG API: https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/group__IMG__BASIC__API.html#ga494869187b5d94d7dd346bc9ff49642f
 *	INS_AddInstrumentFunction() is where we specify what to do for each instruction via Instruction method. Here we specify to the pintool if the instruction is a read, then call RecordMemRead. If it is a write, then call RecordMemWrite.
      *	Both Record methods take in the address of the memory access and determine if this access was a hit or a miss based off of the simulated cache. They both then call the method write_to_memfile which adds the access and its information to a buffer that will be written to the hdf5 file (more on HDF5 later).
      *	More on INS API: https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/group__INS__INST__API.html
 *	PIN_AddFiniFunction() specifies a function which is to be run right before the end of the pintool run. In this case, the function Fini is passed in, meaning Fini will be run right before the program terminates. 
      *	Fini first creates the tag_map.csv which logs what tag number maps to which tag name that was specified by the student. This is important for plotting the data and associating the different accesses to specific data structures. 
      *	The write buffer with any remaining accesses is flushed to the hdf5 output files and the files are closed. 
 *	After all of this is specified, we start instrumentation with Pin using PIN_StartProgram(). While Pin is running, it refers to the above functions to check what it is supposed to tracking. 
      *	Pin has many other functionalities and more examples of what pin can do can be found out /setup/pintool/source/tools/ManualExamples. Look through the .cpp files to see more examples. 

## HDF5:
* Using HDF5 file format is much more efficient than writing to a typical csv file. Since we are writing large sets of data, efficiency is very important. It is faster to write to hdf5 and more importantly, faster for the Vaex library to open hdf5 files. Because we are using hdf5, Vaex can open and process millions of lines of data in seconds. 
