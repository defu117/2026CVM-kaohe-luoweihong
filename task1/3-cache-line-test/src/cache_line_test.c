#define _POSIX_C_SOURCE 200112L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define ARRAY_SIZE ((size_t)256 * 1024 * 1024)
#define REPEAT 8

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1000000000.0;
}

int main(int argc, char **argv) {
    int strides[] = {1, 2, 4, 8, 16, 32, 64, 128, 256};
    int stride_count = sizeof(strides) / sizeof(strides[0]);

    if (argc == 2) {
        strides[0] = atoi(argv[1]);
        stride_count = 1;
    }

    uint8_t *array = NULL;
    if (posix_memalign((void **)&array, (size_t)64, ARRAY_SIZE) != 0) {
        fprintf(stderr, "posix_memalign failed\n");
        return 1;
    }

    for (size_t i = 0; i < ARRAY_SIZE; i++) {
        array[i] = (uint8_t)(i & 0xff);
    }

    printf("stride_bytes,accesses,time_sec,ns_per_access,throughput_MB_s\n");

    volatile uint64_t sink = 0;

    for (int s = 0; s < stride_count; s++) {
        int stride = strides[s];
        size_t accesses_per_round = ARRAY_SIZE / stride;
        size_t total_accesses = accesses_per_round * REPEAT;

        double start = now_sec();

        for (int r = 0; r < REPEAT; r++) {
            for (size_t i = 0; i < ARRAY_SIZE; i += stride) {
                sink += array[i];
            }
        }

        double end = now_sec();
        double elapsed = end - start;
        double ns_per_access = elapsed * 1e9 / total_accesses;
        double throughput = ((double)total_accesses / (1024.0 * 1024.0)) / elapsed;

        printf("%d,%zu,%.6f,%.3f,%.2f\n",
               stride, total_accesses, elapsed, ns_per_access, throughput);
    }

    if (sink == 0xdeadbeef) {
        printf("sink=%llu\n", (unsigned long long)sink);
    }

    free(array);
    return 0;
}
