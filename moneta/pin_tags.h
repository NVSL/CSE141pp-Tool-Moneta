#ifndef MONETA_PINTOOL_TAGS
#define MONETA_PINTOOL_TAGS
#include<cstdio>

extern "C" {
  __attribute__ ((optimize("O0"))) void DUMP_START(const char* tag, const void* begin, const void* end, bool create_new) {}
	__attribute__ ((optimize("O0"))) void DUMP_START_ALL(const char* tag, bool create_new) {DUMP_START(tag, 0, (void*)-1, create_new);}
  __attribute__ ((optimize("O0"))) void DUMP_STOP(const char* tag) {}

  __attribute__ ((optimize("O0"))) void M_START_TRACE(bool one, bool two) {}

  __attribute__ ((optimize("O0"))) void FLUSH_CACHE() {}
  void START_TRACE() {
    M_START_TRACE(true, true);
  }

}
constexpr void* LIMIT {0};

#endif

