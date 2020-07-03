# Notebook Documentation

Programmer documentation for developing the Jupyter Notebook, main.py, and how to use df.select.

## main.py

`main.py` contains all the code necessary to run the tool and can be run in the notebook using
```
%run main.py [-r] [-log]
```
**-r:** Refreshes all output whenever you generate or load a trace, otherwise the statements will continue to print one after the other  
**-log:** Prints logging statements for debugging purposes  

All the widgets for the UI are creating using
[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/ "ipywidgets Documentation"). Any Widgets on the plot itself, like the top bar, is added in the BqplotBackend instead, but also use ipywidgets along with 
[ipyvuetify](https://github.com/mariobuikhuizen/ipyvuetify "ipyvuetify Documentation").  
  
All the files that `main.py` generates using the Pintool can be found in the `/setup/converter/outfiles` directory. This is also where `main.py` looks for `.hdf5` files to populate the SelectMultiple box/widget and to load the selected traces.


## df.select Usage

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
