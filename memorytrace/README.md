# Our Project lies here

Compile the program you want to trace  
Start up the notebook and run it

# Setup Information

Before running the notebook, change directory to "setup-files" and run the setup.sh script

```
cd setup-files
./setup.sh
```

Ignore any errors about the directories already existing (there shouldn't be any errors though except the off chance that one of you made these directories in the "/setup/" directory already).


# Running an Example

After setup is complete, you can run an example from the "Examples" directory. Here is a sample using Examples/sorting.cpp

The cpp file must be compiled prior to running the tool. Then, launch Juptyer Notebook and open LinkedSelectors.ipynb
```
g++ -o sort ../Examples/sorting.cpp
jupyter notebook --allow-root
```
Launching the notebook should print a file link to be opened in a browser.
Note: you may need to change 8888 to 8080 after "http://127.0.0.1:" in the link.

Once LinkedSelectors.ipynb is open, run the first cell so that options for Cache Lines, Lines to Output, Block Size (Bytes), and Executable Path appear after the bottom of the cell. Cache Lines, Lines to Output, Block Size (Bytes) should have default values that can be edited. 

Fill in "Executable Path" with "./sort" then click the run button. This should generate an interactable Vaex plot with options of checking and unchecking different data structures, reads, writes, hits, and misses.

