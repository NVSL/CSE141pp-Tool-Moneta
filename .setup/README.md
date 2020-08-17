# Setup

All the files used by the Dockerfile to set up the image

## bashrc_aliases
Bash aliases to shorten certain commands. These aliases are appended to the end of the `~/.bashrc` file by the Dockerfile during the creation of the image.

### Aliases

#### pin
```
${PIN_ROOT}/pin.sh -ifeellucky -injection child
```
The `-ifeellucky` and `-injection child` are required for `Pin 2.14` to run correctly on newer Linux kernels. For more information, visit the following link: https://chunkaichang.com/tool/pin-notes/

#### moneta
```
jupyter notebook --allow-root ~/work/moneta
```
This is the full command that starts a local Jupyter Notebook server for Moneta to run on. The notebook's base directory will be `~/work/moneta`, and any relative paths used in Moneta's input widgets will be relative to this directory. Note that Vaex only work on Jupyter Notebook and not Jupyter Labs.

## moneta_pintool.tar.gz

In order to get the HDF5 external library to compile with Pin, we had to downgrade to Pin 2.14 and modify the `makefile.default.rules` and `makefile.unix.config` files in the `PIN_ROOT/source/tools/Config/` directory (See https://chunkaichang.com/tool/pin-notes/). This tarball contains Pin 2.14 with the Makefiles already modified. The modified Makefiles can be found under `pin_makefiles` in the `archive` folder of the Github repositor, and  the specific changes to the Makefiles can be found in `docs/README_PINTOOL.md` under **Makefile Changes**.

## requirements.txt
A list of library requirements that are necessary for Moneta to run. These dependencies are installed by the Dockerfile during the creation of the image.

## trace_tool.cpp
Source code file for our custom Pintool to generate memory access data (in HDF5 format) and trace metadata (in CSV and TXT format). This program injects instrumentation code at runtime so we can analyze each memory access and write the corresponding access data to file.

## trace_tool.so
`trace_tool.cpp` compiled using Pin's Makefiles. This is the actual executable that Pin uses.