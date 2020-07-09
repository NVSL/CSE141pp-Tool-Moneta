#include "pin_macros.h"
#include <vector>

using namespace std;

#define SIZE1 16000
#define SIZE2 32000
#define SIZE3 8000

int main(){

    vector<int> test1(SIZE1, 0);
    vector<int> test2(SIZE2, 0);
    vector<int> test3(SIZE3, 0);


    FLUSH_CACHE();
    DUMP_ACCESS_START_TAG("test1", &test1[0], &test1[SIZE1]);
    DUMP_ACCESS_START_TAG("test2", &test2[0], &test2[SIZE2]);
    DUMP_ACCESS_START_TAG("test3", &test3[0], &test3[SIZE3]);


    for(int i = 0; i < 3000; i++){
        test1[i]++;
    }

    for(int i = 0; i < 6000; i++){
        test2[i]++;
    }

    for(int i = 0; i < 2000; i++){
        test3[i]++;
    }

}
