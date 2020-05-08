#include "pin.H"
#include <iostream>

#include <fstream>
#include <iomanip>
#include <string.h>
using std::ofstream;
using std::string;
using std::hex;
using std::setw;
using std::cerr;
using std::dec;
using std::endl;

static bool debug = false;

ofstream mem_file;
ofstream inst_file;

static string mem_file_name;

static string fun_name;

static VOID* start_addr = 0;
static VOID* end_addr = 0;
static bool record = false;

const unsigned long long BUF_SIZE = 4ULL * 8ULL* 1024ULL * 1024ULL;
static char * buffer1 = new char[BUF_SIZE];

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
		"o", "functiontrace.out", "specify trace file name");

KNOB<string> KnobFindFunction(KNOB_MODE_WRITEONCE, "pintool",
    "f", "main", "specify function name");

VOID beforeAfter(CHAR* name, ADDRINT start, ADDRINT end) {
	start_addr = (VOID*)start;
	end_addr = (VOID*)end;
	if (debug) {
		cerr << start << ", " <<  end << endl;
	}
}

/*
VOID dump_check(VOID *ip)
{
	inst_file << ip << "\n";
}
*/
VOID RecordMemRead(VOID * addr)
{
	//mem_file << ip << ": R " << addr << endl;
	//if (record && (start_addr <= addr && addr <= end_addr)) {
	if (start_addr <= addr && addr <= end_addr) {
		mem_file << "R " << addr << "\n";
		//volatile int a=1; a=a;
	}
}

// Print a memory write record
VOID RecordMemWrite(VOID * addr)
{
	if (start_addr <= addr && addr <= end_addr) {
		mem_file << "W " << addr << "\n";
		//volatile int a=1; a=a;
	}
}
 


const char * StripPath(const char * path)
{
	const char * file = strrchr(path, '/');
	if (file)
		return file+1;
	else return path;
}

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
	// Don't add instrumentation if not inside a DUMP_ACCESS block
	if(!record) return;

    // Instruments memory accesses using a predicated call, i.e.
    // the instrumentation is called iff the instruction will actually be executed.
    //
    // On the IA-32 and Intel(R) 64 architectures conditional moves and REP 
    // prefixed instructions appear as predicated instructions in Pin.
    UINT32 memOperands = INS_MemoryOperandCount(ins);
    // Iterate over each memory operand of the instruction.
    for (UINT32 memOp = 0; memOp < memOperands; memOp++)
    {
        if (INS_MemoryOperandIsRead(ins, memOp))
        {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END);
        }
        // Note that in some architectures a single memory operand can be 
        // both read and written (for instance incl (%eax) on IA-32)
        // In that case we instrument it once for read and once for write.
        if (INS_MemoryOperandIsWritten(ins, memOp))
        {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END);
        }
    }
}

VOID dump_vars(ADDRINT begin, ADDRINT end, ADDRINT stop_start);


// Find the DUMP_ACCESS routine in the current image and insert a call
VOID FindDump(IMG img, VOID *v)
{
	cerr << "Find Dump\n";
	RTN rtn = RTN_FindByName(img, "DUMP_ACCESS");
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_vars,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_END);
		RTN_Close(rtn);
	}
}

// Add/remove the instrumentation whenever DUMP_ACCESS is called
VOID dump_vars(ADDRINT begin, ADDRINT end, ADDRINT stop_start)
{
	start_addr = (VOID*)begin;
	end_addr = (VOID*)end;
	record = stop_start != 0;
	cerr <<  "DUMP_ACCESS called " << begin << ", " << end << ", " << stop_start << ", " << start_addr << ", " << end_addr << ", " << record << "\n";

	// Redo instrumentation
	PIN_RemoveInstrumentation();
}

VOID Fini(INT32 code, VOID *v)
{
	if (debug) {
		cerr << "Closing..." << endl;
	}
	cerr << "Closing...\n";;
	mem_file.flush();
	mem_file.close();
	inst_file.flush();
	inst_file.close();
}

INT32 Usage()
{
	std::cerr << "Tracks memory accesses and instruction pointers of given function" << std::endl;
	std::cerr << std::endl << KNOB_BASE::StringKnobSummary() << std::endl;
	return -1;
}

int main(int argc, char *argv[])
{
	//Initialize pin & symbol manager
	PIN_InitSymbols();
	if (PIN_Init(argc, argv)) return Usage();
	
	// Output file names
	mem_file_name = KnobOutputFile.Value().c_str();
	mem_file_name+="_mem.out";

	// Output files
    mem_file.rdbuf()->pubsetbuf(buffer1, BUF_SIZE);
	mem_file.open(mem_file_name.c_str());
        //inst_file.rdbuf()->pubsetbuf(buffer2, BUF_SIZE/2);
	inst_file.open("inst_dump.out");

	// Function name
	//fun_name = KnobFindFunction.Value().c_str();
	cerr << "Going to trace function: \n";

	// Add instrumentation
	//IMG_AddInstrumentFunction(Image, 0);
	IMG_AddInstrumentFunction(FindDump, 0);
		INS_AddInstrumentFunction(Instruction, 0);
	PIN_AddFiniFunction(Fini, 0);

	// RTN_AddInstrumentFunction(Routine, 0);
	
	cerr << "starting now\n";
	PIN_StartProgram();
	
	return 0;
}
