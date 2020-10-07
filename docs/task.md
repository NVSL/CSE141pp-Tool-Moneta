# Optimizing Cache Hit Rate

We will be examining the differences between a row major and column major traversal of a matrix,
and how the cache hit rate varies by key parameters of the cache.

Provided is the code for both row major (`row_major.cpp`) and column major (`col_major.cpp`)
which are, for the purposes of this lab, mostly read-only. There's no need to modify them except for
adding tags, if necessary.
