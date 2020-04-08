#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
#include "pin.H"
using std::ofstream;
using std::string;
using std::hex;
using std::setw;
using std::cerr;
using std::cout;
using std::dec;
using std::endl;

ofstream outFile;
#define TARGET "loopArr"

static int counter = 1;

VOID RecordMemRead(VOID * ip, VOID * addr)
{
	outFile << counter++ << "," << addr << "," << "R" << endl;
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr)
{
	outFile << counter++ << "," << addr << "," << "W" << endl;
}
    

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v){
    

    string funcName = RTN_Name(rtn);
    funcName = PIN_UndecorateSymbolName(funcName, UNDECORATION_NAME_ONLY);
    if(funcName == TARGET){

        RTN_Open(rtn);
        for(INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)){
		    UINT32 memOperands = INS_MemoryOperandCount(ins);

            for(UINT32 memOp = 0; memOp < memOperands; memOp++){
			    if (INS_MemoryOperandIsRead(ins, memOp)){
				    INS_InsertPredicatedCall(
					    ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
					    IARG_INST_PTR,
					    IARG_MEMORYOP_EA, memOp,
					    IARG_END);
			    }
			    // Note that in some architectures a single memory operand can be 
			    // both read and written (for instance incl (%eax) on IA-32)
			    // In that case we instrument it once for read and once for write.
			    if (INS_MemoryOperandIsWritten(ins, memOp)){
				    INS_InsertPredicatedCall(
					    ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
					    IARG_INST_PTR,
					    IARG_MEMORYOP_EA, memOp,
					    IARG_END);
			    }     
            }
        }
        RTN_Close(rtn);
    }

            
}


KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "memtrace.out", "specify output file name");

KNOB<string> KnobFindFunction(KNOB_MODE_WRITEONCE, "pintool",
    "f", "main", "specify function name");

// This function is called when the application exits
// It prints the name and count for each procedure
VOID Fini(INT32 code, VOID *v)
{

    cout<<"Done\n";

}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This Pintool counts the number of times a routine is executed" << endl;
    cerr << "and the number of instructions executed in a routine" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char * argv[])
{
    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();


    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    outFile.open(KnobOutputFile.Value().c_str());

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
