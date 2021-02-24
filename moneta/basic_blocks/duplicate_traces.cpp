#include <iostream>
#include "pin.H"
#include <string>
#include <fstream>
#include <unordered_set>

using namespace std;
int num_dupes = 0;
unordered_set<string> dupes;

VOID Trace(TRACE trace, VOID *v){

    for(BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)){
        string block = "";
        for(INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins=INS_Next(ins)){

            if (!INS_IsStandardMemop(ins) && !INS_HasMemoryVector(ins)){
                // We don't know how to treat these instructions
                continue;
            }
            
            block += INS_Disassemble(ins) + "\n";
        }

        block += "\n\n";

        if(dupes.find(block) != dupes.end()){
            num_dupes++;
        } else {
            dupes.insert(block);
        }


    }

}

VOID Fini(INT32 code, VOID *v)
{
    cout << "Duplicate Traces: " << num_dupes << endl;
}

int main(int argc, char * argv[])
{
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