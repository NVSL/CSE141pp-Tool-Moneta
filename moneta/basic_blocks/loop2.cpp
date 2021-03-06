#include <iostream>
#include <vector>

using namespace std;

void DUMP_STOP() {}
void DUMP_START(int a) {}

int main() {
	cout << "Starting\n";
    DUMP_START(0);
    int test = 0;
    for(int i = 0; i < 10; i++){
        test++;
    }
    DUMP_STOP();
    return 0;
}
