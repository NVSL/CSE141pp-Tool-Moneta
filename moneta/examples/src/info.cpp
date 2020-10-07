#include "../../pin_tags.h"
#include <iostream>
#include <random>
#include <cassert>
#include <vector>

constexpr int SIZE {1000};

int main() {
  std::vector<int> mem (SIZE, 0);

  std::cerr << "Calibration\n";
  DUMP_START_SINGLE("calibration", mem.data(), &mem.back());
  for (int i = 0; i < SIZE; i++) {
    mem[i]++;
  }
  for (int i = 0; i < SIZE; i++) {
    mem[i]--;
  }
  DUMP_STOP("calibration");

  int stats[5] = {};

  DUMP_START_SINGLE("vector_stats", mem.data(), &mem.back());
  DUMP_START_SINGLE("array_stats", stats, &stats[4]);
  for (int i = 0; i < SIZE; i++) {
    int j = rand()%SIZE;
    mem[j]++;
    stats[0]+=j;
  }
  stats[1] = stats[0]/SIZE;

  int curr = 0;
  for (int i = 0; i < SIZE; i++) {
    curr += mem[i];
    if (curr >= SIZE/2) {
      stats[2] = i;
      break;
    }
  }
  DUMP_STOP("vector_stats");
  DUMP_STOP("array_stats");

  std::cerr << "Sum: " << stats[0] << "\n" 
    << "Mean: " << stats[1] << "\n"
    << "Median: " << stats[2] << "\n";

  return 0;
}
