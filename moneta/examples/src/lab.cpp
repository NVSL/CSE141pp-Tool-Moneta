#include <iostream>
#include "../../pin_tags.h"

constexpr int N = 128;

int main() {
  int A[N][N];
  int B[N][N];

  int sum = 0;
  for (int row = 0; row < N; row++) {
    for (int col = 0; col < N; col++) {
      sum += A[row][col] + B[col][row];
    }
  }

  std::cout << "Final sum: " << sum << "\n";
  return 0;
}
