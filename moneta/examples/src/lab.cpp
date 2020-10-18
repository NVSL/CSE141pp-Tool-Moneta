#include <iostream>
#include "../../pin_tags.h"

constexpr int N = 128;

int main() {
  int *A = (int *)malloc(N * N * sizeof(int));
  int *B = (int *)malloc(N * N * sizeof(int));

  int sum = 0;
  for (int row = 0; row < N; row++) {
    DUMP_START_MULTI("iteration", A, B + N*N-1);
    for (int col = 0; col < N; col++) {
      sum += (*(A + N*row + col)) + (*(B + N*col + row));
    }
    DUMP_STOP("iteration");
  }

  std::cout << "Final sum: " << sum << "\n";
  free(A);
  free(B);
  return 0;
}
