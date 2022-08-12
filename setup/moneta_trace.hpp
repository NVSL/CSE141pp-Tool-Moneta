#ifndef MONETA_TRACE_INCLUDED
#define MONETA_TRACE_INCLUDED

// Access type
enum { 
	READ_HIT=1, WRITE_HIT,
	READ_CAP_MISS, WRITE_CAP_MISS,
	READ_COMP_MISS, WRITE_COMP_MISS 
};

// Cache Access type
enum {
	HIT=1, CAP_MISS, COMP_MISS
};


struct trace_entry {
	//uint64_t index;
	uint64_t address;
	uint8_t acc;
	uint8_t threadid;
	//	uint8_t layer;
};

#endif
