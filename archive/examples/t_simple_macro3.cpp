#include <iostream>
#include <vector>
using namespace std;

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START(char* tag, int* begin, int* end) {
}

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP(char* tag) {
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
	int size_a = 1000000;
	int size_b = 100000;
	vector<int> a (size_a, 0);
	vector<int> b (size_b, 0);
	//iterate(&c[0], &c[size-1], c);
	DUMP_ACCESS_START("a", &a.front(), &a.back());
	DUMP_ACCESS_START("b", &b.front(), &b.back());
	for ( int i = 0; i < a.size(); i++) {
		a[i]++;
	}
	iterate(b);
	DUMP_ACCESS_STOP("a");
	DUMP_ACCESS_STOP("b");
	return 0;
}
