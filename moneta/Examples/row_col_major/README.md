# Notes

Full Trace: 

Row_major:  
at 4096 cache lines 64 block size and 10 million lines --> hits: 99.20%  
at 4096 cache lines 32 block size and 10 million lines --> hits: 98.62%  
at 2048 cache lines 32 block size and 10 million lines --> hits: 98.37%  

Col_major:   
at 4096 cache lines 64 block size and 10 million lines --> hits: 99.20%  
at 4096 cache lines 32 block size and 10 million lines --> hits: 98.62%  
at 2048 cache lines 32 block size and 10 million lines --> hits: 98.37%  

  
I am assuming the stats were the same for boths because it is not large enough and so the arrays fit within the array  

Tagged:  

Col_major  
at 4096 cache lines 64 block size and 10 million lines --> hits:   
    --> was not able to test because the tags were not working for me, it was always the pin signal 11 situation, pushed with what I had tried out!