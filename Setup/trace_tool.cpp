#include <iostream>
#include <fstream>
#include <iomanip>
#include <string.h>
#include <utility>
#include <vector>
#include <list>
#include <set>
#include <unordered_set>
#include <unordered_map>
#include <assert.h>

#include "pin.H"   // Pin
#include "H5Cpp.h" // Hdf5

#define DUMP_MACRO_BEG "DUMP_ACCESS_START_TAG"
#define DUMP_MACRO_END "DUMP_ACCESS_STOP_TAG"
#define SET_MAX_OUTPUT "SET_MAX_OUTPUT"

#define DEBUG 0
#define EXTRA_DEBUG 0
#define INPUT_DEBUG 0
#define HDF_DEBUG 0
#define CACHE_DEBUG 0
// Use larger buffer
#define BUFFERED 1
// If addr overlaps multiple ranges, whether to record only one
#define RECORD_ONCE 0

using std::ofstream;
using std::string;
using std::hex;
using std::setw;
using std::cerr;
using std::dec;
using std::endl;
using std::vector;
using std::pair;

// Pin comes with some old standard libraries.
namespace pintool {
template <typename V>
using unordered_set = std::unordered_set<V>;

template <typename K, typename V>
using unordered_map = std::unordered_map<K, V>;
}

// Constant Vars
const ADDRINT DefaultMaxLines = 100000000;
const ADDRINT L1CacheEntries = 4096;
const ADDRINT DefaultCacheLineSize = 64;
const std::string DefaultPath = "./";

ofstream map_file;

// More debug vars
static int read_insts = 0;
// Cache debug
static int cache_writes = 0;
static int first_record = 0;
static int comp_misses = 0;
static int cap_misses = 0;
static int skip_rate = 100;


static int analysis_num_dump_calls = 0;
static bool analysis_dump_on = false;

static UINT64 max_lines = DefaultMaxLines;
static UINT64 cache_size = L1CacheEntries;
static UINT64 cache_line = DefaultCacheLineSize;
static UINT64 curr_lines = 0; // Increment for every write to hdf5 for memory accesses
static std::string output_path = DefaultPath;

// Increment id every time DUMP_ACCESS is called
static int curr_id = 0;

// tag_to_id used only for dump_access_begin/end
// Only the id is output to out_file.
// id_to_tag is output to out_file
typedef pair<ADDRINT, ADDRINT> AddressRange; 
pintool::unordered_map<int, AddressRange> active_ranges; // Original ranges - Suggestions for refactoring - coalesce maps to id -> class mapping
pintool::unordered_map<int, AddressRange> all_ranges; // Save the ranges whereas active_ranges deletes them
pintool::unordered_map<int, ADDRINT> range_offsets; // To normalize on top of each other
pintool::unordered_map<ADDRINT, ADDRINT> stack_map;  // For all values outside active_ranges but inside macros
pintool::unordered_map<string, int> tag_to_id; // String tag to id
pintool::unordered_map<int, string> id_to_tag; // Id to string tag
pintool::unordered_map<int, pair<int, int>> x_range; // First and last access

static ADDRINT free_block = 0; // State for normalized accesses
static ADDRINT free_stack_start = ULLONG_MAX - ULLONG_MAX%DefaultCacheLineSize - DefaultCacheLineSize;
static ADDRINT free_stack = free_stack_start;

static ADDRINT max_range = 0;

// Crudely simulate L1 cache (first n unique accesses between DUMP_ACCESS blocks)

/*
 * Hdf
 */

// Output Columns
const string TagColumn {"Tag"};
const string AddressColumn {"Address"};
const string AccessColumn {"Access"};
const string CacheAccessColumn {"CacheAccess"};

/*
 * Use this to handle hdf with write_data_mem and write_data_cache
 */
class HandleHdf5 {
  static const unsigned long long int chunk_size = 200000; // Private vars
  unsigned long long addrs[chunk_size]; // Chunk local vars
  uint8_t accs[chunk_size];
  int tags[chunk_size];

  unsigned long long cache_addrs[chunk_size]; // Chunk local vars - cache
  // Current access
  size_t mem_ind = 0;
  size_t cache_ind = 0;

  // Memory accesses
  H5::H5File mem_file;
  H5::DataSet tag_d;
  H5::DataSet acc_d;
  H5::DataSet addr_d;
    // State vars
  hsize_t curr_chunk_dims [1] = {chunk_size};
  hsize_t total_ds_dims [1] = {chunk_size};
  hsize_t offset [1] = {0};

  // Cache accesses
  H5::H5File cache_file;
  H5::DataSet cache_d;
    // State vars
  hsize_t curr_chunk_dims_c [1] = {chunk_size};
  hsize_t total_ds_dims_c [1] = {chunk_size};
  hsize_t offset_c [1] = {0};

  // Open files, dataspace, and datasets
  void setup_files() {
    if (HDF_DEBUG) {
      cerr << "Setting up hdf5 files\n";
    }
    // Try catch block here highly recommended!!!
    //H5::Exception::dontPrint(); // Don't print exceptions - Let catch block do it
    hsize_t idims_t[1] = {1};   // Initial dims
    H5::DSetCreatPropList plist; // Set chunk size with property list
    plist.setChunk(1, curr_chunk_dims);
    hsize_t max_dims[1] = {H5S_UNLIMITED}; // For extendable dataset
    H5::DataSpace m_dataspace {1, idims_t, max_dims}; // Initial dataspace
    // Create and write datasets to file
    tag_d = mem_file.createDataSet(TagColumn.c_str(), H5::PredType::NATIVE_INT, m_dataspace, plist);
    acc_d = mem_file.createDataSet(AccessColumn.c_str(), H5::PredType::NATIVE_UINT8, m_dataspace, plist);
    addr_d = mem_file.createDataSet(AddressColumn.c_str(), H5::PredType::NATIVE_ULLONG, m_dataspace, plist);

    H5::DataSpace c_dataspace {1, idims_t, max_dims};
    cache_d = cache_file.createDataSet(CacheAccessColumn.c_str(), H5::PredType::NATIVE_ULLONG, c_dataspace, plist);
  }

  // Extends dataset and writes stored chunk
  void extend_write_mem() {
    if (HDF_DEBUG) {
      cerr << "Extending and writing dataset for memory accesses\n";
    }
    tag_d.extend( total_ds_dims ); // Extend size of dataset
    acc_d.extend( total_ds_dims );
    addr_d.extend( total_ds_dims );

    H5::DataSpace old_dataspace = tag_d.getSpace(); // Get old dataspace
    H5::DataSpace new_dataspace = {1, curr_chunk_dims}; // Get new dataspace
    old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims, offset); // Select slab in extended dataset
    tag_d.write( tags, H5::PredType::NATIVE_INT, new_dataspace, old_dataspace); // Write to the extended part

    old_dataspace = acc_d.getSpace(); // Rinse and repeat
    old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims, offset);
    acc_d.write( accs, H5::PredType::NATIVE_UINT8, new_dataspace, old_dataspace);

    old_dataspace = addr_d.getSpace();
    old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims, offset);
    addr_d.write( addrs, H5::PredType::NATIVE_ULLONG, new_dataspace, old_dataspace);
  }

  // Extends dataset and writes stored chunk
  void extend_write_cache() {
    if (HDF_DEBUG) {
      cerr << "Extending and writing dataset for cache\n";
    }
    cache_d.extend( total_ds_dims_c ); // Extend
    H5::DataSpace old_dataspace = cache_d.getSpace(); // Get old dataspace
    H5::DataSpace new_dataspace = {1, curr_chunk_dims_c}; // Get new dataspace
    old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims_c, offset_c); // Select slab in extended dataset
    cache_d.write( cache_addrs, H5::PredType::NATIVE_ULLONG, new_dataspace, old_dataspace); // Write to the extended part
  }
  

public:
  // Default constructor
  HandleHdf5() : mem_file({"trace.hdf5", H5F_ACC_TRUNC}),
                 cache_file({"cache.hdf5", H5F_ACC_TRUNC}) { setup_files(); }
  // With names
  HandleHdf5(string h, string c) : 
	         mem_file({h.c_str(), H5F_ACC_TRUNC}),
                 cache_file({c.c_str(), H5F_ACC_TRUNC}) { setup_files(); }
  // Destructor
  ~HandleHdf5() {
    if (HDF_DEBUG) {
      cerr << "Hdf5 Destructor\n";
    }
    if (mem_ind != 0) { // New data to write
      curr_chunk_dims[0] = mem_ind; // Not full chunk size
      total_ds_dims[0]  -= chunk_size - mem_ind;

      extend_write_mem();
    }

    if (cache_ind != 0) {
      curr_chunk_dims_c[0] = cache_ind;
      total_ds_dims_c[0] -= chunk_size - cache_ind;

      extend_write_cache();
    }

    // Close files
    mem_file.close();
    cache_file.close();

  }

  // Write data for memory access to file
  int write_data_mem(int tag, int access, ADDRINT address) {
    if (HDF_DEBUG) {
      cerr << "Write to Hdf5 - memory\n";
    }
    tags[mem_ind] = tag; // Write to memory first
    accs[mem_ind] = access;
    addrs[mem_ind++] = address;
    if (mem_ind < chunk_size) { // Unless we have reached chunk size
      return 0;
    }
    mem_ind = 0;

    extend_write_mem(); // Then, write to hdf5 file
      
    total_ds_dims[0] += chunk_size; // Update size and offset
    offset[0] += chunk_size;
    /*try { // Should add this error checking somwhere
    } catch( H5::FileIException error ) {
      error.printError(); // Add custom messages here?
      return -1; // Exit program?
    } catch( H5::DataSetIException error ) {// catch failure caused by the DataSet operations
      error.printError();
      return -1;
    } catch( H5::DataSpaceIException error ) {// catch failure caused by the DataSpace operations
      error.printError();
      return -1;
    } catch( H5::DataTypeIException error ) {// catch failure caused by the DataType operations
      error.printError();
      return -1;
    }*/
    return 0;
  }

  // Write data for cache access to file
  int write_data_cache(ADDRINT address) {
    if (HDF_DEBUG) {
      cerr << "Write to Hdf5 - cache\n";
    }
    cache_addrs[cache_ind++] = address;
    if (cache_ind < chunk_size) { 
      return 0;
    }
    cache_ind = 0;

    extend_write_cache();
    total_ds_dims_c[0] += chunk_size;
    offset_c[0] += chunk_size;
    return 0;
  }

};



HandleHdf5 *hdf_handler;





struct cache_hash {
	inline std::size_t operator()(const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k) const {
		return (uint64_t)k.first;
	}
};

struct cache_equal {
public:
	inline bool operator()(const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k1, const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k2) const {
 
		if (k1.first == k2.first)
			return true;
		return false;
	}
};


/*struct cache_compare {
    inline bool operator() (const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k1, const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k2) const {
        return k1.first < k2.first;
    }
};*/


std::unordered_set<std::pair<ADDRINT, std::list<ADDRINT>::iterator>, cache_hash, cache_equal> accesses;
std::unordered_set<ADDRINT> all_accesses;
//std::set<std::pair<ADDRINT, std::list<ADDRINT>::iterator>, cache_compare> accesses;
std::list<ADDRINT> inorder_acc;

// Increase the file write buffer to speed up i/o
const unsigned long long BUF_SIZE = 4ULL * 8ULL* 1024ULL * 1024ULL;
static char * buffer1 = new char[BUF_SIZE];
static char * buffer2 = new char[BUF_SIZE];
static char * buffer3 = new char[BUF_SIZE];

// Extensions:
// -----------
// Add config options for:
// - Set L1 cache size
// - Set maximum line limit

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "./", "specify output file directory with an absolute path");

KNOB<UINT64> KnobMaxOutput(KNOB_MODE_WRITEONCE, "pintool",
    "m", "0", "specify max lines of output");

KNOB<UINT64> KnobCacheSize(KNOB_MODE_WRITEONCE, "pintool",
    "c", "0", "specify entries in L1 cache");

KNOB<UINT64> KnobCacheLineSize(KNOB_MODE_WRITEONCE, "pintool",
    "l", "0", "specify size of cache line for L1 cache");

// TODO make a config option?
VOID set_max_output_called(UINT64 new_max_lines) {
  max_lines = new_max_lines;
  // If reached file size limit, exit
  if(curr_lines >= max_lines) {
    PIN_ExitApplication(0);
  }
}

VOID dump_beg_called(VOID * tag, ADDRINT begin, ADDRINT end) {
  char* s = (char *)tag;
  string str_tag (s);

  if (DEBUG) {
    cerr << "Dump begin called - " << begin << ", " << end << " TAG: " << str_tag << "\n";
  }

  int id;
  if (tag_to_id.find(str_tag) == tag_to_id.end()) { // New tag
    if (DEBUG) {
      cerr << "Dump begin called - New tag Tag: " << str_tag << "\n";
      cerr << "Range: " << begin << ", " << end << "\n";
    }

    id = curr_id++;
    tag_to_id[str_tag] = id;
    id_to_tag[id] = str_tag;


    range_offsets[id] = begin - free_block;
    free_block+= end-begin;
    free_block+= cache_line - free_block%cache_line; // Move to next cache_line for each new tag

    max_range = std::max(max_range, free_block);

    if (DEBUG) {
      cerr << "Free_block: " << free_block << " range: " << range_offsets[id] << "\n";
    }

  } else { // Reuse tag
    if (DEBUG) {
      cerr << "Dump begin called - Old tag\n";
    }

    // Throw exception if redefining tag
    id = tag_to_id[str_tag];
    assert(active_ranges.find(id) == active_ranges.end());
  }
  active_ranges[id] = AddressRange(begin, end);
  all_ranges[id] = AddressRange(begin, end);
  analysis_num_dump_calls++;
  analysis_dump_on = true;
  //PIN_RemoveInstrumentation();
}

VOID dump_end_called(VOID * tag) {
  char *s = (char *)tag;
  string str_tag (s);
  if (DEBUG) {
    cerr << "End TAG: " << str_tag << "\n";
  }

  // Assert tag exists
  int id = tag_to_id[str_tag];
  assert(active_ranges.find(id) != active_ranges.end());

  active_ranges.erase(id);
  if (--analysis_num_dump_calls <= 0) {
    analysis_num_dump_calls = 0;
    analysis_dump_on = false;
    if (DEBUG) {
      cerr << "End TAG - Deactivated analysis\n";
    }
  }
  //PIN_RemoveInstrumentation();
}

// Write id,op,addr to file
inline VOID write_to_memfile(int id, int op, ADDRINT addr){
  hdf_handler->write_data_mem(id, op, addr); // straight to hdf
  if (x_range.find(id) == x_range.end()) {
    x_range[id] = std::make_pair(curr_lines, curr_lines);
  } else {
    x_range[id].second = curr_lines;
  }
  curr_lines++; // Afterward, for 0-based indexing
  // If reached file size limit, exit
  if(curr_lines >= max_lines) { // Should probably close files
    PIN_ExitApplication(0);
  }
}


/*
 * Returns: a value based on hit, miss, or compulsory miss
 * 0 - hit
 * 1 - miss
 * 2 - compulsory miss
 *
 */
int add_to_simulated_cache(ADDRINT addr) {
  addr -= addr%cache_line; // Cache line modulus
  if (CACHE_DEBUG) {
    cache_writes++;
  }
  if (all_accesses.find(addr) == all_accesses.end()) { // Compulsory miss
    if (CACHE_DEBUG) {
      comp_misses++;
    }
    if (accesses.size() >= cache_size) { // Evict
      // Second value doesn't matter due to custom equal function
      accesses.erase(std::make_pair(inorder_acc.back(), inorder_acc.begin()));
      inorder_acc.pop_back();
    }
    inorder_acc.push_front(addr); // Add to list and set
    accesses.insert(std::make_pair(addr, inorder_acc.begin()));
    all_accesses.insert(addr);
    if (CACHE_DEBUG) {
      cerr << cache_writes << "th write (comp miss): " << addr << "\n";
    }
    return 2;
  }

  auto iter = accesses.find(std::make_pair(addr,inorder_acc.begin()));
  if (iter != accesses.end()) { // In cache, move to front - Hit
    inorder_acc.splice(inorder_acc.begin(), inorder_acc, iter->second);
    if (CACHE_DEBUG && cache_writes%skip_rate == 0) {
      cerr << cache_writes << "th write (Hit): " << addr << "\n";
    }
    return 0;
  } // Not in cache, move to front - Capacity miss
  if (CACHE_DEBUG) {
    cap_misses++;
    cerr << cache_writes << "th write (cap miss): " << addr << "\n";
  }
  if (accesses.size() >= cache_size) { // Evict
    accesses.erase(std::make_pair(inorder_acc.back(), inorder_acc.begin()));
    inorder_acc.pop_back();
  }
  inorder_acc.push_front(addr); // Add to list and set
  accesses.insert(std::make_pair(addr, inorder_acc.begin()));
  return 1;

}

// Print a memory read record
VOID RecordMemRead(ADDRINT addr) {
  if (DEBUG) {
    read_insts++;
  }
  bool recorded = false;
  // Every tag
  for (auto& x : active_ranges) {
    // Every range for tag
    int id = x.first;
    AddressRange range = x.second;
    ADDRINT start_addr = range.first;
    ADDRINT end_addr   = range.second;
    if (start_addr <= addr && addr <= end_addr) {
     recorded = true;
     if (CACHE_DEBUG) {
       if (first_record == 0) {
         first_record = cache_writes;
         cerr << "First read to cache at time [" << first_record << "] :" << addr << "\n";
       }
     }

     int acc_typ = add_to_simulated_cache(addr); // Add original value to cache
     addr -= range_offsets[id]; // Apply transformation
     if (acc_typ == 0) {
       write_to_memfile(id, 1, addr); // Hit -> 1 // Opposite of this: Higher numbers for hits // Higher numbers of reads
     } else if (acc_typ == 1) {
       write_to_memfile(id, 3, addr); // Capacity miss -> 3
     } else {
       write_to_memfile(id, 5, addr); // Compulsory miss -> 5
     }
      if (EXTRA_DEBUG) {
        cerr << "Record read\n";
      }
      if(RECORD_ONCE) break; // Record just once
    }
  }
  /*if (DEBUG) {
    cerr << "Insts so far: " << read_insts << " Recorded - " << (recorded ? "true" : "false" ) << "\n";
  }*/
  if (!recorded) { // Outside ranges
    addr -= addr%cache_line;
    /*if (stack_map.find(addr) == stack_map.end()) {
      stack_map[addr] = free_stack; // Condense to opposite side of space
      free_stack-=cache_line;
    }*/
    //add_to_simulated_cache(stack_map[addr]); // Add transformed address to cache
    add_to_simulated_cache(addr); // Add original value to cache
  }
}

// Print a memory write record
VOID RecordMemWrite(ADDRINT addr) {
  bool recorded = false;
  // Every tag
  for (auto& x : active_ranges) {
    // Every range for tag
    int id = x.first;
    AddressRange range = x.second;
    ADDRINT start_addr = range.first;
    ADDRINT end_addr   = range.second;
    if (start_addr <= (ADDRINT)addr && (ADDRINT)addr <= end_addr) {
     recorded = true;
     if (CACHE_DEBUG) {
       if (first_record == 0) {
         first_record = cache_writes;
         cerr << "First read to cache at time [" << first_record << "] :" << addr << "\n";
       }
     }
     int acc_typ = add_to_simulated_cache(addr); // Add original value to cache
     addr -= range_offsets[id]; // Transform
     if (acc_typ == 0) {
       write_to_memfile(id, 2, addr); // Hit -> 2 
     } else if (acc_typ == 1) {
       write_to_memfile(id, 4, addr); // Capacity miss -> 4
     } else {
       write_to_memfile(id, 6, addr); // Compulsory miss -> 6
     }
      if (EXTRA_DEBUG) {
        cerr << "Record read\n";
      }
      if(RECORD_ONCE) break; // Record just once
    }
  }
  if (!recorded) { // Outside ranges
    addr -= addr%cache_line;
    /*if (stack_map.find(addr) == stack_map.end()) {
      stack_map[addr] = free_stack; // Condense to opposite side of space
      free_stack-=cache_line;
    }*/
    //add_to_simulated_cache(stack_map[addr]); // Add transformed address to cache
    add_to_simulated_cache(addr); // Add original value to cache
  }
}

const char * StripPath(const char * path) {
  const char * file = strrchr(path, '/');
  if (file)
    return file+1;
  else return path;
}

VOID Fini(INT32 code, VOID *v) {

  if (DEBUG) {
    cerr << "Number of read insts: " << read_insts << "\n";
  }
  if (CACHE_DEBUG) {
    cerr << "Number of compulsory misses: " << comp_misses << "\n";
    cerr << "Number of capacity misses: " << cap_misses << "\n";
  }

  // Write out mapping - only need to open and close map_file here
  map_file.open(output_path + "/tag_map.csv");
  // Every id->tag
  map_file << "Tag_Name,Tag_Value,Low_Address,High_Address,First_Access,Last_Access\n";
  for (auto& x : id_to_tag) {
    int id = x.first;
    string tag = x.second;
    AddressRange addr_range = all_ranges[id];
    ADDRINT offset = range_offsets[id];
    int lo_ind = 0;
    int hi_ind = 0;
    auto iter = x_range.find(id);
    if (iter != x_range.end()) {
      lo_ind = iter->second.first;
      hi_ind = iter->second.second;
    }
    map_file << tag << "," << id << ","
             << addr_range.first - offset << ","
	     << addr_range.second - offset << ","
	     << lo_ind << "," << hi_ind << "\n";
  }

  //std::cerr << cache_accesses.size() << " " << uniq_addr.size() << "\n";
  //for(VOID* x : cache_accesses) {
  /*for(ADDRINT addr_int : inorder_acc) {
    if (addr_int >= max_range) { // outside ranges - stack, untracked data structures
      addr_int  = max_range + (free_stack_start - addr_int); // Move transformed stack to right on top of tracked ranges
    }
    hdf_handler->write_data_cache(addr_int);
  }*/
  // Updated cache write - Must check if it's in any of the tagged ranges
  // Add cache values from least recently used to most recently used
  for (std::list<ADDRINT>::reverse_iterator rit= inorder_acc.rbegin(); rit != inorder_acc.rend(); ++rit) {
    // Check if it's part of any of the ranges
    ADDRINT correct_val = *rit;
    bool tagged = false;
    for (auto& x : all_ranges) {
      if (x.second.first <= *rit && *rit <= x.second.second) {
        correct_val -= range_offsets[x.first]; // Normalize
        tagged = true;
        break;
      }
    }
    if (!tagged) {
      correct_val = max_range; // Just move the cache value that's not tagged to somewhere above all tagged accesses
      max_range+= cache_line;
    }
    hdf_handler->write_data_cache(correct_val);
  }

  // Close files
  map_file.flush();
  map_file.close();
  //hdf_handler.~HandleHdf5();
  delete hdf_handler;
}

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
	// Don't add instrumentation if not inside a DUMP_ACCESS block
	//if(!analysis_dump_on) return;

    // Instruments memory accesses using a predicated call, i.e.
    // the instrumentation is called iff the instruction will actually be executed.
    //
    // On the IA-32 and Intel(R) 64 architectures conditional moves and REP 
    // prefixed instructions appear as predicated instructions in Pin.
    UINT32 memOperands = INS_MemoryOperandCount(ins);
    // Iterate over each memory operand of the instruction.
    for (UINT32 memOp = 0; memOp < memOperands; memOp++)
    {
        const bool isRead = INS_MemoryOperandIsRead(ins, memOp);
        const bool isWrite = INS_MemoryOperandIsWritten(ins, memOp);
        if (isRead) {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END);
        }
        // Note that in some architectures a single memory operand can be 
        // both read and written (for instance incl (%eax) on IA-32)
        // In that case we instrument it once for read and once for write.
        if (isWrite) {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END);
        }
    }
}

// Find the DUMP_MACRO and SET_MAX_OUTPUT routines in the current image and insert a call
VOID FindFunc(IMG img, VOID *v)
{
	RTN rtn = RTN_FindByName(img, DUMP_MACRO_BEG);
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_beg_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, DUMP_MACRO_END);
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_end_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, SET_MAX_OUTPUT);
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)set_max_output_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_END);
		RTN_Close(rtn);
	}
}

INT32 Usage() {
  std::cerr << "Tracks memory accesses and instruction pointers between dump accesses" << std::endl;
  std::cerr << std::endl << KNOB_BASE::StringKnobSummary() << std::endl;
  return -1;
}

int main(int argc, char *argv[]) {
  //Initialize pin & symbol manager
  PIN_InitSymbols();
  if (PIN_Init(argc, argv)) return Usage();
  
  if (DEBUG) {
    cerr << "Debugging mode\n";
  }

  // Output file names
  output_path = KnobOutputFile.Value();
  //string cache_file_name = "cache.h5";
  UINT64 in_output_limit = KnobMaxOutput.Value();
  UINT64 in_cache_size = KnobCacheSize.Value();
  UINT64 in_cache_line = KnobCacheLineSize.Value();
  if (INPUT_DEBUG) {
    cerr << "User input: " << in_output_limit << ", " << in_cache_size << ", " << in_cache_line << "\n";
  }
  if (in_output_limit <= 0) {
    max_lines = DefaultMaxLines;
  } else {
    max_lines = in_output_limit;
  }
  if (in_cache_size <= 0) {
    cache_size = L1CacheEntries;
  } else {
    cache_size = in_cache_size;
  }

  if (in_cache_line <= 0) {
    cache_line = DefaultCacheLineSize;
  } else {
    cache_line = in_cache_line;
    free_stack_start = ULLONG_MAX - ULLONG_MAX%cache_line - cache_line;
    free_stack = free_stack_start; // Actual free space for stack
  }
  if (INPUT_DEBUG) {
    cerr << "Max lines of trace: "   << max_lines <<
	    "\n# of cache entries: " << cache_size <<
	    "\nCache line size in bytes: " << cache_line << "\n";
  }

  hdf_handler = new HandleHdf5(output_path + "/trace.hdf5",
		               output_path + "/cache.hdf5");

  // Add instrumentation
  IMG_AddInstrumentFunction(FindFunc, 0);
  INS_AddInstrumentFunction(Instruction, 0);
  
  PIN_AddFiniFunction(Fini, 0);

  if (DEBUG) {
    cerr << "Starting now\n";
  }
  PIN_StartProgram();
  
  return 0;
}






















