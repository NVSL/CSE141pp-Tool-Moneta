#include <iostream>
#include <vector>
using namespace std;

#define STOP  0x1
#define START 0x0

volatile int x = 0;
volatile int* y = 0;
volatile int* z = 0;

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS(int* begin, int* end, int stop_start) {
	x = stop_start;
	y = begin;
	z = end;
	if (x == 1) {
		std::cerr << "done " << x << y << z << std::endl;
	}
}

/*void iterate(int* begin, int * end, vector<int> &cs) {
	for (int i = 0; i < cs.size(); i++) {
		cs[i]++;
	}
	return;
}*/


void dosom() {
	int size = 1000;
	vector<int> c (size, 0);
	for (int i = 0; i < c.size(); i++) {
		c[i]++;
	}
}
int main(int argc, char *argv[]) {
	int size = 1000;
	vector<int> c (size, 0);
	//cerr << &c[0] << ", " << &c[size-1] << endl;
	//iterate(&c[0], &c[size-1], c);
	DUMP_ACCESS(&c[0], &c[size-1], START);
	for (int i = 0; i < c.size(); i++) {
		c[i]++;
	}
	dosom();
	DUMP_ACCESS(&c[0], &c[size-1], STOP);
	return 0;
}
