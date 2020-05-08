#include <iostream>
#include <vector>
using namespace std;

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START(int* begin, int* end) {
}

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP() {
}

void iterate(vector<int> &cs) {
	for (int i = 0; i < cs.size(); i++) {
		cs[i]++;
	}
	return;
}


void dosom() {
	int size = 10000;
	vector<int> c (size, 0);
	for (int i = 0; i < c.size(); i++) {
		c[i]++;
	}
}
// Single Start stop
int main(int argc, char *argv[]) {
	int size = 100;
	vector<int> c (size, 0);
	//iterate(&c[0], &c[size-1], c);
	DUMP_ACCESS_START(&c[0], &c[size-1]);
	for ( int i = 0; i < c.size(); i++) {
		c[i]++;
	}
	dosom();
	DUMP_ACCESS_STOP();
	return 0;
}
