#include "hdf5_pin.h"
#include <stdlib.h>
#include <iostream>
#define NUM_ACCESSES 1000000 //one thosand 

int main(void){

	createFile(); // would be called from pintool file main

	for(int i = 0; i<NUM_ACCESSES; i++){
		//long addr = random();    // generate random address
		unsigned long long addr = i;
		bool isWrite = i%2; // generate if access is read or write
        int tag = i%4;
		
		writeData(addr, isWrite,tag); // would be called from recordMemRead or recordMemWrite
	}
	flushData();	
	closeFile(); // in Fini function of pintool file
}
