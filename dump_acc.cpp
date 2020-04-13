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

static long int start_addr = 0;
static long int end_addr = 0;
static long int record = -1;
static unsigned long int dump_fun_addr = 0;

static unsigned long int inst_start_addr = 0;
static unsigned long int inst_end_addr = 0;

//const unsigned long long BUF_SIZE = 8ULL*1024ULL*1024ULL;
//static char * buffer1 = new char[BUF_SIZE/2];
//static char * buffer2 = new char[BUF_SIZE/2];

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
		"o", "functiontrace.out", "specify trace file name");

KNOB<string> KnobFindFunction(KNOB_MODE_WRITEONCE, "pintool",
    "f", "main", "specify function name");

VOID beforeAfter(CHAR* name, ADDRINT start, ADDRINT end) {
	start_addr = start;
	end_addr = end;
	if (debug) {
		cerr << start << ", " <<  end << endl;
	}
}

VOID dump_vars(ADDRINT begin, ADDRINT end, ADDRINT stop_start)
{
	start_addr = begin;
	end_addr = end;
	record = stop_start;
	cerr << begin << ", " << end << ", " << stop_start << ", " << start_addr << ", " << end_addr << ", " << record << "\n";
}

VOID dump_check(VOID *ip)
{
	inst_file << ip << "\n";
}

VOID RecordMemRead(VOID * ip, VOID * addr)
{
	//mem_file << ip << ": R " << addr << endl;
	if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
		//cerr << ip << ": R " << addr << endl;
		mem_file << "R " << addr << "\n";
	}
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr)
{
	//mem_file << ip << ": W " << addr << endl;
	if (start_addr <= (long int)addr && (long int)addr <= end_addr) {
		//cerr << ip << ": W " << addr << endl;
		mem_file << "W " << addr << "\n";
	}
}
 


const char * StripPath(const char * path)
{
	const char * file = strrchr(path, '/');
	if (file)
		return file+1;
	else return path;
}


VOID Routine(RTN rtn, VOID *v)
{
	//cerr << RTN_Name(rtn) << "\n";
	if (RTN_Name(rtn) == "main") {
		cerr << "Found main\n";
	}
	if (RTN_Name(rtn) == "DUMP_ACCESS") {
		cerr << "Found Dump";
		cerr << " Address_of_dump: " << RTN_Address(rtn) << "\n";
		dump_fun_addr = RTN_Address(rtn);
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_vars,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
				IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
				IARG_END);
		RTN_Close(rtn);
		cerr << "Record says: " << record << "\n";

	}
	else
	{

		RTN_Open(rtn);
		for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
		{
			//INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dump_check, IARG_INST_PTR, IARG_END);

			if (inst_start_addr != 0 && INS_Address(ins) > inst_start_addr && inst_end_addr == 0) // In between the dumps
			{
				UINT32 memOperands = INS_MemoryOperandCount(ins);
				INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dump_check, IARG_INST_PTR, IARG_END); // record all instructions in between the dumps
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

			/*if (INS_Category(ins) == XED_CATEGORY_CALL) {
				cerr << "Found xed call op: " << INS_Opcode(ins) << ", " << OPCODE_StringShort(INS_Opcode(ins)) << " | cat: ";
				cerr << INS_Category(ins) << ", " << CATEGORY_StringShort(INS_Category(ins));
				cerr << " | inst add: " << INS_Address(ins) << "\n";
			}*/

			if (INS_IsDirectCall(ins)) {
				/*cerr << "Found direct call op: " << INS_Opcode(ins) << ", " << OPCODE_StringShort(INS_Opcode(ins)) << " | cat: ";
				cerr << INS_Category(ins) << ", " << CATEGORY_StringShort(INS_Category(ins));
				cerr << "\n | directboctargetaddr: " << INS_DirectControlFlowTargetAddress(ins);
				cerr << " | inst add: " << INS_Address(ins) << "\n";*/
				if (INS_DirectControlFlowTargetAddress(ins) == dump_fun_addr) // Calls to dump_access
				{
					if (inst_start_addr == 0)
					{
						inst_start_addr = INS_Address(ins);
					} 
					else
					{
						inst_end_addr = INS_Address(ins);
					}
				}
			}

			/*if (INS_IsCall(ins)) {
				cerr << "Found is call op: " << INS_Opcode(ins) << ", " << OPCODE_StringShort(INS_Opcode(ins)) << " | cat: ";
				cerr << INS_Category(ins) << ", " << CATEGORY_StringShort(INS_Category(ins));
				cerr << " | inst add: " << INS_Address(ins) << "\n";
			}*/

			// Iterate over each memory operand of the instruction.
			/*for (UINT32 memOp = 0; memOp < memOperands; memOp++)
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
			}*/
			
		}
		RTN_Close(rtn);
	}
}



/*VOID Image(IMG img, VOID *v)
{
	RTN funRtn = RTN_FindByName(img, fun_name.c_str());
	if (RTN_Valid(funRtn))
	{
		if (debug) {
			cerr << "Found routine" << endl;

			string path = StripPath(IMG_Name(SEC_Img(RTN_Sec(funRtn))).c_str());
			cerr << "Name: " << RTN_Name(funRtn) << endl;
			cerr << "Path: " << path << endl;
			cerr << "Address: " << RTN_Address(funRtn) << endl;
		}



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

		if (debug) {
			cerr << "Num of insts: " << num_insts << endl;
		}
		RTN_Close(funRtn);
	}
}*/

VOID Fini(INT32 code, VOID *v)
{
	if (debug) {
		cerr << "Closing..." << endl;
	}
	cerr << "Closing...\n";;
	mem_file.close();
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
        //mem_file.rdbuf()->pubsetbuf(buffer1, BUF_SIZE/2);
	mem_file.open(mem_file_name.c_str());
        //inst_file.rdbuf()->pubsetbuf(buffer2, BUF_SIZE/2);
	inst_file.open("inst_dump.out");

	// Function name
	//fun_name = KnobFindFunction.Value().c_str();
	cerr << "Going to trace function: \n";

	// Add instrumentation
	//IMG_AddInstrumentFunction(Image, 0);
	RTN_AddInstrumentFunction(Routine, 0);
	PIN_AddFiniFunction(Fini, 0);

	// RTN_AddInstrumentFunction(Routine, 0);
	
	cerr << "starting now\n";
	PIN_StartProgram();
	
	return 0;
}



























