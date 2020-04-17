#include <iostream>

/** Useful Info for HDF5 file creation
 *
 * https://support.hdfgroup.org/HDF5/doc/H5.intro.html
 *
 * Recall that H5T_NATIVE_INTs and dimensionality (dataspace) are independent objects, 
 * which are created separately from any dataset that they might be attached to. 
 * Because of this the creation of a dataset requires, at a minimum, 
 * separate definitions of H5T_NATIVE_INT, dimensionality, and dataset. 
 * Hence, to create a dataset the following steps need to be taken:
 *    1. Create and initialize a dataspace for the dataset to be written.
 *    2. Define the H5T_NATIVE_INT for the dataset to be written.
 *    3. Create and initialize the dataset itself.
*/


#include "hdf5_pin.h"



#define DATASETNAME "MemAccesses"
#define RANK 2 //num dimensions of dataset
#define NX 1 // num rows of each datachunk
#define NY 2 // num columns of the dataset
const H5std_string	FILE_NAME("h5tutr_dset.h5");
hid_t file, filespace;
hid_t dataset, dataspace;
hid_t cparms;
hsize_t offset[RANK];
herr_t status;

hsize_t	chunk_dims[RANK] = {NX, NY};
hsize_t dims[RANK] = {NX,NY}; // dataset dimensions for creation
long size = 0; // dataset dimensions for creation
//hsize_t size[RANK] = {NX,NY}; // dataset dimensions for creation
hsize_t maxdims[RANK] = {H5S_UNLIMITED, H5S_UNLIMITED}; //make dataset extendible


extern "C" void writeData(int addr, bool isWrite){
	
	int data[RANK] = {addr,(int) isWrite};
	
	dataspace = H5Screate_simple(RANK, dims, NULL); // create the dataspace
	
	//const char * name = reinterpret_cast<const char *>(size);
	std::string s = std::to_string(size);
	const char* name = s.c_str();
	dataset =  H5Dcreate(file, name, H5T_NATIVE_INT, dataspace, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
	
	// write the new data as the appropriate size in the correct spot in the file
	status = H5Dwrite(dataset, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, data);
	
	size++;


	
}

extern "C" void createFile(){
	
	// create .h5 file, pre-existing file is overwritten w/H5ACC_TRUNC flag
	file = H5Fcreate ("pin_out.h5", H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);	
	
}

extern "C" void closeFile(){

	H5Dclose(dataset);
	H5Sclose(dataspace);
	H5Fclose (file);

}

//int main(int argc, char *argv[]){}
