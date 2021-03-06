#include <iostream>
#include "pin.H"
#include <string>
#include <fstream>
#include <set>
#include <map>

using namespace std;
ofstream outfile("./out_graph");
ofstream outfile2("./format_graph");
set<string> visited;
bool reached_main = false;

struct BBLData {
  ADDRINT start_addr;
  ADDRINT end_addr;
  bool conditional_jump = true;
  ADDRINT next;
  ADDRINT next2;
  ADDRINT prev;
  string debug;
  string disas;
  int count;

  BBLData(ADDRINT s, ADDRINT e): start_addr(s), end_addr(e) {}
};

bool done = false;

map<ADDRINT, BBLData*> bbls;

BBLData *cached = nullptr;

VOID trace_bbl(ADDRINT first, ADDRINT last, ADDRINT next, bool conditional_jump, const char* debug, string disas, int count) {
	if (!reached_main || done) return;
	cout << "in\n";
	if (cached && cached->conditional_jump) {
		cached->next2 = first;
	}
		
	if (bbls.find(first) == bbls.end()) {
	  BBLData* new_bbl = new BBLData(first, last);
	  new_bbl->next = next;
	  new_bbl->conditional_jump = conditional_jump;
	  new_bbl->debug = debug;
	  new_bbl->disas = disas;
	  new_bbl->count = count;
          for (auto& bbl_iter : bbls) {
            BBLData* bbl = bbl_iter.second;
		
	    if (bbl->start_addr <= first && first <= bbl->end_addr) {
		    bbl->next = first;
		    bbl->end_addr = first;
		    bbl->conditional_jump = false;
		    bbl->next2 = 0;
		    bbl->debug = "intermediary";
		    if (new_bbl->count < bbl->count) {
		      string::size_type i = bbl->disas.find('\n');
		      bbl->count-=new_bbl->count;
		      int occs = bbl->count;
		      while(--occs > 0) {
			i = bbl->disas.find('\n', i+1);
		      }
		      bbl->disas = bbl->disas.substr(0, i+1);
		    }
		    break;
	    }
	    
	  }
	  bbls[first] = new_bbl;
	  cached = new_bbl;

	} else {
		cached = nullptr;
	}
}

VOID Trace(TRACE trace, VOID *v){

    for(BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)){
        string result = "";
	ADDRINT first = 0;
	ADDRINT last = 0;
	ADDRINT next = 0;
	string debug {""};
	bool first_reached = false;
	bool conditional_jump = false;
	cout << BBL_Address(bbl) << "\n";
	string dis_text {""};
	int count = 0;
        for(INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins=INS_Next(ins)){

            if (!INS_IsStandardMemop(ins) && !INS_HasMemoryVector(ins)){
                // We don't know how to treat these instructions
                // continue;
            }
	    if (!first_reached) {
		first = INS_Address(ins);
		cout << "start: " << first << "\n";
		first_reached = true;
	    }
	    if (!INS_Valid(INS_Next(ins))) {
	        last = INS_Address(ins);
		if (INS_IsDirectBranch(ins) || INS_IsDirectCall(ins)) {
		    next = INS_DirectBranchOrCallTargetAddress(ins);
		} else {
		    debug = INS_Disassemble(ins);
		}
		conditional_jump = INS_HasFallThrough(ins);
		if (INS_Category(ins) == XED_CATEGORY_COND_BR) {
			cout << "conditional, " << conditional_jump << "\n";
		}
		if (INS_Category(ins) == XED_CATEGORY_UNCOND_BR) {
			cout << "unconditional, " << conditional_jump << "\n";
		}
	    }
            
            ADDRINT addr = INS_Address(ins);
            string disas = INS_Disassemble(ins);
	    dis_text += disas + "\n";
	    count++;
            result += StringFromAddrint(addr) + "||" + disas + "\n";
        }
	    cout << "res: " << result << "\n";
	trace_bbl(first, last, next, conditional_jump, debug.c_str(), dis_text, count);
	/*BBL_InsertCall(bbl, IPOINT_ANYWHERE, (AFUNPTR)trace_bbl,
			IARG_ADDRINT, first,
			IARG_ADDRINT, last, 
			IARG_ADDRINT, next,
			IARG_BOOL, conditional_jump,
			IARG_PTR, debug.c_str(),
			IARG_END);
        */visited.insert(result);
    }

}

VOID signal_start() {
  reached_main = true;
    cout << "Analysis reached main\n";
}

VOID signal_end() {
  done = true;
    cout << "Analysis done\n";
    PIN_ExitApplication(0);
}

VOID FindStartFunc(RTN rtn, VOID *v) {
  if (!RTN_Valid(rtn)) return;
  RTN_Open(rtn);
  const std::string function_name = PIN_UndecorateSymbolName(RTN_Name(rtn), UNDECORATION_NAME_ONLY);
  if (function_name == "DUMP_START") {
    // reached_main = true;
    RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)signal_start, IARG_END);
    cout << "Reached main\n";
  } else if (function_name == "DUMP_STOP") {
	  cout << "Done\n";
    RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)signal_end, IARG_END);
	  // PIN_ExitApplication(0);
  }
  RTN_Close(rtn);
}

VOID Fini(INT32 code, VOID *v){
    for(string s : visited){
        outfile << s << "\n";
    }

    outfile << "---------------------\n";
    for (auto& bbl_iter : bbls) {
      BBLData* bbl = bbl_iter.second;
      outfile << bbl->start_addr << " " << bbl->end_addr << "\n";
      outfile << "Conditional? " << (bbl->conditional_jump ? "Y" : "N") << "\n";
      outfile << "Next: " << bbl->next << " debug: " << bbl->debug << "\n";
      outfile2 << bbl->start_addr << ", " << bbl->next << "\n";
      outfile2 << bbl->count << "\n" << bbl->disas;
      if (bbl->conditional_jump && bbl->next != bbl->next2) {
        outfile << "Next2: " << bbl->next2 << "\n";
        outfile2 << bbl->start_addr << ", " << bbl->next2 << "\n";
        outfile2 << bbl->count << "\n" << bbl->disas;
      }
      free(bbl);
    }
    outfile2.flush();
    outfile2.close();
    outfile.flush();
    outfile.close();
}

int main(int argc, char * argv[]){
    // Initialize pin
    PIN_InitSymbols();
    if (PIN_Init(argc, argv)){
        cerr << "Input error" << endl;
        return -1;
    }

    TRACE_AddInstrumentFunction(Trace, 0);
    RTN_AddInstrumentFunction(FindStartFunc, 0);
    PIN_AddFiniFunction(Fini, 0);
    PIN_StartProgram();
    
    return 0;
}
