# Developer Documentation

This directory contains useful information regarding the implementation of the followng aspects of Moneta:
 - Pin
 - Vaextended

## Table of Contents

   * [General Workflow:](#general-workflow)
   * [Developer Guide: Pin](#developer-guide-pin)
      * [Compiling the Pintool](#compiling-the-pintool)
      * [Running the Pintool](#running-the-pintool)
      * [Output Files](#output-files)
      * [Important Notes](#important-notes)
   * [Developer Guide: Vaextended](#developer-guide-vaextended)
      * [Table of Contents:](#table-of-contents)
      * [Using Vaextended](#using-vaextended)
      * [Modifying Vaex's Existing Backend](#modifying-vaexs-existing-backend)
      * [Other Notes](#other-notes)
         * [Vaex Inverted Navigation](#vaex-inverted-navigation)
         * [@extend_class Decorator](#extend_class-decorator)

## General Workflow:
1.	Student annotates their program with tag functions and tags data structures of interest
2.	Student compiles their program as an executable
3.	Student opens the Jupyter Notebook, sets values for Cache Lines, Block Size, Lines to Output, Working Directory, Executable Path, Name for Trace and Trace Everything
4.	Notebook runs our custom Pintool, `trace_tool.so`, on the executable and outputs all data in the form of an HDF5 file
5.	Vaex (Python library) opens the file and plots the data as an interactive widget. This widget is linked to our custom backend, which is located in the `vaextended` directory
6.	Student analyzes their program by interacting with the plot and selecting what type of accesses they want to examine and for which tags

# Developer Guide: Pin

Intels PIN allows a user to instrument a program to analyze many aspects of the execution. We are using a subset of PINs functionality in order to track memory accesses throughout a students executable. For more information about PIN with examples, visit [Intel's Pin Documentation](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/) for a User Guide. For the APIs used in the tool, visit [Modules](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/modules.html).

Our Pin files are located [here](https://github.com/NVSL/CSE141pp-Tool-Moneta-Pin). Check [Important Notes](https://github.com/NVSL/CSE141pp-Tool-Moneta/blob/docs_pin/docs/README_PIN.md#important-notes) if any step fails.
<hr>

## Compiling the Pintool

Running the makefile in the Pin directory compiles the pintool into a shared object file (.so)

```
> cd PIN_ROOT/source/tools/ManualExamples/
> cp PATH_TO_PINTOOL/pintool.cpp .
> make obj-intel64/pintool.so TARGET=intel64
> ls obj-intel64/

pintool.so
```
We wrapped this up in a script:

```
> python setup/compile_pin.py <PATH_TO_PINTOOL/pintool.cpp> [default: setup/trace_tool.cpp]
> ls PIN_ROOT/source/tools/ManualExamples/obj-intel64/

pintool.so
```

## Running the Pintool

Usage: `pin [OPTION] [-t <tool> [<toolargs>]] -- <command line>`

**Pin:** `PIN_ROOT/pin.sh`  
**[OPTION]:** `-ifeellucky -injection child` (See [**Usage**](https://github.com/NVSL/CSE141pp-Tool-Moneta-Pin#usage))  
**\<tool\>:** `PATH_TO_TOOL/trace_tool.so` (Default: `/PIN_ROOT/source/tools/ManualExamples/obj-intel64/trace_tool.so`)  
**\<toolargs\>:**  
- `-name, -n [string] [default: default]`: Name of trace  
- `-output_lines, -ol [int] [default: 10000000]`: Maximum memory accesses to write to file  
- `-cache_lines, -c [int] [default: 4096]`: Number of lines in the cache  
- `-block, -b [int] [default: 64]`: Block size of cache line in bytes  
- `-full, -f [0 / 1] [default: 0]`: Full trace  
- `-main, -m [0 / 1] [default: 0]`: Start trace at main 

**\<command line\>**: exact command to run the executable such as `./sort`, `./add 1 2`, or `/usr/bin/ls`

#### Examples
```
/pin/pin.sh -ifeellucky -injection child -t setup/trace_tool.so -n sorting -ol 1000000 -c 4096 -b 64 -f 0 -m 0 -- ./moneta/Examples/sorting
```
In the container, the `pin` alias from the `~/.bashrc` file condenses `/pin/pin.sh -ifeellucky -injection child`:
```
pin -t setup/trace_tool.so -n sorting -ol 1000000 -c 4096 -b 64 -f 0 -m 0 -- ./moneta/Examples/sorting
```

## Output Files
Located in Moneta's `.output` folder (Default: `/home/jovyan/work/moneta/.output`):
- `[full_]trace_NAME.hdf5`: Table of rows containing memory address (64-bit), access type ({read, write} x {hit, capacity miss, compulsory miss}), and time of access (seconds)
- `[full_]tag_map_NAME.csv`: Contains info for all traced tags. Tag name, lower and upper address bounds, first and last access
- `[full_]meta_data_NAME.txt`: Contains one line: [cache_lines] [block]

## Important Notes
 - In our Pintool, `trace_tool`, a fully associative cache is simulated and is used to determine if the memory access is a hit or a miss, as Pin cannot tell us if the access is a hit or miss in the system's real cache.
  - In order for Pin to compile using the Makefiles, the `PIN_ROOT` environment variable must be set to the directory where Pin is installed (contains the `pin.sh` file). Our Docker image sets `PIN_ROOT = /pin`.
   - Using the HDF5 file format is much more efficient than writing to a typical CSV file. Since we are writing large sets of data, efficiency is one of our top priorities. Not only is it faster to write to HDF5 files, it is also faster for Vaex to open HDF5 files. Using HDF5 and Vaex, we can open and process millions of lines of data in seconds. 

# Developer Guide: Vaextended

Adapted version of Vaex to allow local control over the backend (Default Path: `moneta/moneta/vaextended`);

**IMPORTANT:** Moneta currently uses the following versions of Vaex, as `plot_widget()` is deprecated in newer versions. These should be already specified in `setup/requirements.txt` [here](https://github.com/NVSL/CSE141pp-Tool-Moneta/blob/master/setup/requirements.txt#L40):
```
vaex-arrow: 0.4.2
vaex-astro 0.6.1
vaex-core: 1.5.0
vaex-hdf5: 0.5.6
vaex-jupyter: 0.4.1
vaex-server: 0.2.1
vaex-ui:  0.3.0
vaex-viz: 0.3.8
```

## Table of Contents:
 * [Using Vaextended](#using-vaextended)
 * [Modifying Vaex's Existing Backend](#modifying-vaexs-existing-backend)
    * [bqplot.py](#bqplotpy)
    * [plot.py](#plotpy)
    * [widgets.py](#widgetspy)
 * [Other Notes](#other-notes)
     * [Vaex Inverted Navigation](#vaex-inverted-navigation)
     * [@extend-class Decorator](#extend_class-decorator)

## Using Vaextended

Using `plot_widget()` with the Vaextended backend requires the following keyword arguments:
 - **backend:** Name referencing the backend to use
 - **type:** Name referencing the `PlotBase` class to use
 - **legend:** A Legend object from `moneta/moneta/legend.py`
 - **x_col:** The x-column name of the dataframe
 - **y_col:** The y-column name of the dataframe
 - **cache_size:** The cache size in bytes
 - **update_stats:** A callback function that updates "Current View Stats" in the Legend object
 - **limit:** The x and y limits in 2D array format (e.g. `[[x_min, x_max], [y_min, y_max]]`) 
    - Required because Vaex incorrectly calculates the y-limits, likely due to the memory addresses being so large in value. This causes the plot to crash from divide-by-zero, so we have to manually pass in the correct limits.


 The following keyword arguments are not required, but should be included as they improve navigation and visuals:
 - **colormap:** Colormap to use. The primary colormap Vaextended uses can be found in `moneta/moneta/settings.py` as `CUSTOM_CMAP`
 - **selection:** Passing in `[True]` allows turning on/off access types or tags via the Legend checkboxes
 - **what:** Determines how Vaex's binned data points should be mapped to the colormap and displayed. Vaextended uses `max(Access)`
 - **default_title:** Title of the plot, typically set to be the trace name (Default: "Moneta")
 - **x_label:** The plot's x-axis label (Default: "Access Number")
 - **y_label:** The plot's y-axis label (Default: "Address")

An example of using `plot_widget()` with Vaextended can be found below. For backend and type, we will use the names set in [**Modifying Vaex's Existing Backend**](#modifying-vaexs-existing-backend):

```python
# Assume this file has three columns: "index", "Address", and "Access"
df = vaex.open('some_trace.hdf5') 
x_min = df.index.min()
x_max = df.index.max()
y_min = df.Address.min()
y_max = df.Address.max()

plot = df.plot_widget(
            df['index'],
            df['Address'],
            what='max(Access)',
            colormap=CUSTOM_CMAP, 
            selection=[True], 
            limits=[[x_min, x_max], [y_min, y_max]],
            backend='moneta_backend', 
            type='vaextended', 
            legend=Legend(),
            default_title='Some Trace', 
            x_col='index', 
            y_col='Address', 
            x_label='Access Number', 
            y_label='Memory Address', 
            cache_size=16384,
            update_stats=function_that_updates_legend_current_view_stats
            )
```


## Modifying Vaex's Existing Backend

Vaex's original files are located in the `/opt/conda/lib/python3.7/site-packages/vaex` directory. We will refer to this directory as `VAEX_ROOT` for brevity. 

Making changes to Vaex's backend mainly requires us to override Vaex's classes and/or files with our own modified versions. As a general guide, look through the source code in `VAEX_ROOT` (Tip: Use `grep -nri`) to see which files you want to change and where the target classes are initialized. Then, make a copy of the file/class and make any changes within the preexisting functions. Since this is an exact copy of the original Vaex file, Vaex still uses/calls the same classes, variables, and functions, so any missing attributes will likely cause Vaex to crash entirely, and any new attributes can only be used/called by preexisting function. Once the modifications are made, override the files/classes accordingly by replacing the value of the Vaex import with your custom backend import.

Basic Example (Examples specific to Vaextended can be found in the below sections):
```
import vaex.original
import vaextended.modified.plot
vaex.original.plot = vaextended.modified.plot
vaex.original.dictionary['new_key'] = vaextended.modified.new_value
```

For Vaextended, we modified 3 of Vaex's files: `bqplot.py`, `plot.py`, and `widgets.py`.

### bqplot.py

Add or modify backends in the following way (([Source](https://github.com/NVSL/CSE141pp-Tool-Moneta/blob/master/moneta/moneta/view.py#L16))):

```python
import vaex.jupyter.plot
vaex.jupyter.plot.backends['moneta_backend'] = ("vaextended.bqplot", "BqplotBackend")
```

This will create a new backend called `moneta_backend` based off the `BqplotBackend` class in `moneta/moneta/vaextended/bqplot.py` instead of the original `BqplotBackend` in  `VAEX_ROOT/jupyter/bqplot.py`. To use the modified `BqplotBackend`, pass `backend='moneta_backend'` into `plot_widget()`.

### plot.py

In order to expand on aspects the plot itself, such as saving metadata (i.e. x/y labels, cache size) and increasing plot point size, we need to change the `PlotBase` class in `plot.py`. To use our modified `PlotBase` instead of Vaex's original `PlotBase` in `VAEX_ROOT/jupyter/plot.py`, we need to include the following code in `moneta/moneta/vaextended/__init__.py` ([Source](https://github.com/NVSL/CSE141pp-Tool-Moneta/blob/master/moneta/moneta/vaextended/__init__.py#L3)):

```python
from vaextended.plot import PlotBase
vaex.jupyter.plot.type_map['vaextended'] = PlotBase
```
To use the modified `PlotBase`, pass `type='vaextended'` into `plot_widget()`. 

**Note:** The `PlotBase` object is what `plot_widget()` returns.


### widgets.py

The `PlotTemplate` class in `widgets.py` contains a base widget for the plot. This includes the top nav bar (title, pan/zoom, etc.), legend, and the plot itself. To use this modified `PlotTemplate`, we need to add the following import to `plot.py` to override the original `PlotTemplate` class ([Source](https://github.com/NVSL/CSE141pp-Tool-Moneta/blob/master/moneta/moneta/vaextended/plot.py#L6)).

```python
from vaextended.widgets import PlotTemplate
```


## Other Notes

### Vaex Inverted Navigation

The default installation of Vaex has a bug where `plot_widget()` has it's vertical navigation inverted. We have fixed this bug in `moneta/moneta/vaextended/plot.py` in by rotating the plot in `_update_image()` ([Source](https://github.com/NVSL/CSE141pp-Tool-Moneta/blob/master/moneta/moneta/vaextended/plot.py#L303)):
```diff
+ I = np.rot90(color_grid).copy()
self.backend.update_image(I)
```


### `@extend_class` Decorator

**Note:** This is a legacy feature not being used in the current iteration of Vaextended. To add or modify additional functions, simply make those changes in the corresponding file in the `vaextended` directory.

The decorator is located in `moneta/moneta/vaextended/utils.py`. To add, override, and/or modify features in the `BqplotBackend` class, use the following format:

```python
@extend_class(BqplotBackend)
def method_name(method_args):
    # body of method
```
