#include "../../pin_tags.h"
#include <iostream>
#include <random>
#include <cassert>
#include <vector>

constexpr int SIZE {1000};

int cutoff(int val) {
  return std::min(std::max(val, 0), SIZE-1);
}

int cutoff(double val) {
  return cutoff((int)val);
}

int main() {
  std::vector<int> mem (SIZE, 0);

  std::cerr << "Calibration\n";
  DUMP_START("calibration", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    mem[i]++;
  }
  DUMP_STOP("calibration");

  std::cerr << mem.size() << " " << mem.data() << " " << &mem.back() << "\n";

  std::cerr << "Testing rand()\n";
  DUMP_START("rand", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = rand()%SIZE;
    mem[j] = i*j;
  }
  DUMP_STOP("rand");

  std::default_random_engine gen;
  std::uniform_int_distribution<int> unif_dist(0, SIZE-1);

  std::cerr << "Testing unif()\n";
  DUMP_START("unif", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = unif_dist(gen);
    mem[j] = i*j;
  }
  DUMP_STOP("unif");

  std::binomial_distribution<int> bin_dist1(SIZE-1, .25);
  DUMP_START("binomial .25", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = bin_dist1(gen);
    mem[j] = i*j;
  }
  DUMP_STOP("binomial .25");

  std::binomial_distribution<int> bin_dist2(SIZE-1, .5);
  DUMP_START("binomial .5", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = bin_dist2(gen);
    mem[j] = i*j;
  }
  DUMP_STOP("binomial .5");

  std::binomial_distribution<int> bin_dist3(SIZE-1, .75);
  DUMP_START("binomial .75", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = bin_dist3(gen);
    mem[j] = i*j;
  }
  DUMP_STOP("binomial .75");

  std::geometric_distribution<int> geo_dist1(.01);
  DUMP_START("geometric .01", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(geo_dist1(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("geometric .01");

  std::geometric_distribution<int> geo_dist2(.1);
  DUMP_START("geometric .1", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(geo_dist2(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("geometric .1");

  std::geometric_distribution<int> geo_dist3(.5);
  DUMP_START("geometric .5", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(geo_dist3(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("geometric .5");

  std::geometric_distribution<int> geo_dist4(.9);
  DUMP_START("geometric .9", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(geo_dist4(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("geometric .9");

  std::normal_distribution<double> norm_dist1(SIZE/2, SIZE/1000);
  DUMP_START("normal 1/1000", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(norm_dist1(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("normal 1/1000");

  std::normal_distribution<double> norm_dist2(SIZE/2, SIZE/100);
  DUMP_START("normal 1/100", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(norm_dist2(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("normal 1/100");

  std::normal_distribution<double> norm_dist3(SIZE/2, SIZE/10);
  DUMP_START("normal 1/10", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(norm_dist3(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("normal 1/10");

  std::exponential_distribution<double> exp_dist1(1.0/SIZE);
  DUMP_START("exp 1/size", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(exp_dist1(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("exp 1/size");

  std::exponential_distribution<double> exp_dist2(0.5/SIZE);
  DUMP_START("exp 1/2size", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(exp_dist2(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("exp 1/2size");

  std::exponential_distribution<double> exp_dist3(0.25/SIZE);
  DUMP_START("exp 1/4size", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(exp_dist3(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("exp 1/4size");

  std::exponential_distribution<double> exp_dist4(2.0/SIZE);
  DUMP_START("exp 2/size", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(exp_dist4(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("exp 2/size");

  std::exponential_distribution<double> exp_dist5(4.0/SIZE);
  DUMP_START("exp 4/size", mem.data(), &mem.back(), false);
  for (int i = 0; i < SIZE; i++) {
    int j = cutoff(exp_dist5(gen));
    mem[j] = i*j;
  }
  DUMP_STOP("exp 4/size");


  return 0;
}
