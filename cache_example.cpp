#include <iostream>
#include <vector>
using namespace std;

#define NUM_ITER (int) 1e3
#define SIZE (int)1e6

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START_TAG(const char* tag, int* begin, int* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP_TAG(const char* tag) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START(int* begin, int* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP() {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS(int* begin, int* end, int stop_start){}
#define START(x,y) DUMP_ACCESS(x,y,1); DUMP_ACCESS_START(x,y); DUMP_ACCESS_START_TAG("a",x,y);
#define STOP(x,y) DUMP_ACCESS(x,y,0); DUMP_ACCESS_STOP(); DUMP_ACCESS_STOP_TAG("a");

vector<int> arr (SIZE, 0);
void dosom(int iters) {
	for(int i = 0; i < iters; i++) 
		for (int j = 0; j < arr.size(); j++)
			arr[j]++;
}

int main(int argc, char *argv[]) {
	vector<int> c (SIZE, 0);
	vector<int> d (100, 0);

	START(&c[0], &c[SIZE-1]);
	STOP(&c[0], &c[SIZE-1]);

	// Memory accesses will not be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}

	// Start dumping accesses for "c"
	START(&c[0], &c[SIZE-1]);
	DUMP_ACCESS_START_TAG("d", &d[0], &d[99]);
	
	// Unrelated memory accesses will not be logged
	dosom(1);
	
	// Accesses to "c" will be logged
	for (int k = 0; k < SIZE/100000; k++) {
		for (int j = 0; j < 10; j++) {
			for (volatile int i = k*100000; i < (k+1)*100000; i++) {
				c[i]++;
			}
			d[10*k+j]++;
		}
	}
	
	// Stop dumping accesses	
	STOP(&c[0], &c[SIZE-1]);
	DUMP_ACCESS_STOP_TAG("d");

	// Large number of accesses outside DUMP_ACCESS section, will not be instrumented
	dosom(NUM_ITER);

	// Memory accesses will not be logged
	for (volatile int i = 0; i < c.size(); i++) {
		c[i]=i;
	}

	return 0;
}
