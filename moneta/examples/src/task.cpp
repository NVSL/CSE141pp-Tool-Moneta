#include <stdio.h>
#include <stdlib.h>
#include "../../pin_tags.h"


int main() {
  int rows = 256;
  int cols = 256;
  int iterations = 10;
  int val = 1;

  int count = 0;
  int *arr = (int *)malloc(rows * cols * sizeof(int));  

  for(int count = 0; count<iterations; count++){
    DUMP_START_MULTI("iteration", arr, arr + rows*cols-1);
    for(int col = 0; col < cols; col++) {
      for(int row = 0; row < rows; row++) {
        (*(arr + row*cols + col))++;
        val+=*(arr + row*cols + col);
      }
    }
    DUMP_STOP("iteration");
  }
  printf("Val = %d\n",val);
  free(arr);  
  return 0;
}
