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
//	std::cerr << "done " << std::dec << (int64_t)begin << " " << std::dec << (int64_t)end << " " << stop_start << std::endl;
}

vector<int> arr (SIZE, 0);
void dosom(int iters) {
	for(int i = 0; i < iters; i++) 
		for (int j = 0; j < arr.size(); j++)
			arr[j]++;
}

int main(int argc, char *argv[]) {
	vector<int> c (SIZE, 0);

	DUMP_ACCESS(&c[0], &c[SIZE-1], START);
	DUMP_ACCESS(&c[0], &c[SIZE-1], STOP);

	// Memory accesses will not be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}

	// Start dumping accesses for "c"
	DUMP_ACCESS(&c[0], &c[SIZE-1], START);
	
	// Unrelated memory accesses will not be logged
	dosom(1);
	
	// Accesses to "c" will be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}
	
	// Stop dumping accesses	
	DUMP_ACCESS(&c[0], &c[SIZE-1], STOP);

	// Large number of accesses outside DUMP_ACCESS section, will not be instrumented
	dosom(NUM_ITER);

	// Memory accesses will not be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}

	return 0;
}
