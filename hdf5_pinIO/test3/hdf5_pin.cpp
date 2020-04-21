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
hid_t dataset, memspace;
hid_t cparms;
hsize_t offset[RANK]={0,0};
herr_t status;

hsize_t	chunk_dims[RANK] = {NX, NY};
hsize_t dims[RANK] = {INT_MAX,NY}; // dataset dimensions for creation
//hsize_t dims[RANK] = {ULONG_MAX,NY}; // dataset dimensions for creation
long size = 0; // dataset dimensions for creation
hsize_t dataDim[RANK] = {NX,NY}; // dataset dimensions for creation
hsize_t maxdims[RANK] = {H5S_UNLIMITED, H5S_UNLIMITED}; //make dataset extendible


extern "C" void writeData(int addr, bool isWrite){
	
	int data[RANK] = {addr,(int) isWrite};
	 
	
	
	//const char * name = reinterpret_cast<const char *>(size);
	//std::string s = std::to_string(size);
	//const char* name = s.c_str();
	//dataset =  H5Dcreate(file, DATASETNAME, H5T_NATIVE_INT, dataspace, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
	// extend the size of the dataset for each memAccess
	
	//status = H5Dextend(dataset, size);
	
	 //create filespace the size of the data to be written, in the correct poistion
	 //filespace = H5Dget_space(dataset);
	 status = H5Sselect_hyperslab(filespace, H5S_SELECT_SET, offset, NULL, dataDim, NULL);
	
//	 status = H5Sselect_hyperslab(dataspace, H5S_SELECT_SET, NULL, NULL, dataDim, NULL);
	
	// create dataspace the size of data to be written
	
	// write the new data as the appropriate size in the correct spot in the file
	status = H5Dwrite(dataset, H5T_NATIVE_INT, memspace, filespace, H5P_DEFAULT, data);
//	status = H5Dwrite(dataset, H5T_NATIVE_INT, dataspace, filespace, H5P_DEFAULT, data);
	 
	offset[0]++;
	
	//size++;


	
}

extern "C" void createFile(){
	
	// create .h5 file, pre-existing file is overwritten w/H5ACC_TRUNC flag
	file = H5Fcreate ("pin_out.h5", H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);	
	
	filespace = H5Screate_simple(RANK, dims, NULL); // create the filespace
	//filespace = H5Screate_simple(RANK, dims, maxdims); // create the filespace
	
	//cparms = H5Pcreate(H5P_DATASET_CREATE);
	
	//status = H5Pset_chunk(cparms, RANK, chunk_dims);
	
	//dataset = H5Dcreate2(file, DATASETNAME, H5T_NATIVE_INT, filespace,H5P_DEFAULT, cparms, H5P_DEFAULT);
	dataset = H5Dcreate1(file, DATASETNAME, H5T_NATIVE_INT, filespace,H5P_DEFAULT);
	 memspace = H5Screate_simple(RANK, dataDim, NULL); // create the dataspace
	// write this data random data to create the dataset, for testing purposes
//	int data0[2] = {8,18};

//	status = H5Dextend(dataset, dims);

//	filespace = H5Dget_space(dataset);
//	offset[0] = 0;
//	offset[1] = 0;

//	status = H5Sselect_hyperslab(filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);

//	status = H5Dwrite(dataset, H5T_NATIVE_INT, dataspace, filespace, H5P_DEFAULT, data0);
	
}

extern "C" void closeFile(){

	H5Dclose(dataset);
	H5Sclose(memspace);
	H5Sclose(filespace);
	H5Fclose (file);

}

//int main(int argc, char *argv[]){}
