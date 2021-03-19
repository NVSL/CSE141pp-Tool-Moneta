#include <iostream>
#include <vector>

using namespace std;

void DUMP_STOP() {}
void DUMP_START(int a) {}

int main() {
	cout << "Starting\n";
    DUMP_START(0);
    int result = 0;
    if (10 < result) {
	    result = 1;
    } else {
	    result = 2;
    }
    result++;
    DUMP_STOP();
    return 0;
}
