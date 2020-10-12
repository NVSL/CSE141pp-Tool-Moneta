# Analyzing Cache Hit Rate

In this lab, you will be analyzing and eventually optimizing a transpose sum operation using Moneta to guide you.

### Software and Environment

1. If you haven't already, check the Getting Started guide in this project and ensure the environment is working by following the tutorial.
2. For this lab, `lab.cpp` provides the code for a pair-wise sum of a square matrix and another transposed square matrix.

## Tasks to Perform

You will be answering the following questions, as you work through this lab.

### Questions

1. What is the baseline hit rate for the entire operation (the outermost loop)?
2. What is the miss rate for one iteration of the outer loop?
3. Does doubling the block size affect the miss rate? Why/why not?
4. Does doubling the number of cache lines affect the miss rate? Why/why not?
5. How many cache lines are used by the array `A` during one iteration of the row loop?
6. What about `B`?
7. How would you modify the code to minimize the total miss rate?

### Inspect the Code

You need to get acquainted with the code in order to optimize it.

There are two 128x128 2D arrays, `A` and `B`. The entire operation can be summarized by 
> sum(A + B.T)

where `sum()` adds up all the values of the matrix.

We will use Moneta to gather the answers.

### Constraints
- Unless otherwise stated, use a cache with 128 lines and a 64-byte block size.
- Compile the program with `-O4`
- Make sure to get the rates for just the accesses to `A` and `B`
- `FLUSH_CACHE` is not needed and using it could result in far worse hit rates

## Tips and Guidelines
Several features of Moneta can come in handy while completing this lab.  

### Tagging
Initially, adding tags to the source code can help orient the user by quickly bringing up the locations of the arrays in the traces.

**DUMP_START_SINGLE** - This function can be useful to tag where the entire array such as `A` is located.  
> **Note:** The first element of `A` has the address `A` and the last element is pointed to by `A + N * N - 1`

**DUMP_START_MULTI** - Separate calls to this function create new tags making locating specific iterations of nested loops straightforward.
> **Note:** Tags are 0-indexed so `DUMP_START_MULTI("loop", ...)` results in `loop0, loop1, ...`

### Analyzing
The UI contains features to access these tags.

**Tags** - The Tags panel contains any tags Moneta picks up. Each tag allows you to zoom in to the region and on hover displays region stats

**Stats** - Current stats in the Stats panel can display the rates of the entire operation if both arrays appear in the plot.

### Other
- Feel free to create lots of traces with meaningful names to keep track of your modifications
- Start with a full trace and track from main to find the arrays manually, if the tags don't work
- When changing cache parameters, think about how much space the arrays take (`int`s are 4 bytes)

