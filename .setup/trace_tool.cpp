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
#include <algorithm>
#include <assert.h>
#include <sys/stat.h> // mkdir

#include "pin.H"   // Pin
#include "H5Cpp.h" // Hdf5


// Pin comes with some old standard libraries.
namespace pintool {
template <typename V>
using unordered_set = std::unordered_set<V>;

template <typename K, typename V>
using unordered_map = std::unordered_map<K, V>;
}

// Debug vars
constexpr bool DEBUG {0};
constexpr bool EXTRA_DEBUG {0};
constexpr bool INPUT_DEBUG {0};
constexpr bool HDF_DEBUG   {0};
constexpr bool CACHE_DEBUG {0};
constexpr bool TAG_DEBUG   {0};

static int read_insts = 0;
// Cache debug
static int cache_writes {0};
static int comp_misses  {0};
static int cap_misses   {0};
constexpr int SkipRate  {10000};

// Constant Vars for User input
constexpr ADDRINT DefaultMaximumLines   {100000000};
constexpr ADDRINT NumberCacheEntries    {4096};
constexpr ADDRINT DefaultCacheLineSize  {64};
const std::string DefaultOutputPath {"/home/jovyan/work/moneta/.output"};
constexpr ADDRINT LIMIT {0};

// Output file formatting
const std::string TracePrefix    {"trace_"};
const std::string TraceSuffix    {".hdf5"};
const std::string TagFilePrefix  {"tag_map_"};
const std::string TagFileSuffix  {".csv"};
const std::string MetaFilePrefix {"meta_data_"};
const std::string MetaFileSuffix {".txt"};
const std::string FullPrefix     {"full_"};

// User-initialized
static UINT64 max_lines  {DefaultMaximumLines};
static UINT64 cache_size {NumberCacheEntries};
static UINT64 cache_line {DefaultCacheLineSize};
static std::string output_trace_path;
static std::string output_tagfile_path;
static std::string output_metadata_path;

// Macros to track
const std::string DUMP_MACRO_BEG {"DUMP_ACCESS_START_TAG"};
const std::string DUMP_MACRO_END {"DUMP_ACCESS_STOP_TAG"};
const std::string FLUSH_CACHE    {"FLUSH_CACHE"};

// Access type
enum { 
  READ_HIT=1, WRITE_HIT,
  READ_CAP_MISS, WRITE_CAP_MISS,
  READ_COMP_MISS, WRITE_COMP_MISS 
};

// Cache Access type
enum {
  HIT, CAP_MISS, COMP_MISS
};

static UINT64 curr_lines {0}; // Increment for every write to hdf5 for memory accesses

// Increment id for every new tag
static int curr_id {2}; // Reserved for stack and heap

struct TagData {
  const std::pair<ADDRINT, ADDRINT> addr_range; // Read only
  std::pair<ADDRINT, ADDRINT> limit_addr_range {ULLONG_MAX, 0}; // For LIMIT, mainly
  const std::string tag_name;
  const int id;
  bool active;                 // R/W
  std::pair<int, int> x_range;
  
  TagData(std::string tn, ADDRINT low, ADDRINT hi) : 
	  addr_range({low, hi}),
	  tag_name(tn), 
	  id(curr_id++),
	  active {true},
    x_range({-1, -1}) {}
  // Default destructor
};

// Only the id is output to out_file.
typedef std::pair<ADDRINT, ADDRINT> AddressRange; 

pintool::unordered_map<std::string, TagData*> all_tags;


ADDRINT lower_stack {ULLONG_MAX};
ADDRINT lower_heap  {ULLONG_MAX};
ADDRINT upper_stack {0};
ADDRINT upper_heap  {0};
int last_acc_stack  {0};
int last_acc_heap   {0};
int first_acc_stack {-1};
int first_acc_heap  {-1};

struct Access {
  TagData* tag;
  int type;
  ADDRINT rsp;
  ADDRINT addr;
} prev_acc;

bool is_prev_acc {0};
ADDRINT min_rsp {ULLONG_MAX};
bool is_last_acc {0};

// Crudely simulate L1 cache (first n unique accesses between DUMP_ACCESS blocks)

/*
 * Hdf
 */

// Output Columns
const std::string TagColumn     {"Tag"};
const std::string AccessColumn  {"Access"};
const std::string AddressColumn {"Address"};
//const std::string CacheAccessColumn {"CacheAccess"};

/*
 * Use this to handle hdf with write_data_mem and write_data_cache
 */
class HandleHdf5 {
  static const unsigned long long int chunk_size = 200000; // Private vars
  unsigned long long addrs[chunk_size]; // Chunk local vars
  uint8_t accs[chunk_size];
  int tags[chunk_size];

  //unsigned long long cache_addrs[chunk_size]; // Chunk local vars - cache
  // Current access
  size_t mem_ind = 0;
  //size_t cache_ind = 0;

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
  /*H5::H5File cache_file;
  H5::DataSet cache_d;
    // State vars
  hsize_t curr_chunk_dims_c [1] = {chunk_size};
  hsize_t total_ds_dims_c [1] = {chunk_size};
  hsize_t offset_c [1] = {0};*/

  // Open files, dataspace, and datasets
  void setup_files() {
    if (HDF_DEBUG) {
      std::cerr << "Setting up hdf5 files\n";
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

    //H5::DataSpace c_dataspace {1, idims_t, max_dims};
    //cache_d = cache_file.createDataSet(CacheAccessColumn.c_str(), H5::PredType::NATIVE_ULLONG, c_dataspace, plist);
  }

  // Extends dataset and writes stored chunk
  void extend_write_mem() {
    if (HDF_DEBUG) {
      std::cerr << "Extending and writing dataset for memory accesses\n";
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
  /*void extend_write_cache() {
    if (HDF_DEBUG) {
      std::cerr << "Extending and writing dataset for cache\n";
    }
    cache_d.extend( total_ds_dims_c ); // Extend
    H5::DataSpace old_dataspace = cache_d.getSpace(); // Get old dataspace
    H5::DataSpace new_dataspace = {1, curr_chunk_dims_c}; // Get new dataspace
    old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims_c, offset_c); // Select slab in extended dataset
    cache_d.write( cache_addrs, H5::PredType::NATIVE_ULLONG, new_dataspace, old_dataspace); // Write to the extended part
  }*/

public:
  // Default constructor
  HandleHdf5() : mem_file({"trace.hdf5", H5F_ACC_TRUNC}) { setup_files(); }

  /*// Default constructor - Cache
  HandleHdf5() : mem_file({"trace.hdf5", H5F_ACC_TRUNC}),
                 cache_file({"cache.hdf5", H5F_ACC_TRUNC}) { setup_files(); }*/

  // With names
  HandleHdf5(std::string h) : mem_file({h.c_str(), H5F_ACC_TRUNC}) { setup_files(); }

  // With names - Cache
  /*HandleHdf5(std::string h, std::string c) : 
	         mem_file({h.c_str(), H5F_ACC_TRUNC}),
                 cache_file({c.c_str(), H5F_ACC_TRUNC}) { setup_files(); }*/
  // Destructor
  ~HandleHdf5() {
    if (HDF_DEBUG) {
      std::cerr << "Hdf5 Destructor\n";
    }
    if (mem_ind != 0) { // New data to write
      curr_chunk_dims[0] = mem_ind; // Not full chunk size
      total_ds_dims[0]  -= chunk_size - mem_ind;

      extend_write_mem();
    }

    /*if (cache_ind != 0) { // Same for cache
      curr_chunk_dims_c[0] = cache_ind;
      total_ds_dims_c[0] -= chunk_size - cache_ind;

      extend_write_cache();
    }*/

    // Close files
    mem_file.close();
    //cache_file.close();

  }

  // Write data for memory access to file
  int write_data_mem(int tag, int access, ADDRINT address) {
    if (HDF_DEBUG) {
      std::cerr << "Write to Hdf5 - memory\n";
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
  /*int write_data_cache(ADDRINT address) {
    if (HDF_DEBUG) {
      std::cerr << "Write to Hdf5 - cache\n";
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
  }*/

};

HandleHdf5 *hdf_handler; // One for this pintool

struct cache_hash { // Could improve on this hash function
  inline std::size_t operator()(const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k) const {
    return (uint64_t)k.first;
  }
};

struct cache_equal {
public:
  inline bool operator()(const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k1, const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k2) const {
 
    if (k1.first == k2.first) {
      return true;
    }
    return false;
  }
};


/*struct cache_compare { // Need this to use set
    inline bool operator() (const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k1, const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k2) const {
        return k1.first < k2.first;
    }
};*/


// Stores all info for cache with pointers to where it is in list
std::unordered_set<std::pair<ADDRINT, std::list<ADDRINT>::iterator>, cache_hash, cache_equal> accesses;
std::unordered_set<ADDRINT> all_accesses;
//std::set<std::pair<ADDRINT, std::list<ADDRINT>::iterator>, cache_compare> accesses; // Try set to see if it's faster than unordered_set
std::list<ADDRINT> inorder_acc; // Everything in cache right now

// Increase the file write buffer to speed up i/o
const unsigned long long BUF_SIZE = 4ULL * 8ULL* 1024ULL * 1024ULL;
static char * buffer1 = new char[BUF_SIZE];
static char * buffer2 = new char[BUF_SIZE];
static char * buffer3 = new char[BUF_SIZE];

// Command line options for pintool
KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "default", "specify name of output trace and tag map file");

KNOB<UINT64> KnobMaxOutput(KNOB_MODE_WRITEONCE, "pintool",
    "m", "0", "specify max lines of output");

KNOB<UINT64> KnobCacheSize(KNOB_MODE_WRITEONCE, "pintool",
    "c", "0", "specify entries in L1 cache");

KNOB<UINT64> KnobCacheLineSize(KNOB_MODE_WRITEONCE, "pintool",
    "l", "0", "specify size of cache line for L1 cache");

KNOB<BOOL> KnobTrackAll(KNOB_MODE_WRITEONCE, "pintool",
    "f", "0", "Ignores tags, tracks all memory accesses");

VOID flush_cache() {
  if (CACHE_DEBUG) {
    std::cerr << "Flushing cache\n";
  }
  inorder_acc.clear();
  all_accesses.clear();
  accesses.clear();
}


VOID write_to_memfile(TagData* t, int op, ADDRINT addr, bool is_stack){
  int id = 0;
  if (is_stack) {
    lower_stack = std::min(lower_stack, addr);
    upper_stack = std::max(upper_stack, addr);
    if (first_acc_stack == -1) {
      first_acc_stack = curr_lines;
    }
    last_acc_stack = curr_lines;
  } else {
    lower_heap = std::min(lower_heap, addr);
    upper_heap = std::max(upper_heap, addr);
    if (first_acc_heap == -1) {
      first_acc_heap = curr_lines;
    }
    last_acc_heap = curr_lines;
    id = 1;
  }
  if (t) { // Only if running with tags
    id = t->id;
    if (t->x_range.first == -1) { // First time accessed
      t->x_range.first  = curr_lines;
    }
    t->x_range.second = curr_lines;
  }
  hdf_handler->write_data_mem(id, op, addr);
  curr_lines++; // Afterward, for 0-based indexing
  
  if(!is_last_acc && curr_lines+1 >= max_lines) { // If reached file size limit, exit
    PIN_ExitApplication(0);
  }
}

VOID dump_beg_called(VOID * tag, ADDRINT begin, ADDRINT end) {
  char* s = (char *)tag;
  std::string str_tag (s);

  if (DEBUG) {
    std::cerr << "Dump begin called - " << begin << ", " << end << " TAG: " << str_tag << "\n";
  }

  if (str_tag == "Heap" || str_tag == "Stack") {
    std::cerr << "Error: Can't use 'Stack' or 'Heap' for tag name\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
  }
  if (all_tags.find(str_tag) == all_tags.end()) { // New tag
    if (DEBUG) {
      std::cerr << "Dump begin called - New tag Tag: " << str_tag << "\n";
      std::cerr << "Range: " << begin << ", " << end << "\n";
    }

    TagData *new_tag = new TagData(str_tag, begin, end);
    all_tags[str_tag] = new_tag;

  } else { // Reuse tag
    if (DEBUG) {
      std::cerr << "Dump begin called - Old tag\n";
    }

    // Exit program if redefining tag
    TagData *old_tag = all_tags[str_tag];
    if (old_tag->addr_range.first != begin || // Must be same range
      old_tag->addr_range.second != end) {
      std::cerr << "Error: Tag redefined - Tag can't map to different ranges\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
    }
    old_tag->active = true;
  }
}

VOID dump_end_called(VOID * tag) {
  char *s = (char *)tag;
  std::string str_tag (s);
  if (DEBUG) {
    std::cerr << "End TAG: " << str_tag << "\n";
  }

  // Assert tag exists
  // Could be try catch or if else
  assert(all_tags.find(str_tag) != all_tags.end());
  all_tags[str_tag]->active = false;

    /*if (DEBUG) { // Could iterate through all_tags and print if none are active
        std::cerr << "End TAG - Deactivated analysis\n";
    }*/
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
      std::cerr << cache_writes << "th write (comp miss): " << addr << "\n";
    }
    return COMP_MISS;
  }

  auto iter = accesses.find(std::make_pair(addr,inorder_acc.begin()));
  if (iter != accesses.end()) { // In cache, move to front - Hit
    inorder_acc.splice(inorder_acc.begin(), inorder_acc, iter->second);
    if (CACHE_DEBUG && cache_writes%SkipRate == 0) {
      std::cerr << cache_writes << "th write (Hit): " << addr << "\n";
    }
    return HIT;
  } // Not in cache, move to front - Capacity miss
  if (CACHE_DEBUG) {
    cap_misses++;
    std::cerr << cache_writes << "th write (cap miss): " << addr << "\n";
  }
  if (accesses.size() >= cache_size) { // Evict
    accesses.erase(std::make_pair(inorder_acc.back(), inorder_acc.begin()));
    inorder_acc.pop_back();
  }
  inorder_acc.push_front(addr); // Add to list and set
  accesses.insert(std::make_pair(addr, inorder_acc.begin()));
  return CAP_MISS;

}

int translate_cache(int access_type, bool read) {
  if (access_type == HIT) {
    return read ? READ_HIT : WRITE_HIT;
  } else if(access_type == CAP_MISS) {
    return read ? READ_CAP_MISS : WRITE_CAP_MISS;
  }
  return read ? READ_COMP_MISS : WRITE_COMP_MISS;
}

void record(ADDRINT addr, int acc_type, TagData* tag, ADDRINT rsp) {
  is_prev_acc = true;
  prev_acc.addr = addr;
  prev_acc.type = acc_type;
  prev_acc.tag  = tag;
  prev_acc.rsp  = rsp;
}

VOID RecordMemAccess(ADDRINT addr, bool is_read, ADDRINT rsp) {
  if (DEBUG) {
    read_insts++;
  }
  min_rsp = std::min(rsp, min_rsp);
  if (is_prev_acc) {
    write_to_memfile(prev_acc.tag, prev_acc.type, prev_acc.addr, prev_acc.addr >= std::min(prev_acc.rsp,rsp));
    is_prev_acc = false;
  }
  int access_type = translate_cache(add_to_simulated_cache(addr), is_read);
  TagData* limit_types[2] = {0}; // Storing half limit or no limit ranges
  for (auto& tag_iter : all_tags) {
    TagData* t = tag_iter.second;
    if (!t->active) continue;
    if (t->addr_range.first == LIMIT && t->addr_range.second == LIMIT) { // both limits take precedence
      record(addr, access_type, t, rsp);
      t->limit_addr_range.first = std::min(t->limit_addr_range.first, addr);
      t->limit_addr_range.second = std::max(t->limit_addr_range.second, addr);
      return;
    }
    bool half_limit = false;
    if (!limit_types[0]) { // first one seen
      if (t->addr_range.first == LIMIT) { // Half limits
        half_limit = true;
        if (addr <= t->addr_range.second) {
          t->limit_addr_range.first = std::min(t->limit_addr_range.first, addr);
          limit_types[0] = t;
	}
      }
      else if (t->addr_range.second == LIMIT) {
        half_limit = true;
        if (t->addr_range.first <= addr) {
          t->limit_addr_range.second = std::max(t->limit_addr_range.second, addr);
          limit_types[0] = t;
	}
      }
    }
    if (!half_limit && !limit_types[1] && t->addr_range.first <= addr && addr <= t->addr_range.second) {
      limit_types[1] = t; // no limits - lowest precedence
    }
  }
  if (!limit_types[0]) {
    limit_types[0] = limit_types[1]; // move to beginning, save a variable
  }
  if (limit_types[0]) {
    record(addr, access_type, limit_types[0], rsp);
    return;
  }

  if (KnobTrackAll) {
    record(addr, access_type, 0, rsp);
  }
}

/* Called when tracked program finishes or Pin_ExitApplication is called
 *
 * Fills up tag map file, cache file, closes files, destroys objects
 */
VOID Fini(INT32 code, VOID *v) {

  if (DEBUG) {
    std::cerr << "Number of read insts: " << read_insts << "\n";
  }
  if (CACHE_DEBUG) {
    std::cerr << "Number of compulsory misses: " << comp_misses << "\n";
    std::cerr << "Number of capacity misses: " << cap_misses << "\n";
  }

  // Updated cache write - Must check if it's in any of the tagged ranges
  // Write cache values from least recently used to most recently used
  /*for (std::list<ADDRINT>::reverse_iterator rit= inorder_acc.rbegin(); rit != inorder_acc.rend(); ++rit) {
    // Check if it's part of any of the ranges
    ADDRINT correct_val = *rit;
    bool tagged = false;
    for (auto& x : all_tags) {
      TagData* t = x.second;
      if (t->addr_range.first <= *rit && *rit <= t->addr_range.second) {
        correct_val -= t->range_offset; // Normalize
        tagged = true;
        break;
      }
    }
    if (!tagged) {
      correct_val = max_range; // Just move the cache value that's not tagged to somewhere above all tagged accesses
      max_range+= cache_line;
    }
    hdf_handler->write_data_cache(correct_val);
  }*/

  if (is_prev_acc) {
    is_last_acc = true;
    write_to_memfile(prev_acc.tag, prev_acc.type, prev_acc.addr, prev_acc.addr >= min_rsp);
    is_prev_acc = false;
  }
  if (TAG_DEBUG) {
    std::cerr << "Stack,0," << lower_stack << "," << upper_stack <<
      "," << first_acc_stack << "," << last_acc_stack << "\n";
    std::cerr << "Heap,1," << lower_heap << "," << upper_heap <<
      "," << first_acc_heap  << "," << last_acc_heap << "\n";
    for (auto& x : all_tags) {
      TagData* t = x.second;
      std::cerr << t->tag_name << "," << t->id << ","
               << t->addr_range.first << ","
               << t->addr_range.second << ","
               << t->x_range.first << "," << t->x_range.second << "\n";
    }
  }
  std::ofstream map_file (output_tagfile_path);
  map_file << "Tag_Name,Tag_Value,Low_Address,High_Address,First_Access,Last_Access\n"; // Header row
  if (first_acc_stack != -1 && last_acc_stack != -1) {
    map_file << "Stack,0," << lower_stack 
      << "," << upper_stack 
      << "," << first_acc_stack 
      << "," << last_acc_stack << "\n";
  }
  if (first_acc_heap != -1 && last_acc_heap != -1) {
    map_file << "Heap,1," << lower_heap 
      << "," << upper_heap 
      << "," << first_acc_heap 
      << "," << last_acc_heap << "\n";
  }
  std::vector<std::pair<std::string, TagData*>> vec_tags (all_tags.begin(), all_tags.end());
  std::sort(vec_tags.begin(), vec_tags.end(), 
    [](const std::pair<std::string, TagData*> &left, const std::pair<std::string, TagData*> &right) {
      return left.second->id < right.second->id;
  });
  for (auto& x : vec_tags) {
    TagData* t = x.second;
    if (t->x_range.first != -1 && t->x_range.second != -1) {
      map_file << t->tag_name << "," << t->id // Could overload in TagData struct
        << "," << (t->addr_range.first == LIMIT ? t->limit_addr_range.first : t->addr_range.first)
        << "," << (t->addr_range.second == LIMIT ? t->limit_addr_range.second : t->addr_range.second)
        << "," << t->x_range.first 
        << "," << t->x_range.second << "\n";
    }
  }

  // Close files
  map_file.flush();
  map_file.close();

  //hdf_handler.~HandleHdf5();
  delete hdf_handler;
  // Delete all TagData's
  for (auto& x : all_tags) {
    delete x.second;
  }
}

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{

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
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemAccess,
                IARG_MEMORYOP_EA, memOp,
                IARG_BOOL, true,
                IARG_REG_VALUE, REG_RSP,
                IARG_END);
        }
        // Note that in some architectures a single memory operand can be 
        // both read and written (for instance incl (%eax) on IA-32)
        // In that case we instrument it once for read and once for write.
        if (isWrite) {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemAccess,
                IARG_MEMORYOP_EA, memOp,
                IARG_BOOL, false,
                IARG_REG_VALUE, REG_RSP,
                IARG_END);
        }
    }
}

// Find the DUMP_MACRO and SET_MAX_OUTPUT routines in the current image and insert a call
VOID FindFunc(IMG img, VOID *v) {
	RTN rtn = RTN_FindByName(img, DUMP_MACRO_BEG.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_beg_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, DUMP_MACRO_END.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_end_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, FLUSH_CACHE.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)flush_cache,
				IARG_END);
		RTN_Close(rtn);
	}
}

INT32 Usage() {
  std::cerr << "Tracks memory accesses and instruction pointers between dump accesses\n";
  std::cerr << "\n" << KNOB_BASE::StringKnobSummary() << "\n";
  return -1;
}

int main(int argc, char *argv[]) {
  //Initialize pin & symbol manager
  PIN_InitSymbols();
  if (PIN_Init(argc, argv)) return Usage();
  
  if (DEBUG) {
    std::cerr << "Debugging mode\n";
  }

  // User input
  output_trace_path = KnobOutputFile.Value();
  std::string pref = KnobTrackAll ? FullPrefix : "";
  output_tagfile_path = DefaultOutputPath + "/" + pref + TagFilePrefix + output_trace_path + TagFileSuffix;
  output_metadata_path = DefaultOutputPath + "/" + pref + MetaFilePrefix + output_trace_path + MetaFileSuffix;
  output_trace_path = DefaultOutputPath + "/" + pref + TracePrefix + output_trace_path + TraceSuffix;

  UINT64 in_output_limit = KnobMaxOutput.Value();
  UINT64 in_cache_size = KnobCacheSize.Value();
  UINT64 in_cache_line = KnobCacheLineSize.Value();
  if (INPUT_DEBUG) {
    std::cerr << "User input: " << in_output_limit << ", " << in_cache_size << ", " << in_cache_line << "\n";
  }
  if (in_output_limit > 0) {
    max_lines = in_output_limit;
  }
  if (in_cache_size > 0) {
    cache_size = in_cache_size;
  }
  if (in_cache_line > 0) {
    cache_line = in_cache_line;
  }
  if (INPUT_DEBUG) {
    std::cerr << "Max lines of trace: "   << max_lines <<
	    "\n# of cache entries: " << cache_size <<
	    "\nCache line size in bytes: " << cache_line << 
	    "\nOutput trace file at: " << output_trace_path << "\n";
  }

  mkdir(DefaultOutputPath.c_str(), 0755);

  std::ofstream meta_file (output_metadata_path);
  meta_file << cache_size << " " << cache_line;
  meta_file.flush();
  meta_file.close();

  hdf_handler = new HandleHdf5(output_trace_path);

  // Add instrumentation
  IMG_AddInstrumentFunction(FindFunc, 0);
  INS_AddInstrumentFunction(Instruction, 0);
  
  PIN_AddFiniFunction(Fini, 0);

  if (DEBUG) {
    std::cerr << "Starting now\n";
  }
  PIN_StartProgram();
  
  return 0;
}
