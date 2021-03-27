#include <iostream>
#include "pin.H"
#include <string>
#include <fstream>
#include <set>
#include <map>
#include <vector>
#include <utility>
#include <unordered_set>
#include <unordered_map>

using namespace std;
ofstream outfile("./out_graph");
ofstream outfile2("./format_graph");
ofstream outfile3("./end_graph");
set<string> visited;
bool reached_main = false;


enum {
  HAS_UNCONDITIONAL_JUMP,
  HAS_CONDITIONAL_JUMP,
  HAS_CALL,
  HAS_RETURN,
  HAS_NONE,
  FRAGMENT
};

struct BBLInfo {
  ADDRINT start_addr;
  ADDRINT end_addr;
  int type;
  ADDRINT next;
  ADDRINT immediate_next = 0;
  vector<pair<ADDRINT, string>> instr_strs;
  unordered_set<ADDRINT> instrs;

  string debug;
  string disas;
  bool post_processed = false;

  int column;
  int line;
  string filename;

  void to_string() {
    cout << start_addr << ", " << end_addr << "\n";
    cout << "C: " << column << " L: " << line << " file: " << filename << "\n";
    cout << "next: " << next << " " << instr_strs.size() << "\n";
    cout << "imm_next: " << immediate_next << "\n";
    for (auto& instr_str : instr_strs) {
      cout << instr_str.second << "\n";
    }
    cout << "-------\n";
  }
  
};


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
unordered_map<ADDRINT, BBLInfo*> bbl_infos;

BBLInfo *cached = nullptr;

VOID trace_bbl(ADDRINT first, ADDRINT last, ADDRINT next, int type, vector<pair<ADDRINT, string>>& instr_strs, const char* debug, int column, int line, string & filename) {
	if (!reached_main || done) return;
	if (cached) {
	  if (cached->type == HAS_CONDITIONAL_JUMP) {
	    cached->immediate_next = first;
	  } else if (cached->type == HAS_RETURN) {
	    cached->next = first;
	  }
	}
		
	if (bbl_infos.find(first) == bbl_infos.end()) {
	  BBLInfo* new_bbl = new BBLInfo();
	  new_bbl->start_addr = first;
	  new_bbl->end_addr = last;
	  new_bbl->next = next;
	  new_bbl->type = type;
	  new_bbl->debug = debug;
	  new_bbl->instr_strs = instr_strs;
	  new_bbl->column = column;
	  new_bbl->line = line;
	  new_bbl->filename = filename;
          /*for (auto& bbl : bbl_infos) {
		
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
	    
	  }*/
	  bbl_infos[first] = new_bbl;
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
	cout << BBL_Address(bbl) << "\n";
	int type = HAS_NONE;
	vector<pair<ADDRINT, string>> instr_strs;

        int column = 0;
        int line = 0;
        string filename;
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
		if (INS_HasFallThrough(ins)) {
		  type = HAS_CONDITIONAL_JUMP;
		} else if (INS_IsRet(ins)) {
		  type = HAS_RETURN;
		    cout << "return: " << INS_Disassemble(ins) << "\n";
		} else {
		  type = HAS_UNCONDITIONAL_JUMP;
		}
		/*if (INS_Category(ins) == XED_CATEGORY_COND_BR) {
			cout << "conditional, " << conditional_jump << "\n";
		}
		if (INS_Category(ins) == XED_CATEGORY_UNCOND_BR) {
			cout << "unconditional, " << conditional_jump << "\n";
		}*/
	    }
            
            ADDRINT addr = INS_Address(ins);
	    PIN_GetSourceLocation(addr, &column, &line, &filename);
            string disas = INS_Disassemble(ins);
	    instr_strs.push_back(make_pair(addr, disas));
            result += StringFromAddrint(addr) + "||" + disas + "\n";
        }
	    cout << "res: " << result << "\n";
	trace_bbl(first, last, next, type, instr_strs, debug.c_str(), column, line, filename);
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

bool split(BBLInfo* outer_bbl, BBLInfo* inner_bbl) {
  bool is_split = false;
  // inner_bbl is a part of outer_bbl - outer_bbl splits into FRAGMENT + inner_bbl, outer_bbl overwritten by FRAGMENT
  if (inner_bbl->start_addr > outer_bbl->start_addr && inner_bbl->end_addr == outer_bbl->end_addr) {
	  cout << "FRAGMENT + inner_bbl subset\n";
    outer_bbl->type = FRAGMENT;
    size_t start_addr_ind = 0;
    while (start_addr_ind < outer_bbl->instr_strs.size()) {
      if (outer_bbl->instr_strs[start_addr_ind].first == inner_bbl->start_addr) {
	break;
      }
      start_addr_ind++;
    }
    outer_bbl->end_addr = outer_bbl->instr_strs[start_addr_ind-1].first;
    outer_bbl->next = inner_bbl->start_addr;
    outer_bbl->immediate_next = 0; // clearing this field out since it's a bbl FRAGMENT
    outer_bbl->instr_strs.erase(outer_bbl->instr_strs.begin()+start_addr_ind, outer_bbl->instr_strs.end());
    is_split = true;
  } else if (inner_bbl->next > outer_bbl->start_addr && inner_bbl->next <= outer_bbl->end_addr) {
	  cout << "FRAGMENT + outer_bbl called in\n";
	  inner_bbl->to_string();
	  outer_bbl->to_string();
  // inner_bbl jumps to middle of outer_bbl - outer_bbl splits into FRAGMENT + part of outer_bbl, add one new BBLInfo
  // <= because bbl can jump to last instruction of another bbl
    size_t start_addr_ind = 0;
    while (start_addr_ind < outer_bbl->instr_strs.size()) {
      if (outer_bbl->instr_strs[start_addr_ind].first == inner_bbl->next) {
	break;
      }
      start_addr_ind++;
    }
    cout << start_addr_ind << "--\n";
    BBLInfo* fragment = new BBLInfo();
    fragment->start_addr = outer_bbl->start_addr;
    fragment->end_addr = outer_bbl->instr_strs[start_addr_ind-1].first;
    fragment->type = FRAGMENT;
    fragment->next = inner_bbl->next;
    vector<pair<ADDRINT, string>> instr_strs (outer_bbl->instr_strs.begin(), outer_bbl->instr_strs.begin() + start_addr_ind);
    fragment->instr_strs = instr_strs;

    outer_bbl->start_addr = inner_bbl->next;
    outer_bbl->instr_strs.erase(outer_bbl->instr_strs.begin(), outer_bbl->instr_strs.begin()+start_addr_ind);
    int column = 0;
    int line = 0;
    string filename;
    PIN_GetSourceLocation(outer_bbl->start_addr, &column, &line, &filename);
    outer_bbl->column = column;
    outer_bbl->line = line;
    outer_bbl->filename = filename;

    bbl_infos[fragment->start_addr] = fragment;
    bbl_infos[outer_bbl->start_addr] = outer_bbl;
    fragment->to_string();
    outer_bbl->to_string();
    is_split = true;
  }
  return is_split;
}

VOID Fini(INT32 code, VOID *v){
    for(string s : visited){
        outfile << s << "\n";
    }

    outfile << "---------------------\n";


    bool unaltered = false;
    bool inner_break = false;
    unordered_map<ADDRINT, BBLInfo*>::iterator outer_iter = bbl_infos.begin();
    while (!unaltered) {
      outer_iter = bbl_infos.begin();

      while (outer_iter != bbl_infos.end()) {
        BBLInfo* outer_bbl = outer_iter->second;
	if (outer_bbl->post_processed) {
          outer_iter++;
	  continue;
	}

        unordered_map<ADDRINT, BBLInfo*>::iterator inner_iter = bbl_infos.begin();
        while (inner_iter != bbl_infos.end()) {
          BBLInfo* inner_bbl = inner_iter->second;
          if (inner_bbl->post_processed) {
            inner_iter++;
	    continue;
	  }
	  if (split(outer_bbl, inner_bbl)) {
            inner_break = true;
            break;
	  }
	  inner_iter++;
        }
	if (inner_break) {
          break;
	} else {
          outer_bbl->post_processed = true;
	}
      }
      if (inner_break) {
        inner_break = false;
      } else {
        unaltered = true;
      }
    }

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
    for (auto& bbl_iter : bbl_infos) {
      BBLInfo* bbl = bbl_iter.second;
      outfile3 << bbl->start_addr << ", " << bbl->next << "\n";
      outfile3 << bbl->instr_strs.size() + 1 << "\n";
      outfile3 << "File: " << bbl->filename << "\n";
      outfile3 << "C: " << bbl->column << " L: " << bbl->line << " ";
      outfile3 << bbl->start_addr << ": ";
      for (auto& instr_str : bbl->instr_strs) {
        outfile3 << instr_str.second << "\n";
      }
      if (bbl->type == HAS_CONDITIONAL_JUMP && bbl->immediate_next != 0) {
        outfile3 << bbl->start_addr << ", " << bbl->immediate_next << "\n";
        outfile3 << bbl->instr_strs.size() + 1 << "\n";
        outfile3 << "File: " << bbl->filename << "\n";
        outfile3 << "C: " << bbl->column << " L: " << bbl->line << " ";
        outfile3 << bbl->start_addr << ": ";
        for (auto& instr_str : bbl->instr_strs) {
          outfile3 << instr_str.second << "\n";
        }
      }
    }
    outfile2.flush();
    outfile2.close();
    outfile.flush();
    outfile.close();
    outfile3.flush();
    outfile3.close();
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
