#include <bits/stdc++.h>
using namespace std;

#define SIZE (int)1e2
#define SIZE2 (int)1e4
int main() {
	vector<int> arr(SIZE2);
	for(int i = 0; i < SIZE; i++) 
		for(int j = 0; j < SIZE2; j++) 
			arr[j] = j;
	
	return 0;
}
