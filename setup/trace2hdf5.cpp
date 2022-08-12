#include<fcntl.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include "H5Cpp.h" // Hdf5
#include<cassert>
#include "moneta_trace.hpp"

// Output Columns
const std::string IndexColumn {"index"};
const std::string AccessColumn  {"Access"};
const std::string AddressColumn {"Address"};
const std::string ThreadIDColumn {"ThreadID"};
const std::string LayerColumn{"Layer"};

/*
 * Use this to handle hdf with write_data_mem and write_data_cache
 */
class HandleHdf5 {
	static const unsigned long long int chunk_size = 200000; // Private vars
	unsigned long long addrs[chunk_size]; // Chunk local vars
	uint8_t accs[chunk_size];
	uint8_t threadids[chunk_size];
	u_long indexes[chunk_size];
	uint8_t layer[chunk_size];

	//unsigned long long cache_addrs[chunk_size]; // Chunk local vars - cache
	// Current access
	size_t mem_ind = 0;
	//size_t cache_ind = 0;
	size_t index = 0; // increment index of each access
	size_t layer_default = 1;
	// Memory accesses
	H5::H5File mem_file;
	//  H5::DataSet tag_d;
	H5::DataSet index_d;
	H5::DataSet acc_d;
	H5::DataSet addr_d;
	H5::DataSet threadid_d;
	H5::DataSet layer_d;
	// State vars
	hsize_t curr_chunk_dims [1] = {chunk_size};
	hsize_t total_ds_dims [1] = {chunk_size};
	hsize_t offset [1] = {0};


	// Open files, dataspace, and datasets
	void setup_files() {

		// Try catch block here highly recommended!!!
		//H5::Exception::dontPrint(); // Don't print exceptions - Let catch block do it
		hsize_t idims_t[1] = {1};   // Initial dims
		H5::DSetCreatPropList plist; // Set chunk size with property list
		plist.setChunk(1, curr_chunk_dims);
		hsize_t max_dims[1] = {H5S_UNLIMITED}; // For extendable dataset
		H5::DataSpace m_dataspace {1, idims_t, max_dims}; // Initial dataspace
		// Create and write datasets to file
		index_d = mem_file.createDataSet(IndexColumn.c_str(), H5::PredType::NATIVE_ULLONG, m_dataspace, plist);
		acc_d =      mem_file.createDataSet(AccessColumn.c_str(),   H5::PredType::NATIVE_UINT8, m_dataspace, plist);
		threadid_d = mem_file.createDataSet(ThreadIDColumn.c_str(), H5::PredType::NATIVE_UINT8, m_dataspace, plist);
		addr_d =     mem_file.createDataSet(AddressColumn.c_str(),  H5::PredType::NATIVE_ULLONG, m_dataspace, plist);
		layer_d = mem_file.createDataSet(LayerColumn.c_str(), H5::PredType::NATIVE_UINT8, m_dataspace, plist);

		//H5::DataSpace c_dataspace {1, idims_t, max_dims};
		//cache_d = cache_file.createDataSet(CacheAccessColumn.c_str(), H5::PredType::NATIVE_ULLONG, c_dataspace, plist);
	}

	// Extends dataset and writes stored chunk
	void extend_write_mem() {

		acc_d.extend( total_ds_dims ); // Extend size of dataset
		addr_d.extend( total_ds_dims );
		threadid_d.extend( total_ds_dims );
		index_d.extend(total_ds_dims);
		layer_d.extend(total_ds_dims);

		H5::DataSpace old_dataspace = acc_d.getSpace(); // Get old dataspace
		H5::DataSpace new_dataspace = {1, curr_chunk_dims}; // Get new dataspace
		old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims, offset); // Select slab in extended dataset
		acc_d.write( accs, H5::PredType::NATIVE_UINT8, new_dataspace, old_dataspace); // Write to extended part

		old_dataspace = addr_d.getSpace(); // Rinse and repeat for address
		old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims, offset);
		addr_d.write( addrs, H5::PredType::NATIVE_ULLONG, new_dataspace, old_dataspace);

		old_dataspace = threadid_d.getSpace(); // Rinse and repeat for threads
		old_dataspace.selectHyperslab(H5S_SELECT_SET, curr_chunk_dims, offset);
		threadid_d.write(threadids, H5::PredType::NATIVE_UINT8, new_dataspace, old_dataspace);

		old_dataspace = index_d.getSpace(); // Rinse and repeat for index
		old_dataspace.selectHyperslab(H5S_SELECT_SET, curr_chunk_dims, offset);
		index_d.write(indexes, H5::PredType::NATIVE_ULLONG, new_dataspace, old_dataspace);

		old_dataspace = layer_d.getSpace(); // Rinse and repeat for layer
		old_dataspace.selectHyperslab(H5S_SELECT_SET, curr_chunk_dims, offset);
		layer_d.write(layer, H5::PredType::NATIVE_UINT8, new_dataspace, old_dataspace);
	}

public:
	// Default constructor
	HandleHdf5() : mem_file({"trace.hdf5", H5F_ACC_TRUNC}) { setup_files(); }


	// With names
	HandleHdf5(std::string h) : mem_file({h.c_str(), H5F_ACC_TRUNC}) { setup_files(); }

	// Destructor
	~HandleHdf5() {
		if (mem_ind != 0) { // New data to write
			curr_chunk_dims[0] = mem_ind; // Not full chunk size
			total_ds_dims[0]  -= chunk_size - mem_ind;

			extend_write_mem();
		}

		mem_file.close();

	}

	// Write data for memory access to file
	int write_data_mem(uintptr_t address, uint8_t access, uint8_t threadid) {
		addrs[mem_ind] = address; // Write to memory first
		threadids[mem_ind] = (unsigned char)(threadid & 0xff);
		accs[mem_ind++] = access;
		index++;
		indexes[mem_ind] = index;
		layer[mem_ind] = layer_default;

		if (mem_ind < chunk_size) { // Unless we have reached chunk size
			return 0;
		}
		mem_ind = 0;

		extend_write_mem(); // Then, write to hdf5 file
      
		total_ds_dims[0] += chunk_size; // Update size and offset
		offset[0] += chunk_size;
		return 0;
	}
};

HandleHdf5 *hdf_handler;

int main(int argc, char *argv[]) {

	char * input_filename = argv[1];
	char * output_filename = argv[2];
	HandleHdf5 * hdf_handler = new HandleHdf5(output_filename);
	
	int input_file_df = open(input_filename, O_RDONLY);
	assert(input_file_df != -1);

	while(1) {
		struct trace_entry entry;
		int bytes_read = read(input_file_df, &entry, sizeof(entry));
		if (bytes_read != sizeof(entry)) {
			break;
		}
		hdf_handler->write_data_mem(entry.address, entry.acc, entry.threadid);
	}

	delete hdf_handler;

	return 0;
}
