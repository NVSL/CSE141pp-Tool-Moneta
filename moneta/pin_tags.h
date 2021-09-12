#ifndef MONETA_PINTOOL_TAGS
#define MONETA_PINTOOL_TAGS
#include<cstdio>

extern "C" {

#define DUMP_START(tag, begin, end, create_new) TAG_START(tag, begin,end, create_new)
#define DUMP_STOP(tag) TAG_STOP(tag)
#define DUMP_START_ALL(tag, create_new) TAG_START_ALL(tag, create_new)
#define START_TRACE ENABLE_TRACING
#define STOP_TRACE DISABLE_TRACING

	__attribute__ ((optimize("O0"), weak)) void TAG_START(const char* tag, const void* begin, const void* end, bool create_new) {}
	__attribute__ ((optimize("O0"), weak)) void TAG_STOP(const char* tag) {}
 	__attribute__ ((optimize("O0"), weak)) void TAG_START_ALL(const char* tag, bool create_new) {TAG_START(tag, 0, (void*)-1, create_new);}
	__attribute__ ((optimize("O0"), weak)) void TAG_GROW(const char* tag, const void* begin, const void* end){}
	__attribute__ ((optimize("O0"), weak)) void M_NEW_TRACE(const char* name) {}
	__attribute__ ((optimize("O0"), weak)) int GET_THREAD_ID() { return 0;}
	
	__attribute__ ((optimize("O0"), weak)) void M_START_TRACE(bool one, bool two) {}
	__attribute__ ((optimize("O0"), weak)) void M_STOP_TRACE(bool one, bool two) {}
	
	__attribute__ ((optimize("O0"), weak)) void FLUSH_CACHE() {}
	__attribute__ ((weak))	void START_TRACE() {
		M_START_TRACE(true, true);
	}
	__attribute__ ((weak)) void STOP_TRACE() {
		M_STOP_TRACE(true, true);
	}
	
	__attribute__ ((weak)) void NEW_TRACE(const char *s) {
		M_NEW_TRACE(s);
	}
	
	
}
constexpr void* LIMIT {0};

#endif

