# LinkedSelectors Documentation

Programmer documentation for developing the LinkedSelectors notebook and its necessary dependencies

## The py Files

LinkedSelectors makes use of 4 py files to execute the tool: imports.py, createUserInput.py, runPintool.py, and generateGraph.py. The Jupyter Notebook will run the scripts using `%run -i fileName.py`. The `-i` flag will allow the variables in the script to be accessed by the other scripts, rather than restricting the scope of the variables to the script it is declared in.

#### imports.py

This file contains the list of imports needed to execute the other 3 files in a centralized location. Add any imports that are used multiple times into this file to reduce repetitive imports in each file.

#### createUserInput.py

This file creates the Widgets on the Jupyter Notebook using `ipywidgets` for entering information (cache lines, lines to output, block size, etc.) and running the tool. 

#### runPintool.py

This file parses the user inputs from the notebook Widgets, checks that the inputs are valid, and run the Pintool based on the given inputs. All necessary files to execute the Pintool can be found in the `/setup/` directory (see README on Setup Directory for more info).  
  
**Note** There are a few cases where the Pintool will not be able to run because `trace.hdf5` is already open in Vaex, and it cannot write to an open file. This will happen if the user open two notebooks at the same time, runs the tool again while `trace.hdf5` is already opened and/or plotted, or if they close, reopen, and replot the notebook without restarting the notebook Kernel. Deleting the `trace.hdf5` file will force Vaex to close the file and will allow the Pintool to recreate and open the file, and as of this moment, this is the simplest workaround for this problem while we handle this case in the Pintool itself.

#### generateGraph.py

This file will take the resulting output from the Pintool in runPintool.py (namely, `trace.hdf5` and `tag_map.csv`) and plot it with Vaex's `plot_widget` (only works on Jupyter Notebook). These files can be found in the `/setup/converter/outfiles` directory.  
  
`trace.hdf5` contains the memory accesses and type of accesses corresponding to each tag value.  
  
Each name in `tag_map.csv` will be mapped to the corresponding tag value, start and end indices, and start and end addesses. This information will be stored as a dictionary and used by the BqplotBackend to scale the axes of the plot_widget (see BqplotBackend README for more info).  
  
Each tag name to value mapping will also be used by the `ipywidgets` checkboxes to show and hide the points for each tag and each type of access. This is implemented using Vaex's `df.select` function. Note that `df.select` does NOT take in a boolean expression as its first argument. Instead, it takes in a Vaex Expression type that looks exactly like a boolean expression but are actually sections of the original dataframe/df based off the evaluation. The mode parameter will apply the corresponding (boolean-like) function to the current group of Expressions in the selection in the order of `df.select` calls (i.e. (A OR B OR C AND D) will apply as (((A OR B) OR C) AND D). To group selections and apply a function (like AND) to two groups of selections, you will need to name the two selections using the name parameter and do one more selection, passing in the first name as the first parameter and the second name as the name parameter.  
  
Other than the checkboxes, any other Widgets you see on the plot_widget are implemented within BqplotBackend (see BqplotBackend README for more info).

