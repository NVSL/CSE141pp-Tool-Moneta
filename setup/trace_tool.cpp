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
#include <ctype.h>
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
const std::string DefaultOutputPath {"/home/jovyan/work/moneta/output"};
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
static bool full_trace {0};
static bool track_main {0};
static std::string output_trace_path;
static std::string output_tagfile_path;
static std::string output_metadata_path;

// Macros to track
const std::string M_DUMP_START_SINGLE {"DUMP_START_SINGLE"};
const std::string M_DUMP_START_MULTI  {"_DUMP_START_MULTI"};
const std::string M_DUMP_START        {"DUMP_START"};
const std::string M_DUMP_STOP         {"_DUMP_STOP"};
const std::string FLUSH_CACHE         {"FLUSH_CACHE"};

// Stack/Heap
const std::string STACK {"Stack"};
const std::string HEAP {"Heap"};

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
static int curr_id {0};

struct TagData;

struct Tag {
  const TagData* parent;
  const int id;
  bool active {true};
  std::pair<int, int> x_range {-1, -1};
  std::pair<ADDRINT, ADDRINT> addr_range {ULLONG_MAX, 0};

  Tag(TagData* td, int id) : parent {td}, id {id} {}

  void update(ADDRINT addr, int access) {
    addr_range.first = std::min(addr_range.first, addr);
    addr_range.second = std::max(addr_range.second, addr);
    if (x_range.first == -1) {
      x_range.first = access;
    }
    x_range.second = access;
  }
};

struct TagData {
  const int id;
  const bool single;
  const std::string tag_name;
  const std::pair<ADDRINT, ADDRINT> addr_range;

  std::vector<Tag*> tags;
  
  TagData(std::string tag_name, ADDRINT low, ADDRINT hi, bool single) : 
	  id(curr_id++),
	  single {single},
	  tag_name {tag_name},
	  addr_range({low, hi})
  {
    this->create_new_tag();
  }

  void create_new_tag() {
    tags.push_back(new Tag(this, tags.size()));
  }

  bool update(ADDRINT addr, int access) {
    bool updated {0};
    for (Tag* t : tags) {
      if (t->active) {
        t->update(addr, access);
	updated = true;
      }
    }
    return updated;
  }
  // Default destructor
  ~TagData() {
    for (Tag* t : tags) {
      delete t;
    }
  }
};

// Only the id is output to out_file.
typedef std::pair<ADDRINT, ADDRINT> AddressRange; 

pintool::unordered_map<std::string, TagData*> all_tags;


struct Access {
  TagData* tag;
  int type;
  ADDRINT addr;
} prev_acc;

bool is_prev_acc {0};
ADDRINT min_rsp {ULLONG_MAX};
bool is_last_acc {0};

bool reached_main {0};

// Crudely simulate L1 cache (first n unique accesses between DUMP_ACCESS blocks)

/*
 * Hdf
 */

// Output Columns
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
    acc_d.extend( total_ds_dims ); // Extend size of dataset
    addr_d.extend( total_ds_dims );

    H5::DataSpace old_dataspace = acc_d.getSpace(); // Get old dataspace
    H5::DataSpace new_dataspace = {1, curr_chunk_dims}; // Get new dataspace
    old_dataspace.selectHyperslab( H5S_SELECT_SET, curr_chunk_dims, offset); // Select slab in extended dataset
    acc_d.write( accs, H5::PredType::NATIVE_UINT8, new_dataspace, old_dataspace); // Write to extended part

    old_dataspace = addr_d.getSpace(); // Rinse and repeat
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
  int write_data_mem(ADDRINT address, int access) {
    if (HDF_DEBUG) {
      std::cerr << "Write to Hdf5 - memory\n";
    }
    addrs[mem_ind] = address; // Write to memory first
    accs[mem_ind++] = access;
    if (mem_ind < chunk_size) { // Unless we have reached chunk size
      return 0;
    }
    mem_ind = 0;

    extend_write_mem(); // Then, write to hdf5 file
      
    total_ds_dims[0] += chunk_size; // Update size and offset
    offset[0] += chunk_size;
    /*try { // Should add this error checking somewhere
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
KNOB<std::string> KnobOutputFileLong(KNOB_MODE_WRITEONCE, "pintool",
    "name", "", "specify name of output trace");

KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "n", "default", "specify name of output trace");

KNOB<UINT64> KnobMaxOutputLong(KNOB_MODE_WRITEONCE, "pintool",
    "output_lines", "", "specify max lines of output");

KNOB<UINT64> KnobMaxOutput(KNOB_MODE_WRITEONCE, "pintool",
    "ol", "10000000", "specify max lines of output");

KNOB<UINT64> KnobCacheSizeLong(KNOB_MODE_WRITEONCE, "pintool",
    "cache_lines", "", "specify # of lines in L1 cache");

KNOB<UINT64> KnobCacheSize(KNOB_MODE_WRITEONCE, "pintool",
    "c", "4096", "specify # of lines in L1 cache");

KNOB<UINT64> KnobCacheLineSizeLong(KNOB_MODE_WRITEONCE, "pintool",
    "block", "", "specify block size in bytes");

KNOB<UINT64> KnobCacheLineSize(KNOB_MODE_WRITEONCE, "pintool",
    "b", "64", "specify block size in bytes");

KNOB<BOOL> KnobTrackAllLong(KNOB_MODE_WRITEONCE, "pintool",
    "full", "", "Track all memory accesses");

KNOB<BOOL> KnobTrackAll(KNOB_MODE_WRITEONCE, "pintool",
    "f", "0", "Track all memory accesses");

KNOB<BOOL> KnobStartMainLong(KNOB_MODE_WRITEONCE, "pintool",
    "main", "", "Start trace at main");

KNOB<BOOL> KnobStartMain(KNOB_MODE_WRITEONCE, "pintool",
    "m", "0", "Start trace at main");

VOID flush_cache() {
  if (CACHE_DEBUG) {
    std::cerr << "Flushing cache\n";
  }
  inorder_acc.clear();
  all_accesses.clear();
  accesses.clear();
}


VOID write_to_memfile(ADDRINT addr, int acc_type, bool is_stack) {
  if (is_stack) {
    all_tags[STACK]->update(addr, curr_lines);
  } else {
    all_tags[HEAP]->update(addr, curr_lines);
  }
  hdf_handler->write_data_mem(addr, acc_type);
  curr_lines++; // Afterward, for 0-based indexing
  
  if(!is_last_acc && curr_lines >= max_lines) { // If reached file size limit, exit
    PIN_ExitApplication(0);
  }
}

VOID dump_define_called(VOID * tag_name, ADDRINT low, ADDRINT hi, bool single) {
  char* s = (char *)tag_name;
  std::string str_tag (s);

  if (DEBUG) {
    std::cerr << "Dump define called - " << low << ", " << hi << " TAG: " << str_tag << "\n";
  }

  if (str_tag == HEAP || str_tag == STACK) {
    std::cerr << "Error: Can't use 'Stack' or 'Heap' for tag name\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
  }
  if (all_tags.find(str_tag) == all_tags.end()) { // New tag
    if (DEBUG) {
      std::cerr << "Dump begin called - New tag Tag: " << str_tag << "\n";
      std::cerr << "Range: " << low << ", " << hi << "\n";
    }

    all_tags[str_tag] = new TagData(str_tag, low, hi, single);

  } else { // Reuse tag
    if (DEBUG) {
      std::cerr << "Dump define called - Old tag\n";
    }

    // TODO - make sure single is not different value
    // Exit program if redefining tag
    TagData* old_tag = all_tags[str_tag];
    if (old_tag->addr_range.first != low || // Must be same range
      old_tag->addr_range.second != hi) {
      std::cerr << "Error: Tag redefined - Tag can't map to different ranges\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
    }
    if (old_tag->single) {
      old_tag->tags.front()->active = true;
    } else {
      old_tag->create_new_tag();
    }
  }
}

VOID dump_start_called(VOID * tag_name) {
  char* s = (char *)tag_name;
  std::string str_tag (s);
  if (str_tag == HEAP || str_tag == STACK) {
    std::cerr << "Error: Can't use 'Stack' or 'Heap' for tag name\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
  }
  if (all_tags.find(str_tag) == all_tags.end()) {
    std::cerr << "Error: Can't use define new tags with this call. Try DUMP_START_SINGLE or MULTI\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
  }
  TagData* old_tag = all_tags[str_tag];
  if (old_tag->single) {
    old_tag->tags.front()->active = true;
  } else {
    old_tag->create_new_tag();
  }
}

VOID dump_stop_called(VOID * tag_name) {
  char *s = (char *)tag_name;
  std::string str_tag (s);
  if (DEBUG) {
    std::cerr << "End TAG: " << str_tag << "\n";
  }
  if (str_tag == HEAP || str_tag == STACK) {
    std::cerr << "Error: Can't use 'Stack' or 'Heap' for tag name\n"
              "Exiting Trace Early...\n";
      PIN_ExitApplication(0);
  }

  // Assert tag exists
  // Could be try catch or if else
  std::unordered_map<std::string, TagData*>::const_iterator iter = all_tags.find(str_tag);
  assert(iter != all_tags.end());
  for (std::vector<Tag*>::reverse_iterator i = iter->second->tags.rbegin();
		  i != iter->second->tags.rend(); ++i) {
    if ((*i)->active) {
      (*i)->active = false;
      break;
    }
  }

    /*if (DEBUG) { // Could iterate through all_tags and print if none are active
        std::cerr << "End TAG - Deactivated analysis\n";
    }*/
}

VOID signal_main() {
  reached_main = true;
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

void record(ADDRINT addr, int acc_type) {
  is_prev_acc = true;
  prev_acc.addr = addr;
  prev_acc.type = acc_type;
}

VOID RecordMemAccess(ADDRINT addr, bool is_read, ADDRINT rsp) {
  if (DEBUG) {
    read_insts++;
  }
  min_rsp = std::min(rsp, min_rsp);
  if (is_prev_acc) {
    is_prev_acc = false;
    write_to_memfile(prev_acc.addr, prev_acc.type, prev_acc.addr >= min_rsp);
  }
  if (track_main && !reached_main) return;
  int access_type = translate_cache(add_to_simulated_cache(addr), is_read);
  bool recorded {0};
  for (auto& tag_iter : all_tags) {
    TagData* td = tag_iter.second;
    if (td->tag_name == STACK || td->tag_name == HEAP) continue;
    if ((td->addr_range.first == LIMIT || td->addr_range.first <= addr) && 
		    (td->addr_range.second == LIMIT || addr <= td->addr_range.second)) {
      bool updated = td->update(addr, curr_lines);
      if (!recorded && updated) {
        record(addr, access_type);
        recorded = true;
      }
    }
  }

  if (!recorded && full_trace) {
    record(addr, access_type);
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
    write_to_memfile(prev_acc.addr, prev_acc.type, prev_acc.addr >= min_rsp);
    is_prev_acc = false;
  }
  std::vector<Tag*> tags;
  for (auto& tag_iter : all_tags) {
    TagData* td = tag_iter.second;
    tags.reserve(tags.size() + distance(td->tags.begin(), td->tags.end()));
    tags.insert(tags.end(), td->tags.begin(), td->tags.end());
  }
  std::sort(tags.begin(), tags.end(), 
    []( Tag* left,  Tag* right) {
      return left->x_range.first < right->x_range.first;
  });

  std::ofstream tag_file (output_tagfile_path);
  tag_file << "Tag_Name,Low_Address,High_Address,First_Access,Last_Access\n"; // Header row
  for (Tag* t : tags) {
    if (t->x_range.first != -1) {
      /*if (t->x_range.first == t->x_range.second) { // Minimum of 2 for x_range for easier plotting
        t->x_range.second++;
      }*/
      //tag_file << t->to_string() << "\n";
      tag_file << t->parent->tag_name << (t->parent->single ? "" : std::to_string(t->id)) << "," << t->addr_range.first << ","
	      << t->addr_range.second << "," << t->x_range.first << ","
	      << t->x_range.second << "\n";
    }
  }

  // Close files
  tag_file.flush();
  tag_file.close();

  //hdf_handler.~HandleHdf5();
  delete hdf_handler;
  for (auto& tag_iter : all_tags) {
    delete tag_iter.second;
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

// Find the macro routines in the current image and insert a call
VOID FindFunc(IMG img, VOID *v) {
	RTN rtn = RTN_FindByName(img, M_DUMP_START_SINGLE.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_define_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_BOOL, true,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, M_DUMP_START_MULTI.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_define_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_BOOL, false,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, M_DUMP_START.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_start_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, M_DUMP_STOP.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_stop_called,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_BOOL, true,
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
	rtn = RTN_FindByName(img, "__libc_start_main");
	if (RTN_Valid(rtn)) {
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)signal_main,
				IARG_END);
		RTN_Close(rtn);
	}
}

INT32 Usage() {
  std::cerr << "Tracks memory accesses and instruction pointers between dump accesses\n";
  std::cerr << "\n" << KNOB_BASE::StringKnobSummary() << "\n";
  return -1;
}

bool check_alnum(const std::string& str) {
  for (char c : str) {
    if (!std::isalnum(c) && c != '_') {
      return false;
    }
  }
  return true;
};

int main(int argc, char *argv[]) {
  //Initialize pin & symbol manager
  PIN_InitSymbols();
  if (PIN_Init(argc, argv)) return Usage();
  
  if (DEBUG) {
    std::cerr << "Debugging mode\n";
  }

  // User input
  output_trace_path = KnobOutputFileLong.Value();
  if (output_trace_path == "") {
    output_trace_path = KnobOutputFile.Value();
    if (output_trace_path == "") {
      output_trace_path = "default";
    }
  }
  if (!check_alnum(output_trace_path)) {
    std::cerr << "Output name (" << output_trace_path << ") can only contain alphanumeric characters or _\n";
    return -1;
  }

  max_lines = KnobMaxOutputLong.Value();
  if (max_lines == 0) {
    max_lines = KnobMaxOutput.Value();
    if (max_lines == 0) {
      max_lines = DefaultMaximumLines;
    }
  }

  cache_size = KnobCacheSizeLong.Value();
  if (cache_size == 0) {
    cache_size = KnobCacheSize.Value();
    if (cache_size == 0) {
      cache_size = NumberCacheEntries;
    }
  }

  cache_line = KnobCacheLineSizeLong.Value();
  if (cache_line == 0) {
    cache_line = KnobCacheLineSize.Value();
    if (cache_line == 0) {
      cache_line = DefaultCacheLineSize;
    }
  }

  full_trace = KnobTrackAllLong || KnobTrackAll;
  track_main = KnobStartMainLong || KnobStartMain;

  if (INPUT_DEBUG) {
    std::cerr << "Max lines of trace: "   << max_lines <<
	    "\n# of cache entries: " << cache_size <<
	    "\nCache line size in bytes: " << cache_line << 
	    "\nOutput trace file at: " << output_trace_path << 
	    "\nFull trace: " << full_trace <<
	    "\nTracking main: " << track_main << "\n";
  }

  std::string pref = full_trace ? FullPrefix : "";
  output_tagfile_path = DefaultOutputPath + "/" + pref + TagFilePrefix + output_trace_path + TagFileSuffix;
  output_metadata_path = DefaultOutputPath + "/" + pref + MetaFilePrefix + output_trace_path + MetaFileSuffix;
  output_trace_path = DefaultOutputPath + "/" + pref + TracePrefix + output_trace_path + TraceSuffix;
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
  all_tags[STACK] = new TagData(STACK, LIMIT, LIMIT, true);
  all_tags[HEAP] = new TagData(HEAP, LIMIT, LIMIT, true);
  PIN_StartProgram();
  
  return 0;
}