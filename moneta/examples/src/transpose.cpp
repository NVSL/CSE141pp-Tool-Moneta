#include <random>
#include <vector>
#include <iostream>
#include "../../pin_tags.h"


const int M = 1000;
const int N = 100;

const double LowerB = 0;
const double UpperB = 1000;

int main(int argc, char *argv[]) {
  std::vector<std::vector<double>> E ( M, std::vector<double> (N, 0) ); // MxN // M >= N skinny
  std::vector<std::vector<double>> K ( N, std::vector<double> (M, 0) ); // NxM // Fat

  std::uniform_real_distribution<double> unif (LowerB, UpperB);
  std::default_random_engine re;

  DUMP_START("K", &K[0][0], &K[N-1][M-1], false);
  // Initialization
  for (int row = 0; row < N; ++row) {
    for (int col = 0; col < M; ++col) {
      K[row][col] = unif(re);
    }
  }
  DUMP_START("E", &E[0][0], &E[M-1][N-1], false);
  // Normal transpose - E = K.T
  for (int row = 0; row < M; ++row) {
    if (row >= 20 && row <= 40) {
      DUMP_START("k_t", LIMIT, LIMIT, true);
    }
    for (int col = 0; col < N; ++col) {
      E[row][col] = K[col][row];
    }
    if (row >= 20 && row <= 40) {
      DUMP_STOP("k_t");
    }
  }

  // Normal transpose - K = E.T
  for (int row = 0; row < N; ++row) {
    if (row >= 20 && row <= 40) {
      DUMP_START("e_t", LIMIT, LIMIT, true);
    }
    for (int col = 0; col < M; ++col) {
      K[row][col] = E[col][row];
    }
    if (row >= 20 && row <= 40) {
      DUMP_STOP("e_t");
    }
  }

  // 1/4 Transpose - E = K.T
  for (int row = 0; row < M/2; ++row) { // Top left part of E
    for (int col = 0; col < N/2; ++col) {
      E[row][col] = K[col][row];
    }
  }
  for (int row = 0; row < M/2; ++row) { // Top right part of E
    for (int col = N/2; col < N; ++col) {
      E[row][col] = K[col][row];
    }
  }
  for (int row = M/2; row < M; ++row) { // Bottom left part of E
    for (int col = 0; col < N/2; ++col) {
      E[row][col] = K[col][row];
    }
  }
  for (int row = M/2; row < M; ++row) { // Bottom right part of E
    for (int col = N/2; col < N; ++col) {
      E[row][col] = K[col][row];
    }
  }
  // Blocked
  int b_size = 8;
  for (int rr = 0; rr < M; rr += b_size) {
    for (int cc = 0; cc < N; cc += b_size) {
      for (int r = rr; r < M && r < rr + b_size; ++r) {
        for (int c = cc; c < N && c < cc + b_size; ++c) {
          E[r][c] = K[c][r];
        }
      }
    }
  }

  DUMP_STOP("E");
  DUMP_STOP("K");
  return 0;
}
