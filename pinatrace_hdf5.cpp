/*
 * Copyright 2002-2019 Intel Corporation.
 * 
 * This software is provided to you as Sample Source Code as defined in the accompanying
 * End User License Agreement for the Intel(R) Software Development Products ("Agreement")
 * section 1.L.
 * 
 * This software and the related documents are provided as is, with no express or implied
 * warranties, other than those that are expressly stated in the License.
 */
​
/*
 *  This file contains an ISA-portable PIN tool for tracing memory accesses.
 */
​
#include <stdio.h>
#include "pin.H"
//#include </home/jovyan/work/hdf5-1.12.0/hdf5/include/hdf5.h>
 #include "/setup/H5Cpp.h"
​
using namespace H5;
​
FILE * trace;
​
const H5std_string	FILE_NAME("h5tutr_dset.h5");
//H5File file;
​
// Print a memory read record
VOID RecordMemRead(VOID * ip, VOID * addr)
{
    fprintf(trace,"%p: R %p\n", ip, addr);
    
	//revise arg ********
/*	int data[] = {*(int *)addr,(int) 0};
	hsize_t dim[] = {2};
	DataSpace dataspace(1, dim);
	DataSet dataset = file.createDataSet("dat", PredType::STD_I32BE, dataspace);
	dataset.write(data, PredType::NATIVE_INT);	
*/
}
​
// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr)
{
    fprintf(trace,"%p: W %p\n", ip, addr);
    //
    //revise arg **********
//	int data[] = {*(int *)addr, (int)1};
	hsize_t dim[] = {2};
	DataSpace dataspace(1, dim);
/*	DataSet dataset = file.createDataSet("dat", PredType::STD_I32BE, dataspace);
	dataset.write(data, PredType::NATIVE_INT);	
*/
	}
​
// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
    // Instruments memory accesses using a predicated call, i.e.
    // the instrumentation is called iff the instruction will actually be executed.
    //
    // On the IA-32 and Intel(R) 64 architectures conditional moves and REP 
    // prefixed instructions appear as predicated instructions in Pin.
    UINT32 memOperands = INS_MemoryOperandCount(ins);
​
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
​
VOID Fini(INT32 code, VOID *v)
{
    //fprintf(trace, "#eof\n");
    //fclose(trace);
}
​
/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
   
INT32 Usage()
{
    PIN_ERROR( "This Pintool prints a trace of memory addresses\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}
​
/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
​
int main(int argc, char *argv[])
{
    if (PIN_Init(argc, argv)) return Usage();
​
    trace = fopen("pinatrace.out", "w");
    //
    //revise args *********
//	file.openFile(FILE_NAME, 'w');
	//dataset = file.openDataSet(DATASET_NAME);
​
    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);
​
    // Never returns
    PIN_StartProgram();
    
    return 0;
}