#ifndef MONETA_PINTOOL_TAGS
#define MONETA_PINTOOL_TAGS

extern "C" {
  __attribute__ ((optimize("O0"))) void DUMP_START(const char* tag, const void* begin, const void* end, bool create_new) {}
  __attribute__ ((optimize("O0"))) void DUMP(const char* tag, bool create_new) {}
  __attribute__ ((optimize("O0"))) void DUMP_STOP(const char* tag) {}

  __attribute__ ((optimize("O0"))) void FLUSH_CACHE() {}
}
constexpr void* LIMIT {0};

#endif
