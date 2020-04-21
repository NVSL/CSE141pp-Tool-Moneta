#include "hdf5_pin.h"
#include <stdlib.h>
#include <iostream>
#define NUM_ACCESSES 1000 //one thosand 

int main(void){

	createFile(); // would be called from pintool file main

	for(int i = 0; i<NUM_ACCESSES; i++){
		long addr = random();    // generate random address
		bool isWrite = true; // generate if access is read or write
		
		writeData(addr, isWrite); // would be called from recordMemRead or recordMemWrite
	}
	
	closeFile(); // in Fini function of pintool file
}
