#include <iostream>
#include "../pin_tags.h"


int main() {
  int arr [5] = {0}; // An array of 5 ints
  DUMP_START_SINGLE("acc_array", arr, arr+4); // arr == first element's address, arr + 4 == fifth element's address
  std::cout << "Hello world! " << arr[0] << "\n";
  DUMP_STOP("acc_array");

  DUMP_START_MULTI("loop_array", arr, arr+4); // new tag to indicate different part of the program, multi so shows up as loop_array0
  for (int i = 0; i < 10; i++) {
    DUMP_START("loop_array"); // using shorthand, same address range of [arr, arr+4]
    for (int j = 0; j < 5; j++) { // being a multi tag, each inner loop will fall into `loop_array1`, `loop_array2`, ..., `loop_array10`
      arr[j]+=i;
    }
    DUMP_STOP("loop_array"); // stop each loop tag
  }
  DUMP_STOP("loop_array"); // remember to stop the initial call as well!!
  return 0;
}
