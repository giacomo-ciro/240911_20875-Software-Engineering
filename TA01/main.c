#include <stdio.h>

int main(int argc, char **argv) {
    printf("Test\n");
    printf("%d\n", argc);
    if (argc > 0) {
        printf("%s\n", argv[0]);
    } else {
        printf("No arguments provided.\n");
    }
    return 0;
}
