#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#define SIZE   (size_t)100E9
int main()
{
	char *big = malloc(SIZE);

	if (big == NULL) {
		printf("Failed\n");
		return 0;
	}

	printf("We have the memory!\n");

	sleep(3);

	big[0] = 1;
	big[SIZE - 1] = 1;

	printf("We wrote to it\n");

	sleep(3);

	printf("Let's write some more!\n");

	for (size_t i = 0; i < SIZE; i++) {
		if ((i & 0x3fffffff) == 0)
			printf("%zd GB\n", i >> 30);

		big[i] = i & 255;
	}

	printf("It worked\n");

	return 0;
}

