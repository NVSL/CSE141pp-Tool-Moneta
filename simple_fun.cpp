#include <iostream>

extern "C" void swap(int* begin, int * end) {
	int temp = *end;
	*end = *begin;
	*begin = temp;
	return;
}

int main(int argc, char *argv[]) {
	int a = 10;
	int b = 20;
	printf("%p - %p\n", &a, &b);
	swap(&a, &b);
	return 0;
}
