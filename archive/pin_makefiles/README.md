# Pin Modified Makefiles

To replace the corresponding files in PIN_ROOT/source/tools/Config/
  
## makefile.default.rules
The following lines are added under Line 166 of `makefile.default.rules` to include the C++ library for HDF5.
```
166: ###### Default build rules for tools ######
167:
168: TOOL_CXXFLAGS += -I/usr/include/hdf5/serial
169: TOOL_LPATHS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial
170: TOOL_LIBS += -lhdf5 -lhdf5_cpp
```

## makefile.unix.config

Fixes the external library compilation issue with Pin (Source: https://chunkaichang.com/tool/pin-notes/)

Modifies Line 343 as follows:
```
<     TOOL_CXXFLAGS_NOOPT += -DTARGET_IA32E -DHOST_IA32E -fPIC
---
>     TOOL_CXXFLAGS_NOOPT += -DTARGET_IA32E -DHOST_IA32E -fPIC -fabi-version=2 -D_GLIBCXX_USE_CXX11_ABI=0
```