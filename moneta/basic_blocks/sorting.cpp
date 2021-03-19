/* Algorithms taken from GeeksforGeeks
 * Bubble sort: https://www.geeksforgeeks.org/bubble-sort/
 * Selection Sort: https://www.geeksforgeeks.org/selection-sort/
 * Insertion Sort: https://www.geeksforgeeks.org/insertion-sort/
 * Heap Sort: https://www.geeksforgeeks.org/heap-sort/
*/


#include <iostream>
#include <stdlib.h>

using namespace std;

constexpr int SIZE {1000};
__attribute__ ((optimize("O0"))) void DUMP_STOP() {}
__attribute__ ((optimize("O0"))) void DUMP_START(int a) {}


void bubbleSort(int data[], int n){
	
	for(int i=0; i<n-1; i++){
		for(int j =0; j<n-i-1; j++){
			if(data[j] > data[j+1]){
				swap(data[j], data[j+1]);
			}
		}
	}
}

void insertionSort(int data[], int n){
	int i, key, j;
	for(i=1; i<n; i++){
		key = data[i];
		j= i-1;

		while(j>=0 && data[j] > key){
			data[j+1] = data[j];
			j--;
		}
		data[j+1] = key;
	}
}

void heapify(int data[], int n, int i){
	int largest = i;
	int l = 2*i +1;
	int r = 2*i +2;

	if( l< n && data[l] > data[largest]){
		largest = l;
	}

	if( r<n && data[r] > data[largest]){
		largest = r;
	}

	if(largest != i){
		swap(data[i], data[largest]);

		heapify(data, n, largest);
	}
}


void heapSort( int data[], int n){
	
	for(int i = n/2 -1; i>=0; i--){
		heapify(data, n, i);
	}

	for(int i=n-1; i>0; i--){
		swap(data[0], data[i]);

		heapify(data, i, 0);
	}
}

void selectionSort(int data[], int n){
	int min_idx;
	for(int i=0; i<n-1; i++){
		min_idx = i;
		for(int j=i+1; j<n; j++){
			if(data[j]<data[min_idx]){
				min_idx = j;
			}
		}
		swap(data[min_idx], data[i]);
	}
}

int main(int argc, char *argv[]){
	
	int bubble[SIZE];
	int heap[SIZE];
	int selection[SIZE];
	int insertion[SIZE];

	for(int i=0; i<SIZE; i++){
		bubble[i] = rand();
		heap[i] = bubble[i];
		selection[i] = bubble[i];
		insertion[i] = bubble[i];
		//cout<<dat3a[i]<<", ";
	}
	DUMP_START(0);
	//cout<<"\n";
	//BUBBLE
	
	bubbleSort(bubble, SIZE);
	
	
	//INSERTION
	
	insertionSort(insertion, SIZE);
	
	
	//HEAP
	
	heapSort(heap, SIZE);
	

	//SELECTION	
	
	selectionSort(selection, SIZE);
	DUMP_STOP();
	
	

	/* Print Sorted array

	for(int i =0; i<size;i++){
		cout<<data[i]<<", ";
	}
	cout<<"\n";
	*/
}
