#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include "../../pin_tags.h"

constexpr int SIZE {1000};

std::uniform_int_distribution<int> distribution(0, SIZE-1);
std::default_random_engine engine;

void heapify(std::vector<int> & data, int n, int i){
  int largest = i;
  int l = 2*i +1;
  int r = 2*i +2;

  if( l< n && data[l] > data[largest]){
    largest = l;
  }

  if( r<n && data[r] > data[largest]){
    largest = r;
  }

  if(largest != i){
    std::swap(data[i], data[largest]);

    heapify(data, n, largest);
  }
}

void fill_v(std::vector<int> & v) {
  for (int i = 0; i < SIZE; i++) {
    v[i] = distribution(engine);
  }
}

int main() {
  std::vector<int> H (SIZE, 0);
  std::vector<int> B (SIZE, 0);
  std::vector<int> F (SIZE, 0);
  std::vector<int> D (SIZE, 0);
  std::vector<int> G (SIZE, 0);
  std::vector<int> C (SIZE, 0);
  std::vector<int> E (SIZE, 0);
  std::vector<int> A (SIZE, 0);

  fill_v(A);
  fill_v(B);
  fill_v(C);
  fill_v(D);
  fill_v(E);
  fill_v(F);
  fill_v(G);
  fill_v(H);

  int u, v;

  // A
  DUMP_START_SINGLE("A", &A.front(), &A.back());
  for (int i = 1; i < SIZE; i++) {
    v = A[i];
    u = i-1;

    while (u >= 0 && A[u] > v) {
      A[u+1] = A[u];
      u--;
    }
    A[u+1] = v;
  }
  DUMP_STOP("A");

  // B
  DUMP_START_SINGLE("B", &B.front(), &B.back());
  for (int i = 0; i < SIZE; i++) {
    int j = rand()%SIZE;
    B[j] = i*j;
  }
  for (int j = 0; j < SIZE*4; j++) {
    int i = j/4;
    B[i] += i*i;
    v+=B[i]+B[SIZE-i-1];
    B[SIZE-i-1] += i*i;
  }
  for (int i = 0; i < SIZE; i++) {
    int j = rand()%SIZE;
    B[j] = i*j;
  }
  DUMP_STOP("B");

  // C
  for (int i = 0; i < SIZE-1; i++) {
    v = i;
    for (int j = i + 1; j < SIZE; j++) {
      if (C[j] < C[v]) {
        v = j;
      }
    }
    std::swap(C[v], C[i]);
  }

  // D
  DUMP_START_SINGLE("D", &D.front(), &D.back());
  for (int i = SIZE/2 - 1; i >= 0; i--) {
    heapify(D, SIZE, i);
  }
  for (int i = SIZE - 1; i > 0; i--) {
    std::swap(D[0], D[i]);
    heapify(D, i, 0);
  }
  DUMP_STOP("D");


  // E
  for (int i = 0; i < SIZE; i+=SIZE/100) {
    E[i]=i*i;
  }
  for (int i = 0; i < SIZE*10; i++) {
    if (i%2 == 0) {
      E[SIZE-1]++;
    } else {
      E[0]++;
    }
  }
  for (int i = 0; i < SIZE; i+=SIZE/100) {
    E[i] = i*i;
  }

  // F
  DUMP_START_SINGLE("F", &F.front(), &F.back());
  for (int i = 0; i < SIZE-17; i+=18) {
    for (int j = i; j < i+9; j++) {
      std::swap(F[j], F[j-17]);
    }
  }
  for (int i = 0; i < SIZE*10; i++) {
    if (i%2 == 0) {
      F[SIZE/2-100]++;
    } else {
      F[SIZE/2+100]++;
    }
  }
  for (int i = 0; i < SIZE-17; i+=18) {
    for (int j = i; j < i+9; j++) {
      std::swap(F[j], F[j-17]);
    }
  }
  DUMP_STOP("F");

  // G
  DUMP_START_SINGLE("G", &G.front(), &G.back());
  std::normal_distribution<double> norm_dist(SIZE/2, SIZE/10);
  for (int i = 0; i < SIZE*10; i++) {
    int j = std::min(std::max((int)norm_dist(engine), 0), SIZE-1);
    G[j] = i*j;
  }
  DUMP_STOP("G");

  // H
  DUMP_START_SINGLE("H", &H.front(), &H.back());
  for (int i = 0; i < SIZE-1; i++) {
    for (int j = 0; j < SIZE-i-1; j++) {
      if (H[j] > H[j+1]) {
        std::swap(H[j], H[j+1]);
      }
    }
  }
  DUMP_STOP("H");

  

  return 0;
}
