# Developer Guide: Pin

Intel’s PIN allows a user to instrument a program to analyze many aspects of the execution. We are using a subset of PIN’s functionality in order to track memory accesses throughout a student’s executable. For more information about PIN with examples, visit [Intel's Pin Documentation](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/) for a User Guide. For the APIs used in the tool, visit [Modules](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/modules.html).

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
> python .setup/compile_pin.py <PATH_TO_PINTOOL/pintool.cpp> [default: .setup/trace_tool.cpp]
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
/pin/pin.sh -ifeellucky -injection child -t .setup/trace_tool.so -n sorting -ol 1000000 -c 4096 -b 64 -f 0 -m 0 -- ./moneta/Examples/sorting
```
In the container, the `pin` alias from the `~/.bashrc` file condenses `/pin/pin.sh -ifeellucky -injection child`:
```
pin -t .setup/trace_tool.so -n sorting -ol 1000000 -c 4096 -b 64 -f 0 -m 0 -- ./moneta/Examples/sorting
```

## Output Files
Located in Moneta's `.output` folder (Default: `/home/jovyan/work/moneta/.output`):
- `[full_]trace_NAME.hdf5`: Table of rows containing memory address, access type ({read, write} x {hit, capacity miss, compulsory miss}), and time of access (seconds)
- `[full_]tag_map_NAME.csv`: Contains info for all traced tags. Tag name, lower and upper address bounds, first and last access
- `[full_]meta_data_NAME.txt`: Contains one line: [cache_lines] [block]

## Important Notes
 - In our Pintool, `trace_tool`, a fully associative cache is simulated and is used to determine if the memory access is a hit or a miss, as Pin cannot tell us if the access is a hit or miss in the system's real cache.
 - In order for Pin to compile using the Makefiles, the `PIN_ROOT` environment variable must be set to the directory where Pin is installed (contains the `pin.sh` file). Our Docker image sets `PIN_ROOT = /pin`.
 - Using the HDF5 file format is much more efficient than writing to a typical CSV file. Since we are writing large sets of data, efficiency is one of our top priorities. Not only is it faster to write to HDF5 files, it is also faster for Vaex to open HDF5 files. Using HDF5 and Vaex, we can open and process millions of lines of data in seconds. 
