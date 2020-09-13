#ifndef MONETA_PINTOOL_TAGS
#define MONETA_PINTOOL_TAGS

extern "C" {
  __attribute__ ((optimize("O0"))) void _DUMP_START_MULTI(const char* tag, const void* begin, const void* end, bool _t) {}
  __attribute__ ((optimize("O0"))) void _DUMP_STOP(const char* tag, bool _t) {}

  __attribute__ ((optimize("O0"))) void DUMP_START_SINGLE(const char* tag, const void* begin, const void* end) {}
  void DUMP_START_MULTI(const char* tag, const void* begin, const void* end) {
    _DUMP_START_MULTI(tag, begin, end, true);
  }
  __attribute__ ((optimize("O0"))) void DUMP_START(const char* tag) {}
  void DUMP_STOP(const char* tag) {
    _DUMP_STOP(tag, true);
  }
  __attribute__ ((optimize("O0"))) void FLUSH_CACHE() {}
}
constexpr void* LIMIT {0};

#endif
