#include "pin_macros.h"
#include <vector>

using namespace std;

int main(){

    vector<int> test1(5, 0);
    vector<int> test2(5, 0);
    vector<int> test3(5, 0);
    vector<int> test4(5, 0);
    vector<int> test5(5, 0);
    vector<int> test6(5, 0);
    vector<int> test7(5, 0);
    vector<int> test8(5, 0);
    vector<int> test9(5, 0);
    vector<int> test10(5, 0);
    vector<int> test11(5, 0);
    vector<int> test12(5, 0);
    vector<int> test13(5, 0);
    vector<int> test14(5, 0);
    vector<int> test15(5, 0);


    FLUSH_CACHE();
    DUMP_ACCESS_START_TAG("test1", &test1[0], &test1[4]);
    DUMP_ACCESS_START_TAG("test2", &test2[0], &test2[4]);
    DUMP_ACCESS_START_TAG("test3", &test3[0], &test3[4]);
    DUMP_ACCESS_START_TAG("test4", &test4[0], &test4[4]);
    DUMP_ACCESS_START_TAG("test5", &test5[0], &test5[4]);
    DUMP_ACCESS_START_TAG("test6", &test6[0], &test6[4]);
    DUMP_ACCESS_START_TAG("test7", &test7[0], &test7[4]);
    DUMP_ACCESS_START_TAG("test8", &test8[0], &test8[4]);
    DUMP_ACCESS_START_TAG("test9", &test9[0], &test9[4]);
    DUMP_ACCESS_START_TAG("test10", &test10[0], &test10[4]);
    DUMP_ACCESS_START_TAG("test11", &test11[0], &test11[4]);
    DUMP_ACCESS_START_TAG("test12", &test12[0], &test12[4]);
    DUMP_ACCESS_START_TAG("test13", &test13[0], &test13[4]);
    DUMP_ACCESS_START_TAG("test14", &test14[0], &test14[4]);
    DUMP_ACCESS_START_TAG("test15", &test15[0], &test15[4]);

    for(int i = 0; i < 5; i++){
        test1[i]++;
        test2[i]++;
        test3[i]++;
        test4[i]++;
        test5[i]++;
        test6[i]++;
        test7[i]++;
        test8[i]++;
        test9[i]++;
        test10[i]++;
        test11[i]++;
        test12[i]++;
        test13[i]++;
        test14[i]++;
        test15[i]++;

    }

}
