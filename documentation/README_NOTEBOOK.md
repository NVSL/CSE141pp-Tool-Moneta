# LinkedSelectors Documentation

Programmer documentation for developing the LinkedSelectors notebook and its necessary dependencies

## The py Files

LinkedSelectors makes use of 4 py files to execute the tool: imports.py, createUserInput.py, runPintool.py, and generateGraph.py. The Jupyter Notebook will run the scripts using `%run -i fileName.py`. The `-i` flag will allow the variables in the script to be accessed by the other scripts, rather than restricting the scope of the variables to the script it is declared in. Important notes about each of the files can be found below:

#### imports.py

Add any imports that are used multiple times here to reduce repetitive imports in each file.

#### createUserInput.py

The textbox and Button Widgets (as well as the checkboxes in `generateGraph.py`) are creating using
[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/ "ipywidgets Documentation"). Any Widgets on the plot itself, like the sidebar, is added in the BqplotBackend instead (see README on BqplotBackend for more info).

#### runPintool.py

All input parsing from the Widgets in `createUserInput.py` is done here. All neccessary files to execute the Pintool will be found in the `/setup` directory. (see README on Setup Directory for more info).  
  
**Note:** There are a few cases where the Pintool will not be able to run because `trace.hdf5` is already open in Vaex, and the Pintool cannot write to an open file: 

- Two notebooks are open at the same time and the user runs the tool again while `trace.hdf5` is already opened and/or plotted in a different notebook
- The user closes, reopens, and replots the notebook without restarting the Notebook kernel (This occured before but doesn't seem to be happening anymore, but will keep this here as a possibility in case the issue recurs)

Deleting the `trace.hdf5` file will force Vaex to close the file and will allow the Pintool to recreate and open the file, and as of this moment, this is the simplest workaround for this problem while we handle this case in the Pintool itself.

#### generateGraph.py

This file will take the resulting output from the Pintool in runPintool.py (namely, `trace.hdf5` and `tag_map.csv`) and plot it with Vaex's `plot_widget` (only works on Jupyter Notebook). These files will be found in the `/setup/converter/outfiles` directory by default.  
  
`trace.hdf5` contains the memory address accesses, type of accesses (read, write, hit, miss, etc.), and corresponding tag value.
  
Each tag/name in `tag_map.csv` will be mapped to the corresponding tag value, start and end indices, and start and end addesses. This information will be stored as a dictionary and used by the BqplotBackend to scale the axes of the plot\_widget (see BqplotBackend README for more info).  
  
Each tag name to value mapping will also be used by the 
[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/ "ipywidgets Documentation")
 checkboxes to show and hide the points for each tag and each type of access. This is implemented using Vaex's `df.select` function. 

##### df.select Usage

Documentation on `df.select` parameters and return values can be found 
[here](https://vaex.readthedocs.io/en/latest/api.html#vaex.dataframe.DataFrame.select "df.select Documentation"). We will go through usage more in depth here, since the Vaex documentation is not completely clear on how to use the parameters.  
  
The `boolean_expression` argument for `df.select` works a little differently from typical boolean expressions. When comparing columns and values for a dataframe as a boolean (i.e. `df.Tag == 1` for `df.select(df.Tag == 1)`), Vaex automatically generates a new type, Vaex Expression, based on the boolean. Because of this, although `df.Tag == 1` looks like a boolean, is actually of type Expression, which means that typical boolean operators (or, and, xor, etc.) will not work on Expressions. However, the `mode` and `name` parameters (both strings) of `df.select` will allow you to apply boolean operators to Expressions through Vaex.


###### Mode

`and`, `or`, and `xor` will work exactly the same as their boolean counterparts. `replace` overwrites any saved or existing Expressions with the newest `boolean_expression`. `subtract` removes the given `boolean_expression` from the current Expression list, or the saved Expression list of a `name` is given.

###### Name

The `name` parameter allows you to save an Expression to the provided string. When given a `boolean_expression`, `mode`, and `name`, `df.select` will apply `mode` to the `boolean_expression` and saved Expression(s). An example has been given below to clarify on this:

```
# 'current' stores nothing
df.select(df.Tag == 1, mode='replace', name='current')
# 'current' and stores '(df.Tag == 1)'
df.select(df.Tag == 2, mode='and', name='current')
#'current' now stores '(df.Tag == 1) and (df.Tag == 2)'

```

`df.select` has no precedence in `modes` and will apply the given `mode` operators in the order that `df.select` is called. In order to apply `mode` to groups of Expressions, you will need to store the Expressions in a `name` (you can think of `name` in this case as parentheses for the operators) and pass in the `name` string containing the final result into `df.select` as the `boolean_expression` without other parameters. An example has been given below to generate `(A or B) and (C or D)`:

```
df.select(df.value == A, mode='replace', name='first') # first == A
df.select(df.value == B, mode='or', name='first') # first = first or B = A or B
df.select(df.value == C, mode='replace', name='second') # second = C
df.select(df.value == D, mode='or', name='second') #second = second or D = C or D
df.select('first', mode='and', 'second') # second = first and second = (A or B) and (C or D)
df.select('second') # Show second

```
