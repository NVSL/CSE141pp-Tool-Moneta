#ifndef MEMORYTRACE_PINTOOL_MACROS
#define MEMORYTRACE_PINTOOL_MACROS

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START_TAG(const char* tag, void* begin, void* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP_TAG(const char* tag) {}
extern "C" __attribute__ ((optimize("O0"))) void FLUSH_CACHE() {}

#endif
