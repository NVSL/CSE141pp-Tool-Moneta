# Optimizing Cache Hit Rate

We will be examining the differences between a row major and column major traversal of a matrix,
and how the cache hit rate varies based on key parameters of the cache.

Provided is the code for both row major (`row_major.cpp`) and column major (`col_major.cpp`)
which are, for the purposes of this lab, mostly read-only. There's no need to modify them except for
adding tags, if necessary.

Ensure you have followed the **Getting Started** guide to get the container and code ready.

## Tasks to Perform

### Inspect The Code

There are two source files of importance:
1. `row_major.cpp` - A reference of a high hit rate program
2. `col_major.cpp` - The program whose cache you will change to increase the cache hit rate

Make sure you are familiar with the behavior of these programs

### Run Row Major

To get you started, we will walk through the initial setup to get a sense of the goal for this lab


Compile `row_major.cpp`
`g++ -O4 row_major.cpp -o row_major`

**Note** Tags can make the analysis here easier but we will start with just a full trace

Open up the Moneta notebook

**IMPORTANT** We'll be using a 256 KB cache which is also the default

Fill in the path to the executable  

Fill in enough number of lines to get at least two iterations of the outer loop (we used 100 million which is not the default)  

Name it "row_major"  

Select full trace  

Select start from main since we are focusing on the accesses in main  

Hit generate  

Load the trace  

With these very large arrays we find they are allocated near the top of the heap area, you should see a large horizontal line in the plot (ours was at the top):  
<img src="../../assets/InitialRowMajor.png" alt="RowMajorZoomedOut" width="400px">  

Zoom into the top line with zoom selection  
Keep zooming to that rectangle until you see something like this:  
<img src="../../assets/RowMajor.png" alt="RowMajorZoomedIn" width="400px">  
<hr>  

**IMPORTANT** If at any time the kernel crashes, ensure you have 4-8 GB for Docker. Also, you may attempt the lab with one iteration or if the problem persists, reduce the size of the array by a tenth  
<hr>

Open up the stats panel in the legend and record the current view stats noting the cache hit rate. This is the maximum hit rate for linear accesses with the default cache parameters.  

Since the program revolves entirely around just these accesses, the total stats should have similar rates, so zooming in is not necessary

### Increase Hit Rate of Column Major

To complete this lab, you need to change the cache parameters (cache lines and block size) when running `col_major.cpp` to try to hit (or beat!) row major's hit rate

<hr>

#### Rules
* Do not modify any of the interal structure of either program
* You may tag these programs to make zooming and analyzing easier
* The upper limit for the cache is 256 KB
* Generate enough accesses for at least one iteration

### Recommendations
* Stick to the format we used for row major:
* Trace from main
* Use multiples of 2 for the cache parameters
* Compare how far each consecutive access is for row major vs col major


