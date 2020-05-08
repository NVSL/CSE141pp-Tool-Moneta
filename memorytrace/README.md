# Our Project lies here

Compile the program you want to trace  
Start up the notebook and run it after specifying the full path to the executable that is to be analyzed.

# Running an Example

After setup is complete, you can run an example from the "Examples" directory. Here is a sample using Examples/src/sorting.cpp

The cpp file must be compiled prior to running the tool. The sorting.cpp file has already been compiled and is stored as Examples/build/sorting. Launch Juptyer Notebook with the following command. 

```
jupyter notebook --allow-root
```

Running this command should print a file link which should be opened in a browser.
Note: you may need to change 8888 to 8080 after "http://127.0.0.1:" in the link.

Select LinkedSelectors.ipynb to open the notebook.

Once LinkedSelectors.ipynb is open, run the first cell so that options for Cache Lines, Lines to Output, Block Size (Bytes), and Executable Path appear after the bottom of the cell. Cache Lines, Lines to Output, Block Size (Bytes) should have default values that can be edited. 

Fill in "Executable Path" with "./Examples/build/sorting" then click the run button. This should generate an interactable Vaex plot with options of checking and unchecking different data structures, reads, writes, hits, and misses.

