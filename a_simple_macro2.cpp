#include <iostream>
#include <vector>
using namespace std;

#define STOP  0x0
#define START 0x1

#define NUM_ITER (int) 1e3
#define SIZE (int)1e7

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS(int* begin, int* end, int stop_start) {
	volatile int x = stop_start;
	volatile int* y = begin;
	volatile int* z = end;
	std::cerr << "done " << std::dec << (int64_t)begin << " " << std::dec << (int64_t)end << " " << stop_start << std::endl;
}

void dosom() {
	vector<int> arr (SIZE, 0);
	for(int i = 0; i < NUM_ITER; i++) 
		for (int j = 0; j < arr.size(); j++)
			arr[j]++;
}

int main(int argc, char *argv[]) {
	vector<int> c (SIZE, 0);

	// Memory accesses will not be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}

	// Start dumping accesses
	DUMP_ACCESS(&c[0], &c[SIZE-1], START);
	
	// Unrelated memory accesses will not be logged
	dosom();
	
	// Accesses to "arr" will be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}
	
	// Stop dumping accesses	
	DUMP_ACCESS(&c[0], &c[SIZE-1], STOP);

	// Memory accesses will not be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}

	return 0;
}
