# Developer Documentation

This directory contains useful information regarding the implementation of the followng aspects of Moneta:
 - Pin
 - Vaextended

## General Workflow:
1.	Student annotates their program with tag functions and tags data structures of interest
2.	Student compiles their program as an executable
3.	Student opens the Jupyter Notebook, sets values for Cache Lines, Block Size, Lines to Output, Working Directory, Executable Path, Name for Trace and Trace Everything
4.	Notebook runs our custom Pintool, `trace_tool.so`, on the executable and outputs all data in the form of an HDF5 file
5.	Vaex (Python library) open the file and plots the data as an interactive widget. This widget is linked to our custom backend called `Vaextended`
6.	Student analyzes their program by interacting with the plot and selecting what type of accesses they want to examine and for which data structures