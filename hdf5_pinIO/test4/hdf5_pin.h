
#include "/home/jovyan/work/hdf5-1.12.0/c++/src/H5Cpp.h"
using namespace H5;


extern "C" void writeData(unsigned long long addr, bool isWrite);

extern "C" void flushData();
	

extern "C" void createFile();

extern "C" void closeFile();

