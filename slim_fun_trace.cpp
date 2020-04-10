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
using std::dec;
using std::endl;



ofstream mem_file;
ofstream mem_fun_file;
ofstream inst_file;

static string mem_file_name;
static string mem_fun_file_name;
static string inst_file_name;

static string fun_name;

static long int start_addr = 0;
static long int end_addr = 0;


KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
		"o", "functiontrace.out", "specify trace file name");

KNOB<string> KnobFindFunction(KNOB_MODE_WRITEONCE, "pintool",
    "f", "main", "specify function name");

VOID beforeAfter(CHAR* name, ADDRINT start, ADDRINT end) {
	start_addr = start;
	end_addr = end;
	mem_fun_file << name << endl;
	mem_fun_file << start << endl;
	mem_fun_file << end << endl;

}

/*VOID function_print(VOID *ip) {
	//inst_file << ip << endl;
	cerr << ip << endl;
}*/

VOID RecordMemRead(VOID * ip, VOID * addr)
{
	//mem_file << ip << ": R " << addr << endl;
	if (start_addr <= (long int)addr && (long int)addr < end_addr) {
		//cerr << ip << ": R " << addr << endl;
		mem_file << "R " << addr << endl;
	}
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr)
{
	//mem_file << ip << ": W " << addr << endl;
	if (start_addr <= (long int)addr && (long int)addr < end_addr) {
		//cerr << ip << ": W " << addr << endl;
		mem_file << "W " << addr << endl;
	}
}
 


const char * StripPath(const char * path)
{
	const char * file = strrchr(path, '/');
	if (file)
		return file+1;
	else return path;
}

VOID Image(IMG img, VOID *v)
{
	RTN funRtn = RTN_FindByName(img, fun_name.c_str());
	if (RTN_Valid(funRtn))
	{
		cerr << "Found routine" << endl;

		string path = StripPath(IMG_Name(SEC_Img(RTN_Sec(funRtn))).c_str());
		cerr << "Name: " << RTN_Name(funRtn) << endl;
		cerr << "Path: " << path << endl;
		cerr << "Address: " << RTN_Address(funRtn) << endl;



		RTN_Open(funRtn);

		RTN_InsertCall(funRtn, IPOINT_BEFORE, (AFUNPTR)beforeAfter,
				IARG_ADDRINT, fun_name,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_END);

		int num_insts = 0;

		for (INS ins = RTN_InsHead(funRtn); INS_Valid(ins); ins = INS_Next(ins))
		{
			num_insts++;

			// Insert a call to print fun stuff
			//INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)function_print, IARG_INST_PTR, IARG_END);

			UINT32 memOperands = INS_MemoryOperandCount(ins);

			// Iterate over each memory operand of the instruction.
			for (UINT32 memOp = 0; memOp < memOperands; memOp++)
			{
				if (INS_MemoryOperandIsRead(ins, memOp))
				{
					 INS_InsertPredicatedCall(
						ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
						IARG_INST_PTR,
						IARG_MEMORYOP_EA, memOp,
						IARG_END);
				}
				// Note that in some architectures a single memory operand can be 
				// both read and written (for instance incl (%eax) on IA-32)
				// In that case we instrument it once for read and once for write.
				if (INS_MemoryOperandIsWritten(ins, memOp))
				{
					INS_InsertPredicatedCall(
						ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
						IARG_INST_PTR,
						IARG_MEMORYOP_EA, memOp,
						IARG_END);
				}
			}
		}

		cerr << "Num of insts: " << num_insts << endl;
		RTN_Close(funRtn);
	}
}

VOID Fini(INT32 code, VOID *v)
{
	cerr << "Closing..." << endl;
	mem_file.close();
	mem_fun_file.close();
	inst_file.close();
}

INT32 Usage()
{
	cerr << "Tracks memory accesses and instruction pointers of given function" << endl;
	cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
	return -1;
}

int main(int argc, char *argv[])
{
	//Initialize pin & symbol manager
	PIN_InitSymbols();
	
	// Initialize pin
	if (PIN_Init(argc, argv)) return Usage();

	// Output file names
	mem_file_name = KnobOutputFile.Value().c_str();
	mem_fun_file_name = mem_file_name + "_funmem.out";
	inst_file_name = mem_file_name + "_inst.out";
	mem_file_name+="_mem.out";

	// Output files
	mem_file.open(mem_file_name.c_str());
	mem_fun_file.open(mem_fun_file_name.c_str());
	inst_file.open(inst_file_name.c_str());

	// Function name
	fun_name = KnobFindFunction.Value().c_str();
	cerr << "Going to trace function: " << fun_name << endl;

	// Add instrumentation
	IMG_AddInstrumentFunction(Image, 0);
	PIN_AddFiniFunction(Fini, 0);

	// RTN_AddInstrumentFunction(Routine, 0);
	
	PIN_StartProgram();
	
	return 0;
}



























