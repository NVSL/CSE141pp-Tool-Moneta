# Developer Guide: Pin

Intel’s PIN allows a user to instrument a program to analyze many aspects of the execution. We are using a subset of PIN’s functionality in order to track memory accesses throughout a student’s executable. For more information about PIN with examples, visit [Intel's Pin Documentation](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/) for a User Guide. For the APIs used in the tool, visit [Modules](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/modules.html).

Our Pin files are located [here](https://github.com/NVSL/CSE141pp-Tool-Moneta-Pin).
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
> python .setup/compile_pin.py <PATH_TO_PINTOOL/pintool.cpp> [default: .setup/trace_tool.cpp]
> ls PIN_ROOT/source/tools/ManualExamples/obj-intel64/

pintool.so
```

## Running the Pintool

Usage: `pin [OPTION] [-t <tool> [<toolargs>]] -- <command line>`

where command line is the exact command to run the executable such as `./sort` or `./add 1 2`

### Values

Again, for our Docker image, `PIN_ROOT = /pin`.

**Pin executable:** `PIN_ROOT/pin.sh`

**Pin options:** `-ifeellucky -injection child` (See [**Usage**](https://github.com/NVSL/CSE141pp-Tool-Moneta-Pin))

**Pin tool:** `PATH_TO_TOOL/trace_tool.so` (Default: `/home/jovyan/work/.setup/trace_tool.so`)

### trace\_tool.so: toolargs

`-name, -n [string]`: Name of trace

`-output_lines, -ol [int]`: Maximum memory accesses to write to file

`-cache_lines, -c [int]`: Number of lines in the cache

`-block, -b [int]`: Block size of cache line

`-full, -f [0 / 1]`: Full trace

`-main, -m [0 / 1]`: Track main

#### Examples

Using these values and flags, a Pin execution command for `trace_tool.so` may look similar to the one below:
```
/pin/pin.sh -ifeellucky -injection child -t .setup/pintool.so -n sorting -ol 1000000 -c 4096 -b 64 -f 0 -m 0 -- ./moneta/Examples/sorting
```

Alternatively, if you are running from the Docker command line, you can use the `pin` alias from the `~/.bashrc` file:
```
pin -t .setup/pintool.so -n sorting -ol 1000000 -c 4096 -b 64 -f 0 -m 0 -- ./moneta/Examples/sorting
```

## Output Files

If Pin traces the program successfully, it will create the following files in Moneta's `.output` folder (Default: `/home/jovyan/work/moneta/.output`):

`[full_]trace_NAME.hdf5`: Table of rows containing memory address, access type (read, write x hit, capacity miss, compulsory miss), and time of access

`[full_]tag_map_NAME.csv`: Contains info for all traced tags. Tag name, lower and upper address bounds, first and last access

`[full_]meta_data_NAME.csv`: Contains information about the cache from the `-c` and `-b` flags

## Important Notes
 - In our Pintool, `trace_tool`, a fully associative cache is simulated and is used to determine if the memory access is a hit or a miss, as Pin cannot tell us if the access is a hit or miss in the system's real cache.
 - The PIN\_ROOT environment variable is set to the directory where Pin is installed. For our Docker image, `PIN_ROOT = /pin`.
 - Using the HDF5 file format is much more efficient than writing to a typical CSV file. Since we are writing large sets of data, efficiency is one of our top priorities. Not only is it faster to write to HDF5 files, it is also faster for Vaex to open HDF5 files. Using HDF5 and Vaex, we can open and process millions of lines of data in seconds. 


