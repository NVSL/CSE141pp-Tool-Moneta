#include <iostream>
#include <vector>
using namespace std;

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START_TAG(const char* tag, int* begin, int* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP_TAG(const char* tag) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START(int* begin, int* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP() {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS(int* begin, int* end, int stop_start){}
#define START(x,y) DUMP_ACCESS(x,y,1); DUMP_ACCESS_START(x,y); DUMP_ACCESS_START_TAG("a",x,y);
#define STOP(x,y) DUMP_ACCESS(x,y,0); DUMP_ACCESS_STOP(); DUMP_ACCESS_STOP_TAG("a");

void iterate(vector<int> &cs) {
	for (int i = 0; i < cs.size(); i++) {
		cs[i]++;
	}
}


void dosom() {
	int size = 10000;
	vector<int> c (size, 0);
	for (int i = 0; i < c.size(); i++) {
		c[i]++;
	}
}
// Single range across nested function
int main(int argc, char *argv[]) {
	int size = 100;
	vector<int> c (size, 0);
	//iterate(&c[0], &c[size-1], c);
	START(&c[0], &c[size-1]);
	for ( int i = 0; i < c.size(); i++) {
		c[i]++;
	}
	iterate(c);
	STOP(&c[0], &c[size-1]);
	return 0;
}
