#include <string>
#include "/home/jovyan/work/hdf5-1.12.0/c++/src/H5Cpp.h"
using namespace H5;

//#include "hdf5_pin.h"


/*
#define DATASETNAME "MemAccesses"
#define RANK 1 //num dimensions of dataset
#define NX 200000 // num rows of each datachunk
//#define NX 12 // num rows of each datachunk
#define NY 1 // num columns of the dataset
//extern const H5std_string	FILE_NAME("h5tutr_dset.h5");
extern hid_t file, filespace;
extern hid_t dataset, dataspace;
extern hid_t bool_dataset;
extern hid_t b_filespace;
extern hid_t tag_dataset;
extern hid_t t_filespace;

extern hid_t cparms;
extern hid_t dtype;
extern hsize_t offset[RANK];
extern herr_t status;

extern hsize_t	chunk_dims[RANK];
extern hsize_t dims[RANK]; // dataset dimensions for creation
extern hsize_t size[RANK]; // dataset dimensions for creation
extern hsize_t maxdims[RANK]; //make dataset extendible

extern int numAccess;

extern unsigned long long addrs[NX];
extern bool writes[NX];
extern int tags[NX];
*/


extern "C" void writeData(unsigned long long addr, char isWrite, int tag);

extern "C" void flushData();
	

extern "C" int createFile(const char* h5FileName);

extern "C" void closeFile();

extern "C" void convert( const char* csvFileName, const char* h5FileName);



extern "C" void access_writeData(unsigned long long access);

extern "C" void access_flushData();

extern "C" int access_createFile(const char* h5FileName);

extern "C" void access_convert( const char* csvFileName, const char* h5FileName);