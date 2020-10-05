#include <stdio.h>
#include <stdlib.h>
#include <bits/stdc++.h> 
#include "../../pin_tags.h" 


//Tag both programs
// Compile at -O0
// Generate and load traces for both programs - Qs i, ii
// Optimize col_major and try to improve the cache hit rate


int main() {
    int rows = 10000;
    int cols = 10000;
    int iterations = 10;
    int val = 1;

    int count = 0;
    int *arr = (int *)malloc(rows * cols * sizeof(int));  

    time_t start, end; 

    time(&start);
    for(int count = 0; count<iterations; count++){
        for(int col = 0; col < cols; col++) {
            for(int row = 0; row < rows; row++) {
                (*(arr + row*cols + col))++;
                val+=*(arr + row*cols + col);
            }
        }
    }
    time(&end); 

    double time_taken = double(end - start); 
    std::cout << "Time: " << time_taken << std::setprecision(5); 
    std::cout << " sec " << std::endl; 

    //printf("Val = %d\n",val);
    free(arr);  

}
