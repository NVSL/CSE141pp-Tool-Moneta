#include <iostream>
#include <vector>

using namespace std;

void DUMP_STOP() {}
void DUMP_START(int a) {}


int functionA(int i) {
  return i + 1;
}

void functionB(int i) {
  i++;
}

int functionC(int i) {
  return i - 1;
}


int main() {
	cout << "Starting\n";
    DUMP_START(0);
    int result = 0;
    result = functionA(result);
    functionB(result);
    result = functionC(result);
    DUMP_STOP();
    return 0;
}
