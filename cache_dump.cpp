#include "pin.H"
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

#define DUMP_MACRO_BEG "DUMP_ACCESS_START_TAG"
#define DUMP_MACRO_END "DUMP_ACCESS_STOP_TAG"
#define SET_MAX_OUTPUT "SET_MAX_OUTPUT"

#define DEFAULT_MAX_LINES (int)1e8

#define FILE_SUFFIX "_mem.out"
#define DEBUG 0
#define EXTRA_DEBUG 0
// Use larger buffer
#define BUFFERED 1
// If addr overlaps multiple ranges, whether to record only one
#define RECORD_ONCE 0

#define L1_CACHE_SIZE 256 * 1024
#define L1_CACHE_ENTRIES 4096
#define DEFAULT_CACHE_LINE 64

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
using unordered_set = std::tr1::unordered_set<V>;

template <typename K, typename V>
using unordered_map = std::tr1::unordered_map<K, V>;
}

ofstream out_file;
ofstream map_file;
ofstream accesses_file;

static int analysis_num_dump_calls = 0;
static bool analysis_dump_on = false;

static UINT64 max_lines = DEFAULT_MAX_LINES;
static UINT64 cache_size = L1_CACHE_ENTRIES;
static UINT64 cache_line = DEFAULT_CACHE_LINE;
static UINT64 curr_lines = 0;

// Increment id every time DUMP_ACCESS is called
static int curr_id = 0;

// tag_to_id used only for dump_access_begin/end
// Only the id is output to out_file.
// id_to_tag is output to out_file
typedef pair<ADDRINT, ADDRINT> AddressRange; 
pintool::unordered_map<int, AddressRange> active_ranges;
pintool::unordered_map<int, ADDRINT> range_offsets;
pintool::unordered_map<ADDRINT, ADDRINT> stack_map;
pintool::unordered_map<string, int> tag_to_id;
pintool::unordered_map<int, string> id_to_tag;

static ADDRINT free_block = 0;
static ADDRINT free_stack_start = ULLONG_MAX - ULLONG_MAX%DEFAULT_CACHE_LINE - DEFAULT_CACHE_LINE;
static ADDRINT free_stack = free_stack_start;

static ADDRINT max_range = 0;

// Crudely simulate L1 cache (first n unique accesses between DUMP_ACCESS blocks)
//pintool::unordered_set<VOID*> uniq_addr;
//std::vector<VOID*> cache_accesses;


struct cache_hash {
	inline std::size_t operator()(const std::pair<VOID*, std::list<VOID*>::iterator> & k) const {
		return (uint64_t)k.first;
	}
};

struct cache_equal {
public:
	inline bool operator()(const std::pair<VOID*, std::list<VOID*>::iterator> & k1, const std::pair<VOID*, std::list<VOID*>::iterator> & k2) const {
 
		if (k1.first == k2.first)
			return true;
		return false;
	}
};


/*struct cache_compare {
    inline bool operator() (const std::pair<VOID*, std::list<VOID*>::iterator> & k1, const std::pair<VOID*, std::list<VOID*>::iterator> & k2) const {
        return k1.first < k2.first;
    }
};*/


std::tr1::unordered_set<std::pair<VOID*, std::list<VOID*>::iterator>, cache_hash, cache_equal> accesses;
//std::set<std::pair<VOID*, std::list<VOID*>::iterator>, cache_compare> accesses;
std::list<VOID*> inorder_acc;

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
    "o", "functiontrace", "specify trace file name");

KNOB<UINT64> KnobMaxOutput(KNOB_MODE_WRITEONCE, "pintool",
    "m", "0", "specify max lines of output");

KNOB<UINT64> KnobCacheSize(KNOB_MODE_WRITEONCE, "pintool",
    "c", "0", "specify entires in L1 cache");

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
      cerr << "Dump begin called - New tag\n";
    }

    id = curr_id++;
    tag_to_id[str_tag] = id;
    id_to_tag[id] = str_tag;


    range_offsets[id] = begin - free_block;
    free_block+= end-begin;
    free_block+= cache_line - free_block%cache_line; // Move to next cache_line for each new tag

    //ADDRINT new_end = end - range_offsets[id];
    //max_range = std::max(max_range, new_end - new_end%cache_line + cache_line);
    max_range = std::max(max_range, free_block);

  } else { // Reuse tag
    if (DEBUG) {
      cerr << "Dump begin called - Old tag\n";
    }

    // Throw exception if redefining tag
    // BUG - id is not defined here
    assert(active_ranges.find(id) == active_ranges.end());

    id = tag_to_id[str_tag]; // Move this up?
  }
  active_ranges[id] = AddressRange(begin, end);
  analysis_num_dump_calls++;
  analysis_dump_on = true;
  PIN_RemoveInstrumentation();
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
  PIN_RemoveInstrumentation();
}

// Write id,op,addr to file
inline VOID write_to_memfile(int id, int op, VOID* addr){
  out_file << id << ',' << op << ',' << (ADDRINT)addr << '\n';
  curr_lines++;
  // If reached file size limit, exit
  if(curr_lines >= max_lines) {
    PIN_ExitApplication(0);
  }
}

/*void add_to_simulated_cache(VOID* addr) {
  if(uniq_addr.size() >= L1_CACHE_SIZE || uniq_addr.find(addr) != uniq_addr.end()) return;
  uniq_addr.insert(addr);
  cache_accesses.push_back(addr);
}*/

bool add_to_simulated_cache2(VOID* addr) {
  //if (accesses.size() >= L1_CACHE_SIZE) return;
  bool is_hit = false;
  addr = (VOID *)((ADDRINT)addr - ((ADDRINT)addr)%cache_line); // Cache line modulus
  auto iter = accesses.find(std::make_pair(addr,inorder_acc.begin()));
  if (iter != accesses.end()) { // In cache, move to front
    inorder_acc.splice(inorder_acc.begin(), inorder_acc, iter->second);
    is_hit = true;
  } else { // Not in cache, move to front
    if (accesses.size() >= cache_size) { // Evict
      accesses.erase(std::make_pair(inorder_acc.back(), inorder_acc.begin()));
      inorder_acc.pop_back();
    }
    inorder_acc.push_front(addr); // Add to list and set
    accesses.insert(std::make_pair(addr, inorder_acc.begin()));
  }
  return is_hit;

}

// Print a memory read record
VOID RecordMemRead(VOID * addr) {
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
     ADDRINT offset = range_offsets[id];
     addr = (VOID *)((ADDRINT)addr - offset); // Apply transformation
     bool is_hit = add_to_simulated_cache2(addr);
     if (is_hit) { // hit
       write_to_memfile(id, 32, addr); // R -> 32 // Higher numbers for hits // Higher numbers of reads
     } else { // miss
       write_to_memfile(id, 8, addr); // S -> 8
     }
      if (EXTRA_DEBUG) {
        cerr << "Record read\n";
      }
      if(RECORD_ONCE) break; // Record just once
    }
  }
  if (!recorded) { // Outside ranges
    ADDRINT addr_int = (ADDRINT)addr; // Condense to opposite side of space
    addr_int = addr_int - addr_int%cache_line;
    if (stack_map.find(addr_int) == stack_map.end()) {
      stack_map[addr_int] = free_stack;
      free_stack-=cache_line;
    }
    add_to_simulated_cache2((VOID *)stack_map[addr_int]); // Add transformed address to cache
  }
}

// Print a memory write record
VOID RecordMemWrite(VOID * addr) {
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
     ADDRINT offset = range_offsets[id];
     addr = (VOID *)((ADDRINT)addr - offset); // Transform
     bool is_hit = add_to_simulated_cache2(addr);
     if (is_hit) { // hit
       write_to_memfile(id, 16, addr); // W -> 16
     } else { // miss
       write_to_memfile(id, 4, addr); // X -> 4
     }
      if (EXTRA_DEBUG) {
        cerr << "Record read\n";
      }
      if(RECORD_ONCE) break; // Record just once
    }
  }
  if (!recorded) { // Outside ranges
    ADDRINT addr_int = (ADDRINT)addr; // Condense to opposite side of space
    addr_int = addr_int - addr_int%cache_line;
    if (stack_map.find(addr_int) == stack_map.end()) {
      stack_map[addr_int] = free_stack;
      free_stack-=cache_line;
    }
    add_to_simulated_cache2((VOID *)stack_map[addr_int]); // Add transformed address to cache
  }
}

const char * StripPath(const char * path) {
  const char * file = strrchr(path, '/');
  if (file)
    return file+1;
  else return path;
}

VOID Fini(INT32 code, VOID *v) {

  // Write out mapping - only need to open and close map_file here
  map_file.open("tag_map.out");
  // Every id->tag
  for (auto& x : id_to_tag) {
    int id = x.first;
    string tag = x.second;
    map_file << id << "," << tag << "\n";
  }

  accesses_file.open("cache_accesses.out");
  //std::cerr << cache_accesses.size() << " " << uniq_addr.size() << "\n";
  std::cerr << accesses.size() << " " << inorder_acc.size() << "\n";
  //accesses_file << "Accesses" << "\n"; // For vaex read from csv
  //for(VOID* x : cache_accesses) {
  for(VOID* x : inorder_acc) {
    ADDRINT addr_int = (ADDRINT)x;
    if (addr_int >= max_range) { // outside ranges - stack, untracked data structures
      addr_int  = max_range + (free_stack_start - addr_int); // Move transformed stack to right on top of tracked ranges
    }
    accesses_file << addr_int << "\n";
  }

  // Close files
  map_file.flush();
  map_file.close();
  out_file.flush();
  out_file.close();
  accesses_file.flush();
  accesses_file.close();
}

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
	// Don't add instrumentation if not inside a DUMP_ACCESS block
	if(!analysis_dump_on) return;

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
  string out_file_name = KnobOutputFile.Value().c_str();
  out_file_name+="_mem.out";
  UINT64 in_output_limit = KnobMaxOutput.Value();
  UINT64 in_cache_size = KnobCacheSize.Value();
  UINT64 in_cache_line = KnobCacheLineSize.Value();
  cerr << in_output_limit << ", " << in_cache_size << ", " << in_cache_line << "\n";
  if (in_output_limit <= 0) {
    max_lines = DEFAULT_MAX_LINES;
  } else {
    max_lines = in_output_limit;
  }
  if (in_cache_size <= 0) {
    cache_size = L1_CACHE_ENTRIES;
  } else {
    cache_size = in_cache_size;
  }

  if (in_cache_line <= 0) {
    cache_line = DEFAULT_CACHE_LINE;
  } else {
    cache_line = in_cache_line;
    free_stack_start = ULLONG_MAX - ULLONG_MAX%cache_line - cache_line;
    free_stack = free_stack_start; // Actual free space for stack
  }

  // Open files
  if(BUFFERED) {
    out_file.rdbuf()->pubsetbuf(buffer1, BUF_SIZE);
    map_file.rdbuf()->pubsetbuf(buffer2, BUF_SIZE);
    accesses_file.rdbuf()->pubsetbuf(buffer3, BUF_SIZE);
  }
  out_file.open(out_file_name.c_str());
  //out_file << "TAG,ACCESS,ADDRESS\n"; // For vaex read from csv

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



























