#include <iostream>
#include "../../pin_tags.h"

constexpr int N = 128;

int main() {
  int *A = (int *)malloc(N * N * sizeof(int));
  int *B = (int *)malloc(N * N * sizeof(int));


  DUMP_START_SINGLE("A", A, A + N*N - 1);
  DUMP_START_SINGLE("B", B, B + N*N - 1);
  int sum = 0;
  for (int i = 0; i < 10; i++) {
    for (int row = 0; row < N; row++) {
      for (int col = 0; col < N; col++) {
        sum += (*(A + N*row + col)) + (*(B + N*col + row));
      }
    }
  }
  DUMP_STOP("A");
  DUMP_STOP("B");

  std::cout << "Final sum: " << sum << "\n";
  free(A);
  free(B);
  return 0;
}
