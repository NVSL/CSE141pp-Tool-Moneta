#include "pin.H"
#include <iostream>

#include <fstream>
#include <iomanip>
#include <string.h>
#include <utility>
#include <vector>
#include <unordered_set>

#define DUMP_MACRO_BEG "DUMP_ACCESS_START"
#define DUMP_MACRO_END "DUMP_ACCESS_STOP"
#define DEBUG 0

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

}


ofstream mem_file;

// DEBUG variables
ofstream inst_file;
static int recur_depth = 1;

static string mem_file_name;

static long int start_addr = 0;
static long int end_addr = 0;
static unsigned long int dump_beg_addr = 0;
static unsigned long int dump_end_addr = 0;

static int instrument_num_dump_calls = 0;
static int analysis_num_dump_calls   = 0;
static bool analysis_dump_on      = false;
static bool instrument_dump_on    = false;

const unsigned long long BUF_SIZE = 4ULL * 8ULL* 1024ULL * 1024ULL;
static char * buffer1 = new char[BUF_SIZE];

pintool::unordered_set<std::string> seen_rtns;
vector<pair<ADDRINT, ADDRINT>> ranges;

// Maybe add command line options for:
// Limit on number of accesses to record - int
// Number of files to write to - spread evenly between calls to dump accesses - int

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "functiontrace.out", "specify trace file name");

//KNOB<string> KnobFindFunction(KNOB_MODE_WRITEONCE, "pintool",
//    "f", "main", "specify function name");


VOID dump_beg_called(ADDRINT begin, ADDRINT end) {
  analysis_num_dump_calls++;
  analysis_dump_on = true;
  start_addr = begin;
  end_addr = end;
  ranges.push_back(std::make_pair(start_addr, end_addr)); // Merge intervals?
  if (DEBUG) {
    cerr << "Ranges size: " << ranges.size() << " - " << begin << ", " << end << "\n";
  }
}

VOID dump_end_called() {
  analysis_num_dump_calls = std::max(0, analysis_num_dump_calls-1); // only valid begin ends ()(())(()()())
  if (analysis_num_dump_calls == 0) {
    analysis_dump_on = false;
  }
}

VOID dump_check(VOID *ip) {
  if (DEBUG && analysis_dump_on) {
    inst_file << ip << "\n";
  }
}

// Print a memory read record
VOID RecordMemRead(VOID * addr) {
  for (pair<ADDRINT, ADDRINT> range: ranges) {
    start_addr = range.first;
    end_addr = range.second;
    if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
      mem_file << "R " << addr << "\n";
      break;
    }
  }
}

// Print a memory write record
VOID RecordMemWrite(VOID * addr) {
  for (pair<ADDRINT, ADDRINT> range: ranges) {
    start_addr = range.first;
    end_addr = range.second;
    if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
      mem_file << "W " << addr << "\n";
      break;
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
// UNHANDLED: Instrumentation applied everywhere but analysis may work
// f1() {
//   c[0]++
//   DUMP_END()
// }
//
// main() {
//   DUMP_BEGIN()
//   f1()
// }
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
    UINT32 memOperands = INS_MemoryOperandCount(ins);

    if (DEBUG) { // Instrument every call
      INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dump_check, IARG_INST_PTR, IARG_END);
    }
    // Add instrumentation for memory calls
    for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
      if (INS_MemoryOperandIsRead(ins, memOp)) {
         INS_InsertPredicatedCall(
          ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
          IARG_MEMORYOP_EA, memOp,
          IARG_END);
      }
      if (INS_MemoryOperandIsWritten(ins, memOp)) {
        INS_InsertPredicatedCall(
          ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
          IARG_MEMORYOP_EA, memOp,
          IARG_END);
      }
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
      RTN_InsertCall(e_rtn, IPOINT_BEFORE, (AFUNPTR)dump_end_called, IARG_END);
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
      UINT32 memOperands = INS_MemoryOperandCount(ins);
      for (UINT32 memOp = 0; memOp < memOperands; memOp++) { // Memory accesses
        if (INS_MemoryOperandIsRead(ins, memOp)) {
           INS_InsertPredicatedCall(
            ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
            IARG_MEMORYOP_EA, memOp,
            IARG_END);
        }
        if (INS_MemoryOperandIsWritten(ins, memOp)) {
          INS_InsertPredicatedCall(
            ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
            IARG_MEMORYOP_EA, memOp,
            IARG_END);
        }
      }
    }

    if (INS_IsCall(ins) && INS_IsDirectControlFlow(ins)) { // Check everything for calls to dump access
      if (INS_DirectControlFlowTargetAddress(ins) == dump_beg_addr) { // Calls to dump_access beg
        instrument_num_dump_calls++;
        instrument_dump_on = true;
      }
      else if (INS_DirectControlFlowTargetAddress(ins) == dump_end_addr) { // Calls to dump_access end
        instrument_num_dump_calls = std::max(0, instrument_num_dump_calls-1); // only valid begin ends ()(())(()()())
        if (instrument_num_dump_calls == 0) {
          instrument_dump_on = false;
        }
      }
      else if (instrument_dump_on) { // Call to another function in between dump_access calls
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
  mem_file.close();
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
  
  // Output file names
  mem_file_name = KnobOutputFile.Value().c_str();
  mem_file_name+="_mem.out";

  // Output files
  mem_file.rdbuf()->pubsetbuf(buffer1, BUF_SIZE);
  mem_file.open(mem_file_name.c_str());
  if (DEBUG) {
    cerr << "Debugging mode\n";
    inst_file.open("inst_dump.out");
  }

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



























