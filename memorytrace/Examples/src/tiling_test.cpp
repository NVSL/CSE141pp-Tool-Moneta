#include "pin_macros.h"
#include <iostream>
#include <stdlib.h>
#include <vector>

using namespace std;

#define SIZE 256
#define SIZE2 32

int main(int argc, char *argv[]){
	
    vector<vector<int>> scale(SIZE, vector<int> (SIZE));
    vector<int> values(SIZE2);

    for(int i = 0; i < SIZE; i++){
        for(int j = 0; j < SIZE; j++){
            scale[i][j] = (i + j) % 10;
        }
    }

    for(int i = 0; i < SIZE2; i++){
        values[i] = (i * SIZE);
    }


    FLUSH_CACHE();
    DUMP_ACCESS_START_TAG("scale", &scale[0][0], &scale[SIZE-1][SIZE-1]);

    for(int i = 0; i < SIZE2; i++){
        for(int x = 0; x < SIZE; x++){
            for(int y = 0; y < SIZE; y++){
                values[i] += scale[x][y];
            }
        }
    }

    DUMP_ACCESS_STOP_TAG("scale");

    cout << values[0] << endl;

}
