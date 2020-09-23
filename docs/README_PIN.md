# Developer Guide: Pin

Intel’s PIN allows a user to instrument a program to analyze many aspects of the execution. We are using a subset of PIN’s functionality in order to track memory accesses throughout a student’s executable. For more information about PIN, visit [Intel's Pin Documentation](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/) for a User Guide.


## Important Notes
 - In our Pintool, `trace_tool`, a fully associative cache is simulated and is used to determine if the memory access is a hit or a miss, as Pin cannot tell us if the access is a hit or miss in the system's real cache.

 - The PIN\_ROOT environment variable is set to the directory where Pin is installed. For our Docker image, `PIN_ROOT = /pin`.

## <a name="issues"></a> Issues with External Libraries

**IMPORTANT:** We are using Pin 2.14, an older version of Pin, so we can link the necessary libraries to write to HDF5 files via our tool. The newest version ( Pin 3.2 ) makes it very difficult to compile other libraries with the tool. For our purposes, the two versions of Pin are functionally the same, since we only use a small subset of Pin's features. More information about the compilation issue can be found here:

https://chunkaichang.com/tool/pin-notes/

### Command Line Execution

To run the Pintool, we need to add the following two flags as `<pin options>`. From [Intel's Pin 2.14 Documentation Page](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/):

```
<Pin executable> <pin options> -t <Pin tool> <Other Pin tool options> -- <Test application> <Test application options>
```

These flags allow Pin 2.14 to run on newer Linux kernels, like the one our Docker image is built on.

### Makefile Changes

The modified Makefiles can be found in the `archive/pin_makefiles` directory of the GitHub repository. The modified Makefiles are pre-bundled into `moneta_pintool.tar.gz`, which is used to install Pin when building the Docker image.

#### makefile.default.rules
The following lines are added under Line 166 of `makefile.default.rules` to include the C++ library for HDF5.
```
166: ###### Default build rules for tools ######
167:
168: TOOL_CXXFLAGS += -I/usr/include/hdf5/serial
169: TOOL_LPATHS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial
170: TOOL_LIBS += -lhdf5 -lhdf5_cpp
```

#### makefile.unix.config

Fixes the external library compilation issue with Pin

Modifies Line 343 as follows:
```
<     TOOL_CXXFLAGS_NOOPT += -DTARGET_IA32E -DHOST_IA32E -fPIC
---
>     TOOL_CXXFLAGS_NOOPT += -DTARGET_IA32E -DHOST_IA32E -fPIC -fabi-version=2 -D_GLIBCXX_USE_CXX11_ABI=0
```


## Compiling the Pintool

The `.setup` directory contains a Python script, `compile_pin.py`, that you can run to compile the pintool. This script does exactly what we would do if we were to manually compile the pintool. Usage information is as follows:

```
python compile_pin.py <PATH TO PINTOOL SOURCE FILE> <OUTPUT DIRECTORY>
```

To manually compile the pintool, follow the steps listed below:

1. Navigate to the `ManualExamples` in Pin's directory
```
cd PIN_ROOT/source/tools/ManualExamples/
```
2. Copy the pintool to the `Manual Examples` directory (the current directory)
```
cp PATH_TO_PINTOOL/TOOL_NAME.cpp .
```
3. Compile using Pin's Makefiles. The output file will be located in the `obj-intel64/` directory.
```
make obj-intel64/TOOL_NAME.so TARGET=intel64
```
4. Copy the pintool `.so` file into the `.setup` folder (This is where the Python scripts in the `moneta` directory looks for the `.so` files)
```
cp obj-intel64/TOOL_NAME.so ~/work/setup
```

## Running the Pintool

From [Intel's Pin 2.14 Documentation Page](https://software.intel.com/sites/landingpage/pintool/docs/71313/Pin/html/) the general format for running the a pintool is as follows:

```
<Pin executable> <pin options> -t <Pin tool> <Other Pin tool options> -- <Test application> <Test application options>
```

### Values

Again, for our Docker image, `PIN_ROOT = /pin`.

**Pin executable:** `PIN_ROOT/pin.sh`

**Pin options:** `-ifeellucky -injection child` (See [**Issues with External Libraries**](#issues))

**Pin tool:** `PATH_TO_TOOL/trace_tool.so` (Default: `/home/jovyan/work/setup/trace_tool.so`)

### trace\_tool.so: Pin Tool Options

`-o [string]`: Name of trace

`-m [int]`: Maximum memory accesses to write to file

`-c [int]`: Number of lines in the cache

`-l [int]`: Block size of cache line

`-f [0 / 1]`: Full trace

Using these values and flags, a Pin execution command for `trace_tool.so` may look similar to the one below:
```
/pin/pin.sh -ifeellucky -injection child -t ~/work/setup/pintool.so -c 4096 -m 1000000 -l 64 -o sorting -f 0 -- ~/work/moneta/examples/sorting
```

Alternatively, if you are running from the Docker command line, you can use the `pin` alias in the `~/.bashrc` file:
```
pin -t ~/work/setup/pintool.so -c 4096 -m 1000000 -l 64 -o sorting -f 0 -- ~/work/moneta/examples/sorting
```

## Output Files

If Pin traces the program successfully, it will create the following files in Moneta's `.output` folder (Default: `/home/jovyan/work/moneta/output`):

`[full_]trace_NAME.hdf5`: Contains the program's memory accesses, corresponding tag ID, and corresponding access type (read, write, hit, capacity miss, compulsory miss)

`[full_]tag_map_NAME.csv`: Contains all tag information specified by the `pin_tags.h` functions, such as tag name, tag ID, and lower and upper memory address bounds 

`[full_]meta_data_NAME.csv`: Contains information about the cache from the `-c` and `-l` flags

### HDF5:

Using the HDF5 file format is much more efficient than writing to a typical CSV file. Since we are writing large sets of data, efficiency is one of our top priorities. Not only is it faster to write to HDF5 files, it is also faster for Vaex to open HDF5 files. Using HDF5 and Vaex, we can open and process millions of lines of data in seconds. 


## Important Pin Functions

### PIN\_InitSymbols(), PIN\_Init()

Must be called prior to `PIN_StartProgram()` in order for Pin to be able to read symbols and verify the arguments passed to the pintool are valid

### IMG\_AddInstrumentFunction(), INS\_AddInstrumentFunction()

Specifies a function to be called for each [Image](https://software.intel.com/sites/landingpage/pintool/docs/81205/Pin/html/group__IMG__BASIC__API.html) and [Instruction](https://software.intel.com/sites/landingpage/pintool/docs/81205/Pin/html/group__INS__BASIC__API.html) respectively

### PIN\_AddFiniFunction() 

Specifies a function to be run right before the pintool finishes execution (typically right after the traced program is done executing).



