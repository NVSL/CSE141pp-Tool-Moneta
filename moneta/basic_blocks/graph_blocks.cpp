#include <iostream>
#include "pin.H"
#include <string>
#include <fstream>
#include <unordered_set>

using namespace std;
ofstream outfile("./out_graph");
unordered_set<string> visited;

VOID Trace(TRACE trace, VOID *v){

    for(BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)){
        string result = "";
        for(INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins=INS_Next(ins)){

            if (!INS_IsStandardMemop(ins) && !INS_HasMemoryVector(ins)){
                // We don't know how to treat these instructions
                continue;
            }
            
            ADDRINT addr = INS_Address(ins);
            string disas = INS_Disassemble(ins);
            result += StringFromAddrint(addr) + "||" + disas + "\n";
        }
        visited.insert(result);
    }

}

VOID Fini(INT32 code, VOID *v){
    for(string s : visited){
        outfile << s << "\n";
    }
    outfile.flush();
    outfile.close();
}

int main(int argc, char * argv[]){
    // Initialize pin
    if (PIN_Init(argc, argv)){
        cerr << "Input error" << endl;
        return -1;
    }

    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);
    PIN_StartProgram();
    
    return 0;
}