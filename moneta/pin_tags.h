#ifndef MONETA_PINTOOL_TAGS
#define MONETA_PINTOOL_TAGS

extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_START_TAG(const char* tag, const void* begin, const void* end) {}
extern "C" __attribute__ ((optimize("O0"))) void DUMP_ACCESS_STOP_TAG(const char* tag) {}
extern "C" __attribute__ ((optimize("O0"))) void FLUSH_CACHE() {}
constexpr void* LIMIT {0};

#endif
