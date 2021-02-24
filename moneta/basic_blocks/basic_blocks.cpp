#include <iostream>
#include "pin.H"
#include <string>
#include <fstream>

using namespace std;
ofstream outfile("./basic_blocks_output");

VOID Trace(TRACE trace, VOID *v){

    for(BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)){
        outfile << "-----------------\n";
        outfile << "   Basic Block   \n";
        outfile << "-----------------\n\n";
        for(INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins=INS_Next(ins)){

            if (!INS_IsStandardMemop(ins) && !INS_HasMemoryVector(ins)){
                // We don't know how to treat these instructions
                continue;
            }
            
            outfile << INS_Disassemble(ins) << "\n";
        }
        
        outfile << "\n-----------------\n\n\n";
        break;
    }

}

VOID Fini(INT32 code, VOID *v)
{
    cout << "Done" << endl;
    outfile.flush();
    outfile.close();
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