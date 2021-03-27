#include "../../pin_tags.h"
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
    DUMP_START("test1", &test1[0], &test1[4], false);
    DUMP_START("test2", &test2[0], &test2[4], false);
    DUMP_START("test3", &test3[0], &test3[4], false);
    DUMP_START("test4", &test4[0], &test4[4], false);
    DUMP_START("test5", &test5[0], &test5[4], false);
    DUMP_START("test6", &test6[0], &test6[4], false);
    DUMP_START("test7", &test7[0], &test7[4], false);
    DUMP_START("test8", &test8[0], &test8[4], false);
    DUMP_START("test9", &test9[0], &test9[4], false);
    DUMP_START("test10", &test10[0], &test10[4], false);
    DUMP_START("test11", &test11[0], &test11[4], false);
    DUMP_START("test12", &test12[0], &test12[4], false);
    DUMP_START("test13", &test13[0], &test13[4], false);
    DUMP_START("test14", &test14[0], &test14[4], false);
    DUMP_START("test15", &test15[0], &test15[4], false);

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
    DUMP_STOP("test1");
    DUMP_STOP("test2");
    DUMP_STOP("test3");
    DUMP_STOP("test4");
    DUMP_STOP("test5");
    DUMP_STOP("test6");
    DUMP_STOP("test7");
    DUMP_STOP("test8");
    DUMP_STOP("test9");
    DUMP_STOP("test10");
    DUMP_STOP("test11");
    DUMP_STOP("test12");
    DUMP_STOP("test13");
    DUMP_STOP("test14");
    DUMP_STOP("test15");
}
