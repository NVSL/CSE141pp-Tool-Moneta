#include <vector>
#include <cstdlib>
#include <iostream>
#include "pin_tags.h"
#include <algorithm>
#include <random>


using namespace std;

#define SIZE 10000000
#define R_MIN 100
#define R_MAX 500

int main() {

    vector<int> arr1(SIZE, 1);
    vector<int> arr7(SIZE, 1);
    vector<int> arr3(SIZE, 1);
    vector<int> arr5(SIZE, 1);
    vector<int> arr2(SIZE, 1);
    vector<int> arr8(SIZE, 1);
    vector<int> arr4(SIZE, 1);
    vector<int> arr6(SIZE, 1);

    vector<int*> starts = {&arr1[0], &arr2[0],&arr3[0],&arr4[0],&arr5[0],&arr6[0],&arr7[0],&arr8[0]};
    vector<int*> ends = {&arr1[SIZE-1], &arr2[SIZE-1],&arr3[SIZE-1],&arr4[SIZE-1],&arr5[SIZE-1],&arr6[SIZE-1],&arr7[SIZE-1],&arr8[SIZE-1]};

    int* startPtr = *min_element(starts.begin(), starts.end());
    int* endPtr =  *max_element(ends.begin(), ends.end());
    int sectionSize;


    DUMP_START_SINGLE("Scavenger Hunt", startPtr, endPtr);


    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr1[10000] = 0;
    }
    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr2[50000] = 0;
    }
    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr3[100000] = 0;
    }
    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr4[500000] = 0;
    }



    sectionSize = (rand() % R_MAX + R_MIN) / 3;
    for(int i = 2500000; i < 2500000 + sectionSize; i++){
        arr5[i] = 0;
    }
    for(int i = 0; i < sectionSize/2; i++){
        arr5[2500000] = 0;
        arr5[2500000 + sectionSize] = 0;
    }
    for(int i = 2500000; i < 2500000 + sectionSize; i++){
        arr5[i] = 0;
    }



    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr6[0] = 0;
    }
    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr7[5000000] = 0;
    }
    sectionSize = rand() % R_MAX + R_MIN;
    for(int i = 0; i < sectionSize; i++){
        arr8[SIZE-1] = 0;
    }

    DUMP_STOP("Scavenger Hunt");
}

