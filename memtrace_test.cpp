#include <bits/stdc++.h>
using namespace std;

#define SIZE (int)100000

long int loopArr(int arr[]){
    long int tester = 3;
    for(int i = 0; i < SIZE; i++){
        tester += arr[i];
    }
    return tester;
}

int main() {
	int arr[SIZE];
	int sum = 0;
	for(int i = 0; i < SIZE; i++) {
		arr[i] = i;
	}
	
    sum = loopArr(arr) % 10;

    return sum;
}
