rm functiontrace.out_mem.out
time pin -t pintools/$1 -- programs/$2
wc functiontrace.out_mem.out
