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
#define RANK 1 //num dimensions of dataset
#define NX 200000 // num rows of each datachunk
//#define NX 12 // num rows of each datachunk
#define NY 1 // num columns of the dataset
const H5std_string	FILE_NAME("h5tutr_dset.h5");
hid_t file, filespace;
hid_t dataset, dataspace;
hid_t bool_dataset;
hid_t b_filespace;
hid_t tag_dataset;
hid_t t_filespace;

hid_t cparms;
hid_t dtype;
hsize_t offset[RANK] = {0};
herr_t status;

hsize_t	chunk_dims[RANK] = {NX};
hsize_t dims[RANK] = {NX}; // dataset dimensions for creation
hsize_t size[RANK] = {NX}; // dataset dimensions for creation
hsize_t maxdims[RANK] = {H5S_UNLIMITED}; //make dataset extendible

int numAccess = 0;

unsigned long long addrs[NX];
bool writes[NX];
int tags[NX];


extern "C" void writeData(unsigned long long addr, bool isWrite, int tag){
	

	addrs[numAccess] = addr;
	writes[numAccess] = isWrite;
    tags[numAccess] = tag;
	
	numAccess++;
	
	if(numAccess < NX){
		return;
	}
	
	numAccess = 0;	

	// extend the size of the dataset for each memAccess
	status = H5Dextend(dataset, size);
	status = H5Dextend(bool_dataset, size);
	status = H5Dextend(tag_dataset, size);

	
	// create filespace the size of the data to be written, in the correct poistion
	filespace = H5Dget_space(dataset);
	b_filespace = H5Dget_space(bool_dataset);
	t_filespace = H5Dget_space(tag_dataset);

	status = H5Sselect_hyperslab(filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);
	status = H5Sselect_hyperslab(b_filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);
	status = H5Sselect_hyperslab(t_filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);

	
	// create dataspace the size of data to be written
	dataspace = H5Screate_simple(RANK, dims, NULL); // create the dataspace

    // write the new data as the appropriate size in the correct spot in the file
	status = H5Dwrite(dataset, dtype, dataspace, filespace, H5P_DEFAULT, addrs);
	status = H5Dwrite(bool_dataset, H5T_NATIVE_CHAR, dataspace, b_filespace, H5P_DEFAULT, writes);
    status = H5Dwrite(tag_dataset, H5T_NATIVE_INT, dataspace, t_filespace, H5P_DEFAULT, tags);



	size[0]+= NX;
	offset[0]+=NX;

	
}

extern "C" void flushData(){
	if(numAccess == 0){
		return;
	}
	
	dims[0]=numAccess;
	size[0] -= (NX-numAccess);
	status = H5Dextend(dataset, size);
    status = H5Dextend(bool_dataset, size);
    status = H5Dextend(tag_dataset, size);

	
	// create filespace the size of the data to be written, in the correct poistion
	filespace = H5Dget_space(dataset);
	status = H5Sselect_hyperslab(filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);
    
	b_filespace = H5Dget_space(bool_dataset);
	status = H5Sselect_hyperslab(b_filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);

    t_filespace = H5Dget_space(tag_dataset);
	status = H5Sselect_hyperslab(t_filespace, H5S_SELECT_SET, offset, NULL, dims, NULL);

	
	// create dataspace the size of data to be written
	dataspace = H5Screate_simple(RANK, dims, NULL); // create the dataspace
	
	// write the new data as the appropriate size in the correct spot in the file
	status = H5Dwrite(dataset, dtype, dataspace, filespace, H5P_DEFAULT, addrs);
	status = H5Dwrite(bool_dataset, H5T_NATIVE_CHAR, dataspace, b_filespace, H5P_DEFAULT, writes);
    status = H5Dwrite(tag_dataset, H5T_NATIVE_INT, dataspace, t_filespace, H5P_DEFAULT, tags);



}
extern "C" void createFile(){
	
	// create .h5 file, pre-existing file is overwritten w/H5ACC_TRUNC flag
	file = H5Fcreate ("pin_out.h5", H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);	
	dtype = H5T_NATIVE_LLONG;
	
	dataspace = H5Screate_simple(RANK, dims, maxdims); // create the dataspace
	
	cparms = H5Pcreate(H5P_DATASET_CREATE);
	
	status = H5Pset_chunk(cparms, RANK, chunk_dims);
	
	dataset = H5Dcreate2(file, "ADDRESS", dtype, dataspace,H5P_DEFAULT, cparms, H5P_DEFAULT);
	bool_dataset = H5Dcreate2(file, "WRITE", H5T_NATIVE_CHAR, dataspace,H5P_DEFAULT, cparms, H5P_DEFAULT);
    tag_dataset = H5Dcreate2(file, "tag", H5T_NATIVE_INT, dataspace,H5P_DEFAULT, cparms, H5P_DEFAULT);
	
}

extern "C" void closeFile(){

	H5Dclose(dataset);
	H5Dclose(bool_dataset);
	H5Dclose(tag_dataset);

	H5Sclose(dataspace);
//	H5Sclose(filespace);
	H5Fclose (file);

}

//int main(int argc, char *argv[]){}
