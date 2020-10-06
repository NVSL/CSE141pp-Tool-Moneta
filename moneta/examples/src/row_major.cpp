#include <stdio.h>
#include <stdlib.h>
#include "../../pin_tags.h"


int main() {
  int rows = 10000;
  int cols = 10000;
  int iterations = 10;
  int val = 1;

  int count = 0;
  int *arr = (int *)malloc(rows * cols * sizeof(int));  

  for(int count = 0; count<iterations; count++){
    for(int row = 0; row < rows; row++) {
      for(int col = 0; col < cols; col++) {
        (*(arr + row*cols + col))++;
        val+=*(arr + row*cols + col);
      }
    }
  }
  printf("Val = %d\n",val);
  free(arr);  
  return 0;
}
