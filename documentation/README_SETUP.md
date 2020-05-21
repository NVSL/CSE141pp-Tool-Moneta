# Setup/Vaex\_Extended Directory Information

There are 2 setup directories that are of importance: the root directory `/setup/` and the relative directory `../Setup/`. Likewise, there are
3 vaex\_extended directories of importance: `/setup/vaex-extended`, `../Setup/vaex_extended_setup`, and `../vaex_extended`. Note that the default current directory will be the `~/work/memorytrace` directory.

### ../Setup vs  /setup/

The `../Setup` directory will contain all the files necessary when building the Docker image. Most of these files will be copied over to the `/setup/` direc
tory when building the image. The `../Setup/` directory should contain the following files and subdirectories:


```
pin_makefile.default.rules
pin_makefile.unix.config
requirements.txt
trace_tool.cpp
trace_tool.so
vaex_extended_setup

```

##### pin\_makefile.default.rules, pin\_makefile.unix.config

Our Pintool uses an external HDF5 library to write the memory accesses directly into a .hdf5 formatted file. These two makefiles will overwrite the existing
 makefiles for the Pintool when it is installed by the Dockerfile so that our custom Pintool can be compiled.

##### requirements.txt

This file contains all the necessary libraries and dependencies to `pip install` for our tool to work.

##### trace\_tool.cpp, trace\_tool.so

`trace_tool.cpp` is the source code for our Pintool and `trace_tool.so` is the executable that is created when `trace_tool.cpp` is compiled using Pin's make
file. The `trace_tool.so` file in the `../Setup` directory should be up to date with the source code. Whenever changes are made to the source file, a new ex
ecutable should also be created in this directory.  
  
  
Once the Docker image is built, you should see the following files in the root `/setup/` directory:
```
converter
converter/outfiles
converter/trace_tool.so
pintool
requirements.txt
vaex_extended
```

The files in this directory (not including requirements.txt) will be used by the Jupyter Notebook to run various parts of the memory trace tool. These files
 are placed in the root directory to provide an absolute path to the Notebook

##### converter, converter/outfiles, converter/trace\_tool.so

`runPintool.py` will use the `trace_tool.so` file in this directory to run the Pintool and will output all files created by the Pintool to the `converter/ou
tfiles` directory.

##### pintool

This directory contains all the Pin source files and the main executable to run the Pin program itself.

### /setup/vaex\_extended vs ../vaex\_extended vs ../Setup/vaex\_extended
These directories contain all the files to create our modified bqplot backend. We will do our backend development in the  `../vaex_extended` directory. Whenever features are finalized and/or fully developed, we will add these changes to `../Setup/vaex_extended_setup`. Once the files are in the `../Setup` directory, the Dockerfile will now copy `../Setup/vaex_extended_setup` to `/setup/vaex_extended`, and the Notebook refer to `/setup/vaex_extended` when it plots using bqplot.  
  
**Note:**  You will see a line at the top of `generateGraph.py` that looks like one of the following:

```
sys.path.append('../')
sys.path.append('/setup/')
```

These two lines tell the Notebook where to look to find the files for BqplotBackend. For development (i.e. when working in the dev branch), since the changes are made in the `../vaex_extended` directory, we will need to direct the Notebook's path to `../` so it can find the current changes in the `vaex_extended` folder. However, for student use (i.e. when pushing to the master branch), we will need to change the path to `/setup/`, since the `vaex_extended` directory with the most recent finalized changes will be found there.
