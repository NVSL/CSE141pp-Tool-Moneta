#include "pin.H"
#include <iostream>

#include <fstream>
#include <iomanip>
#include <string.h>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>

#define DUMP_MACRO_BEG "DUMP_ACCESS_START_TAG"
#define DUMP_MACRO_END "DUMP_ACCESS_STOP_TAG"

#define FILE_SUFFIX "_mem.out"
#define DEBUG 0
#define EXTRA_DEBUG 0
#define BUFFERED 1

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

static int analysis_num_dump_calls = 0;
static bool analysis_dump_on = false;

struct pair_hash {
    inline std::size_t operator()(const std::pair<int,int> & v) const {
        return v.first*31+v.second;
    }
};

pintool::unordered_set<std::string> seen_rtns;
pintool::unordered_map<string, std::tr1::unordered_set<pair<ADDRINT, ADDRINT>,pair_hash>> active_ranges;
pintool::unordered_map<string, std::tr1::unordered_set<pair<ADDRINT, ADDRINT>,pair_hash>> dump_ranges;

const unsigned long long BUF_SIZE = 4ULL * 8ULL* 1024ULL * 1024ULL;
static char * buffer1 = new char[BUF_SIZE];


// Extensions:
// -----------
// Maybe add command line options for:
// Limit on number of accesses to record - int
// Number of files to write to - spread evenly between calls to dump accesses - int

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "functiontrace.out", "specify trace file name");

VOID dump_beg_called(VOID * tag, ADDRINT begin, ADDRINT end) {
  ADDRINT start_addr = begin;
  ADDRINT end_addr = end;

  char* s = (char *)tag;
  string str_tag (s);
  if (DEBUG) {
    cerr << "Dump begin called - " << begin << ", " << end << " TAG: " << str_tag << "\n";
  }

  if (active_ranges.find(str_tag) == active_ranges.end()) { // New tag
    if (DEBUG) {
      cerr << "Dump begin called - New tag\n";
    }
    std::tr1::unordered_set<pair<ADDRINT, ADDRINT>, pair_hash> first_val;
    first_val.insert(std::make_pair(start_addr, end_addr));
    active_ranges[str_tag] = first_val;
  } else {
    if (DEBUG) {
      cerr << "Dump begin called - Old tag\n";
    }
    // Merge intervals? - detect only duplicates using set
    active_ranges[str_tag].insert(
			    std::make_pair(start_addr, end_addr));
  }
  analysis_num_dump_calls = active_ranges.size();
  analysis_dump_on = true;
  PIN_RemoveInstrumentation();
}

VOID dump_end_called(VOID * tag) {
  char *s = (char *)tag;
  string str_tag (s);
  if (DEBUG) {
    cerr << "End TAG: " << str_tag << "\n";
  }
  if (active_ranges.find(str_tag) != active_ranges.end()) { // existing tag
    dump_ranges[str_tag] = std::move(active_ranges[str_tag]);
    active_ranges.erase(str_tag);
    if (--analysis_num_dump_calls <= 0) {
      analysis_num_dump_calls = 0;
      analysis_dump_on = false;
      if (DEBUG) {
        cerr << "End TAG - Deactivated analysis\n";
      }
    }
  }
  PIN_RemoveInstrumentation();
}

// Print a memory read record
VOID RecordMemRead(VOID * addr) {
  // Every tag
  for (auto it = active_ranges.begin(); it != active_ranges.end(); ++it) {
    // Every range for tag
    for (pair<ADDRINT, ADDRINT> range : it->second) {
      ADDRINT start_addr = range.first;
      ADDRINT end_addr   = range.second;
      if (start_addr <= (ADDRINT)addr && (ADDRINT)addr <= end_addr) {
        out_file << "R " << addr << "\n";
        if (EXTRA_DEBUG) {
          cerr << "Record read\n";
        }
        return; // Record just once
      }
    }
  }
}

// Print a memory write record
VOID RecordMemWrite(VOID * addr) {
  // Every tag
  for (auto it = active_ranges.begin(); it != active_ranges.end(); ++it) {
    // Every range for tag
    for (pair<ADDRINT, ADDRINT> range : it->second) {
      ADDRINT start_addr = range.first;
      ADDRINT end_addr   = range.second;
      if (start_addr <= (ADDRINT)addr && (ADDRINT)addr <= end_addr) {
        out_file << "W " << addr << "\n";
        if (EXTRA_DEBUG) {
          cerr << "Record read\n";
        }
        return; // Record just once
      }
    }
  }
}

// Print a memory read/write record
VOID RecordMemReadWrite(VOID * addr) {
  // Every tag
  for (auto it = active_ranges.begin(); it != active_ranges.end(); ++it) {
    // Every range for tag
    for (pair<ADDRINT, ADDRINT> range : it->second) {
      ADDRINT start_addr = range.first;
      ADDRINT end_addr   = range.second;
      if (start_addr <= (ADDRINT)addr && (ADDRINT)addr <= end_addr) {
        out_file << "Y " << addr << "\n";
        if (EXTRA_DEBUG) {
          cerr << "Record both\n";
        }
        return; // Record just once
      }
    }
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
  dump_ranges.insert(active_ranges.begin(), active_ranges.end()); // add any not yet recorded

  // Every tag
  for (auto it = dump_ranges.begin(); it != dump_ranges.end(); ++it) {
    map_file << it->first << ": ";
    // Every range for tag
    for (pair<ADDRINT, ADDRINT> range : it->second) {
      map_file << "{" << range.first << "-" << range.second << "}";
    }
    map_file << "\n";
  }
  // Close files
  out_file.flush();
  out_file.close();
  map_file.close();
  map_file.close();
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
	if(isRead && isWrite) {
	    INS_InsertPredicatedCall(
		ins, IPOINT_BEFORE, (AFUNPTR)RecordMemReadWrite,
                IARG_MEMORYOP_EA,
                memOp,
		IARG_END);
	}
        else if (isRead) {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END);
        }
        // Note that in some architectures a single memory operand can be 
        // both read and written (for instance incl (%eax) on IA-32)
        // In that case we instrument it once for read and once for write.
        else if (isWrite) {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END);
        }
    }
}

// Find the DUMP_ACCESS routine in the current image and insert a call
VOID FindDump(IMG img, VOID *v)
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

  // Open files
  if(BUFFERED)
    out_file.rdbuf()->pubsetbuf(buffer1, BUF_SIZE);
  out_file.open(out_file_name.c_str());

  // Add instrumentation
  IMG_AddInstrumentFunction(FindDump, 0);
  INS_AddInstrumentFunction(Instruction, 0);
  
  PIN_AddFiniFunction(Fini, 0);

  if (DEBUG) {
    cerr << "Starting now\n";
  }
  PIN_StartProgram();
  
  return 0;
}



























