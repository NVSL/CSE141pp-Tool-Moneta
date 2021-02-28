#include <iostream>
#include "../../pin_tags.h"
#include <random>

std::default_random_engine gen;
std::uniform_int_distribution<int> unif_dist(0, 1000);

constexpr int SIZE = 100;

int main() {
  int arr [SIZE] = {0};
  DUMP_START("second_half", arr + SIZE/2, arr + SIZE-1, false);

  // init
  for (int i = 0; i < SIZE; i++) {
    arr[i] = unif_dist(gen);
  }

  // Move largest element to end
  for (int i = 1; i < SIZE; i++) {
    if (arr[i-1] > arr[i]) {
      int tmp = arr[i-1];
      arr[i-1] = arr[i];
      arr[i] = tmp;
    }
  }
  DUMP_STOP("second_half");
  return 0;
}
