#include "../../pin_tags.h"
#include <iostream>
#include <stdlib.h>
#include <vector>
#include <string>

using namespace std;

#define SIZE 256
#define SIZE2 32

int main(int argc, char *argv[]){
	
    int TILE_SIZE = SIZE;

    try{
        if(argc > 1){
            TILE_SIZE = max(1, stoi(argv[1]));
        }
    } catch(...) {
        cerr << "Invalid Tile Size\n";
        exit(-1);
    }

    cout << "Tile Size: " << TILE_SIZE << endl;

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
    DUMP_START("scale", &scale[0][0], &scale[SIZE-1][SIZE-1], false);


    for(int xx = 0; xx < SIZE; xx += TILE_SIZE){
        for(int i = 0; i < SIZE2; i++){
            for(int x = xx; x < SIZE && x < xx + TILE_SIZE; x++){
                for(int y = 0; y < SIZE; y++){
                    values[i] += scale[x][y];
                }
            }
        }
    }

    DUMP_STOP("scale");

    cout << values[0] << endl;

}
