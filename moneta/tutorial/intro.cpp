#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include "../pin_tags.h"

constexpr int SIZE {1000};

std::uniform_int_distribution<int> distribution(0, SIZE-1);
std::default_random_engine engine;

//Defined after main
void mystery_a(std::vector<int> & a);
void mystery_b(std::vector<int> & b);
void mystery_c(std::vector<int> & c);
void mystery_d(std::vector<int> & d);
void mystery_e(std::vector<int> & e);
void mystery_f(std::vector<int> & f);
void mystery_g(std::vector<int> & g);
void mystery_h(std::vector<int> & h);
void fill_v(std::vector<int> & v);
void heapify(std::vector<int> & data, int n, int i);

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

  DUMP_START_SINGLE("vectors", &H.front(), &A.back());

  // A
  DUMP_START_SINGLE("A", &A.front(), &A.back());
  mystery_a(A);
  DUMP_STOP("A");

  // B
  DUMP_START_SINGLE("B", &B.front(), &B.back());
  mystery_b(B);
  DUMP_STOP("B");

  // C
  DUMP_START_SINGLE("C", &C.front(), &C.back());
  mystery_c(C);
  DUMP_STOP("C");

  // D
  DUMP_START_SINGLE("D", &D.front(), &D.back());
  mystery_d(D);
  DUMP_STOP("D");

  // E
  mystery_e(E);

  // F
  mystery_f(F);

  // G
  mystery_g(G);

  // H
  mystery_h(H);


  DUMP_STOP("vectors");
  return 0;
}


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

void mystery_a(std::vector<int> & a) {
  int u, v;
  for (int i = 1; i < SIZE; i++) {
    v = a[i];
    u = i-1;

    while (u >= 0 && a[u] > v) {
      a[u+1] = a[u];
      u--;
    }
    a[u+1] = v;
  }
}

void mystery_b(std::vector<int> & b) {
  int v;
  for (int i = 0; i < SIZE; i++) {
    int j = rand()%SIZE;
    b[j] = i*j;
  }
  for (int j = 0; j < SIZE*4; j++) {
    int i = j/4;
    b[i] += i*i;
    v+=b[i]+b[SIZE-i-1];
    b[SIZE-i-1] += i*i;
  }
  for (int i = 0; i < SIZE; i++) {
    int j = rand()%SIZE;
    b[j] = i*j;
  }
}

void mystery_c(std::vector<int> & c) {
  int v;
  for (int i = 0; i < SIZE-1; i++) {
    v = i;
    for (int j = i + 1; j < SIZE; j++) {
      if (c[j] < c[v]) {
        v = j;
      }
    }
    std::swap(c[v], c[i]);
  }
}

void mystery_d(std::vector<int> & d) {
  for (int i = SIZE/2 - 1; i >= 0; i--) {
    heapify(d, SIZE, i);
  }
  for (int i = SIZE - 1; i > 0; i--) {
    std::swap(d[0], d[i]);
    heapify(d, i, 0);
  }
}

void mystery_e(std::vector<int> & e) {
  for (int i = 0; i < SIZE; i+=SIZE/100) {
    e[i]=i*i;
  }
  for (int i = 0; i < SIZE*10; i++) {
    if (i%2 == 0) {
      e[SIZE-1]++;
    } else {
      e[0]++;
    }
  }
  for (int i = 0; i < SIZE; i+=SIZE/100) {
    e[i] = i*i;
  }
}

void mystery_f(std::vector<int> & f) {
  for (int i = 0; i < SIZE-17; i+=18) {
    for (int j = i; j < i+9; j++) {
      std::swap(f[j], f[j-17]);
    }
  }
  for (int i = 0; i < SIZE*10; i++) {
    if (i%2 == 0) {
      f[SIZE/2-100]++;
    } else {
      f[SIZE/2+100]++;
    }
  }
  for (int i = 0; i < SIZE-17; i+=18) {
    for (int j = i; j < i+9; j++) {
      std::swap(f[j], f[j-17]);
    }
  }
}

void mystery_g(std::vector<int> & g) {
  std::normal_distribution<double> norm_dist(SIZE/2, SIZE/10);
  for (int i = 0; i < SIZE*10; i++) {
    int j = std::min(std::max((int)norm_dist(engine), 0), SIZE-1);
    g[j] = i*j;
  }
}

void mystery_h(std::vector<int> & h) {
  for (int i = 0; i < SIZE-1; i++) {
    for (int j = 0; j < SIZE-i-1; j++) {
      if (h[j] > h[j+1]) {
        std::swap(h[j], h[j+1]);
      }
    }
  }
}

void fill_v(std::vector<int> & v) {
  for (int i = 0; i < SIZE; i++) {
    v[i] = distribution(engine);
  }
}