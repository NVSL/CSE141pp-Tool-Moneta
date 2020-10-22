#include <iostream>
#include "../../pin_tags.h"

constexpr int N = 128;
constexpr int BLOCK = 16;

int main() {
  int *A = (int *)malloc(N * N * sizeof(int));
  int *B = (int *)malloc(N * N * sizeof(int));


  DUMP_START_SINGLE("A", A, A + N*N - 1);
  DUMP_START_SINGLE("B", B, B + N*N - 1);
  int sum = 0;
  for (int i = 0; i < 10; i++) {
    for (int rr = 0; rr < N; rr+=BLOCK) {
      for (int cc = 0; cc < N; cc+=BLOCK) {
        for (int row = rr; row < rr + BLOCK && row < N; row++) {
          for (int col = cc; col < cc + BLOCK && col < N; col++) {
            sum += (*(A + N*row + col)) + (*(B + N*col + row));
          }
        }
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
