#include "pin.H"
#include <iostream>

#include <fstream>
#include <iomanip>
#include <string.h>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>

#define DUMP_MACRO_BEG "DUMP_ACCESS_START"
#define DUMP_MACRO_END "DUMP_ACCESS_STOP"

#define FILE_SUFFIX "_mem.out"
#define DEBUG 1
#define EXTRA_DEBUG 0

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

// DEBUG variables
ofstream inst_file;
static int recur_depth = 1;

static long int start_addr = 0;
static long int end_addr = 0;
static unsigned long int dump_beg_addr = 0;
static unsigned long int dump_end_addr = 0;

static int instrument_num_dump_calls = 0;
static int analysis_num_dump_calls   = 0;
static bool analysis_dump_on      = false;
static bool instrument_dump_on    = false;


struct pair_hash {
    inline std::size_t operator()(const std::pair<int,int> & v) const {
        return v.first*31+v.second;
    }
};

pintool::unordered_set<std::string> seen_rtns;
//pintool::unordered_map<string, pair<<pair<ADDRINT, ADDRINT>>, pair<ofstream*, bool>>> tagged_ranges;
//pintool::unordered_map<string, vector<pair<pair<ADDRINT, ADDRINT>,bool>>> tagged_ranges;
pintool::unordered_map<string, std::tr1::unordered_set<pair<ADDRINT, ADDRINT>,pair_hash>> active_ranges;
pintool::unordered_map<string, std::tr1::unordered_set<pair<ADDRINT, ADDRINT>,pair_hash>> dump_ranges;

/*vector<vector<int>> insert_interval(vector<vector<int>>& intervals, vector<int>& newInterval) {

        if (intervals.size() == 0) {
            intervals.push_back(newInterval);
            return intervals;
        }
        int left = 0;
        int right = 0;
        
        for (vector<int> interval :intervals){
            if (newInterval[0]>interval[1]) left++;
            if (newInterval[1]>=interval[0]) right++;
            else break;
        }
        
        if (left == right) {
            intervals.insert(intervals.begin() + left, newInterval);
            return intervals;
        }
        newInterval[0] = min(newInterval[0], intervals[left][0]);
        newInterval[1] = max(newInterval[1], intervals[right-1][1]);
        
        intervals.insert(intervals.begin() + left, newInterval);
        intervals.erase(intervals.begin()+left+1,intervals.begin()+right+1);

        return intervals;
}*/


// What it does:

/*main() {
  start("a", a1, a2)
  start("a", b1, b2) // start tracking b1 b2 instead
  data_a/funs()
  end("a") // ends all tracking
 }*/

/*main() {
  start("a", a1, a2) // these two interchangeable
  start("b", b1, b2)
  data_a/funs()
  data_b/funs()
  end("a") // same here
  end("b")
 }*/

/*main() {
  start("a", a1, a2)
  start("b", b1, b2)
  data_a/funs()
  end("a")
  data_b/funs()
  end("b")
 }*/

/*main() {
  start("a", a1, a2)
  data_a/funs()
  end("a")
  data_a/b/funs() // not tracked
  start("b", b1, b2)
  data_b/funs()
  end("b")
 }*/

// What it does not (weird cases):

/*main() {
  start("a", a1, a2)
  start("b", b1, b2)
  data_a/funs()
  data_b/funs()
  end("a") // end tracking just for a
  data_b/funs() // tracked for b
 }*/


/*f1() {
   data_a // tracked
   end("a")
   data_a // not tracked
  }
  main() {
   start("a", a1, a2)
   f1()
  }*/
// Instrumentation applied everywhere but analysis may work

// Extensions:
// -----------
// Maybe add command line options for:
// Limit on number of accesses to record - int
// Number of files to write to - spread evenly between calls to dump accesses - int

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "functiontrace.out", "specify trace file name");

//KNOB<string> KnobFindFunction(KNOB_MODE_WRITEONCE, "pintool",
//    "f", "main", "specify function name");


VOID dump_beg_called(VOID * tag, ADDRINT begin, ADDRINT end) {
  start_addr = begin;
  end_addr = end;

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

  //ranges.push_back(std::make_pair(start_addr, end_addr)); // Merge intervals?
  /*if (DEBUG) {
    cerr << "Ranges size: " << ranges.size() << " - " << begin << ", " << end << " TAG: " << str_tag << "\n";
  }*/
}

VOID dump_end_called(VOID * tag) {
  
  char *s = (char *)tag;
  string str_tag (s);
  if (DEBUG) {
    cerr << "End TAG: " << str_tag << "\n";
  }
  if (active_ranges.find(str_tag) != active_ranges.end()) { // existing tag
    dump_ranges[str_tag] = std::move(active_ranges[str_tag]);
    //dump_ranges[str_tag].insert(active_ranges[str_tag].begin(),
	//	                active_ranges[str_tag].end());
    active_ranges.erase(str_tag);
    if (--analysis_num_dump_calls <= 0) {
      analysis_num_dump_calls = 0;
      analysis_dump_on = false;
      if (DEBUG) {
        cerr << "End TAG - Deactivated analysis\n";
      }
    }
  }
}

VOID dump_check(VOID *ip) {
  if (DEBUG && analysis_dump_on) {
    inst_file << ip << "\n";
  }
}

// Print a memory read record
VOID RecordMemRead(VOID * addr) {
  // Every tag
  for (auto it = active_ranges.begin(); it != active_ranges.end(); ++it) {
    // Every range for tag
    for (pair<ADDRINT, ADDRINT> range : it->second) {
      start_addr = range.first;
      end_addr   = range.second;
      if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
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
      start_addr = range.first;
      end_addr   = range.second;
      if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
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
      start_addr = range.first;
      end_addr   = range.second;
      if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
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

// Handles Recursive calls to functions between dump accesses
// NOTE: Does not check for dump accesses here. ASSUMPTION: entirety of function body is requested for memory trace
VOID instrument_mem_rec(RTN rtn) {
  if (!RTN_Valid(rtn)) {
    return;
  }
  RTN_Open(rtn);
  if (DEBUG) {
    cerr << "Opening: " << RTN_Name(rtn) << " - " << recur_depth << "\n";
  }
  int curr_inst = 0;
  // Go through all instructions
  for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins), curr_inst++) {

    if (DEBUG) { // Instrument every call
      INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dump_check, IARG_INST_PTR, IARG_END);
    }
    // Add instrumentation for memory calls
    if (INS_IsMemoryRead(ins)) {
      if (INS_IsMemoryWrite(ins)) {
      if (EXTRA_DEBUG) {
            cerr << "[" << curr_inst << "] both\n";
      }
       INS_InsertPredicatedCall(
        ins, IPOINT_BEFORE, (AFUNPTR)RecordMemReadWrite,
        IARG_MEMORYREAD_EA,
        IARG_END);
      } else {
      if (EXTRA_DEBUG) {
            cerr << "[" << curr_inst << "] just read\n";
      }
       INS_InsertPredicatedCall(
        ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
        IARG_MEMORYREAD_EA,
        IARG_END);
      }
    } else if (INS_IsMemoryWrite(ins)) {
      if (EXTRA_DEBUG) {
            cerr << "[" << curr_inst << "] just write\n";
      }
      INS_InsertPredicatedCall(
        ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
        IARG_MEMORYWRITE_EA,
        IARG_END);
    }

    if (INS_IsCall(ins) && INS_IsDirectControlFlow(ins)) { // Look for calls in assembly - RECURSION
      RTN_Close(rtn);
      RTN rtn_r = RTN_FindByAddress(INS_DirectControlFlowTargetAddress(ins)); // Get the routine
      if (DEBUG) {
        cerr << "Attempting to call - " << recur_depth << "\n";
      }
      if (seen_rtns.find(RTN_Name(rtn_r)) == seen_rtns.end()) {
        if (DEBUG) {
          cerr << "Calling - " << recur_depth << " - " << RTN_Name(rtn_r) << "\n";
          recur_depth++;
        }
        seen_rtns.insert(RTN_Name(rtn_r));
        instrument_mem_rec(rtn_r); // Recurse
        if (DEBUG) {
          recur_depth--;
          cerr << "Exiting - " << recur_depth << " - " << RTN_Name(rtn_r) << "\n";
        }
      }
      RTN_Open(rtn);
      ins = RTN_InsHead(rtn); // Reset back to instruction before recursive call
      int c = curr_inst;
      while(--c) {
        ins = INS_Next(ins);
      }
    }
  }
  RTN_Close(rtn);
}

VOID Routine(RTN rtn, VOID *v) {
  if (!RTN_Valid(rtn) || seen_rtns.find(RTN_Name(rtn)) != seen_rtns.end()) { // Remove duplication
    if (DEBUG) {
      cerr << "Seeing it again or invalid: " << RTN_Name(rtn) << "\n";
    }
    return;
  }

  if (dump_beg_addr == 0) { // Get addresses for dump macros/functions
    RTN b_rtn = RTN_FindByName(SEC_Img(RTN_Sec(rtn)), DUMP_MACRO_BEG);
    RTN e_rtn = RTN_FindByName(SEC_Img(RTN_Sec(rtn)), DUMP_MACRO_END);
    // TODO:
    // If either one does not exist, exit pintool immediately, because undefined behavior
    if (RTN_Valid(b_rtn)) {
      dump_beg_addr = RTN_Address(b_rtn);
      seen_rtns.insert(RTN_Name(b_rtn));
      if (DEBUG) {
        cerr << "VALID dump begin: " << dump_beg_addr << "\n";
      }
      RTN_Open(b_rtn); // Instrument dump begin
      RTN_InsertCall(b_rtn, IPOINT_BEFORE, (AFUNPTR)dump_beg_called,
          IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
          IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
          IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
          IARG_END);
      RTN_Close(b_rtn);
    }
    if (RTN_Valid(e_rtn)) {
      dump_end_addr = RTN_Address(e_rtn);
      seen_rtns.insert(RTN_Name(e_rtn));
      if (DEBUG) {
        cerr << "VALID dump end: " << dump_end_addr << "\n";
      }
      RTN_Open(e_rtn); // Instrument dump end
      RTN_InsertCall(e_rtn, IPOINT_BEFORE, (AFUNPTR)dump_end_called, 
          IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
	  IARG_END);
      RTN_Close(e_rtn);
    }
  }

  // Check if instrumentation is necessary

  int curr_inst = 0;
  RTN_Open(rtn);
  // Check every instruction
  for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins), curr_inst++) {

    if (instrument_dump_on) { // Start instrumenting
      if (DEBUG) { // Instrument every call
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dump_check, IARG_INST_PTR, IARG_END);
      }
      if (INS_IsMemoryRead(ins)) { // Memory accesses
        if (INS_IsMemoryWrite(ins)) {
        if (EXTRA_DEBUG) {
	      cerr << "[" << curr_inst << "] both\n";
	}
         INS_InsertPredicatedCall(
          ins, IPOINT_BEFORE, (AFUNPTR)RecordMemReadWrite,
          IARG_MEMORYREAD_EA,
          IARG_END);
        } else {
        if (EXTRA_DEBUG) {
	      cerr << "[" << curr_inst << "] just read\n";
	}
         INS_InsertPredicatedCall(
          ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
          IARG_MEMORYREAD_EA,
          IARG_END);
        }
      } else if (INS_IsMemoryWrite(ins)) {
        if (EXTRA_DEBUG) {
	      cerr << "[" << curr_inst << "] just write\n";
	}
        INS_InsertPredicatedCall(
          ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
          IARG_MEMORYWRITE_EA,
          IARG_END);
      }


    }

    if (INS_IsCall(ins) && INS_IsDirectControlFlow(ins)) { // Check everything for calls to dump access
      if (INS_DirectControlFlowTargetAddress(ins) == dump_beg_addr) { // Calls to dump_access beg
        if (DEBUG) {
          cerr << "[" << curr_inst << "] Call to dump start - activate\n";
	}
        instrument_num_dump_calls++;
        instrument_dump_on = true;
      }
      else if (INS_DirectControlFlowTargetAddress(ins) == dump_end_addr) { // Calls to dump_access end
        instrument_num_dump_calls = std::max(0, instrument_num_dump_calls-1); // only valid begin ends ()(())(()()())
        if (DEBUG) {
          cerr << "[" << curr_inst << "] Call to dump end\n";
	}
        if (instrument_num_dump_calls == 0) {
          if (DEBUG) {
            cerr << "Dump - deactivated\n";
	  }
          instrument_dump_on = false;
        }
      }
      else if (instrument_dump_on) { // Call to another function in between dump_access calls
        RTN_Close(rtn);
        RTN rtn_r = RTN_FindByAddress(INS_DirectControlFlowTargetAddress(ins)); // Get the routine
        if (DEBUG) {
          cerr << "[" << curr_inst << "] Attempting to call - " << recur_depth << "\n";
        }
        if (seen_rtns.find(RTN_Name(rtn_r)) == seen_rtns.end()) {
          if (DEBUG) {
            cerr << "Calling - " << recur_depth << " - " << RTN_Name(rtn_r) << "\n";
            recur_depth++;
          }
          seen_rtns.insert(RTN_Name(rtn_r));
          instrument_mem_rec(rtn_r); // Recurse
          if (DEBUG) {
            recur_depth--;
            cerr << "[" << curr_inst << "] Exiting - " << recur_depth << " - " << RTN_Name(rtn_r) << "\n";
          }
        }
        RTN_Open(rtn);
        ins = RTN_InsHead(rtn); // Reset back to instruction before recursive call
        int c = curr_inst;
        while(--c) {
          ins = INS_Next(ins);
        }
      }
    }
  }
  if (instrument_dump_on) {
    if (DEBUG) {
      cerr << "Dump reached end of function - deactivated\n";
    }
    instrument_dump_on = false;
    instrument_num_dump_calls = 0;
  }
  RTN_Close(rtn);
  if (DEBUG && RTN_Name(rtn) == "main") {
    cerr << "Found main\n";
  }
}



VOID Fini(INT32 code, VOID *v) {
  if (DEBUG) {
    cerr << "Closing...\n";
    inst_file.close();
  }
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
  out_file.close();
  map_file.close();
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
    inst_file.open("inst_dump.out");
  }

  // Output file names
  string out_file_name = KnobOutputFile.Value().c_str();
  out_file_name+="_mem.out";

  // Open files
  out_file.open(out_file_name.c_str());

  // Add instrumentation
  //IMG_AddInstrumentFunction(Image, 0);
  RTN_AddInstrumentFunction(Routine, 0);
  PIN_AddFiniFunction(Fini, 0);

  if (DEBUG) {
    cerr << "Starting now\n";
  }
  PIN_StartProgram();
  
  return 0;
}



























