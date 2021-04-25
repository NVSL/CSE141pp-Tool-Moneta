#ifndef MONETA_PINTOOL_TAGS
#define MONETA_PINTOOL_TAGS
#include<cstdio>

extern "C" {
#define VOLATILE_NOP volatile asm{nop}
	
	__attribute__ ((optimize("O0"))) void DUMP_START(const char* tag, const void* begin, const void* end, bool create_new) {VOLATILE_NOP;}
	__attribute__ ((optimize("O0"))) void M_NEW_TRACE(const char* name) {VOLATILE_NOP;}
	__attribute__ ((optimize("O0"))) void DUMP_START_ALL(const char* tag, bool create_new) {DUMP_START(tag, 0, (void*)-1, create_new);}
	__attribute__ ((optimize("O0"))) void DUMP_STOP(const char* tag) {VOLATILE_NOP;}
	
	__attribute__ ((optimize("O0"))) void M_START_TRACE(bool one, bool two) {VOLATILE_NOP;}
	__attribute__ ((optimize("O0"))) void M_STOP_TRACE(bool one, bool two) {VOLATILE_NOP;}
	
	__attribute__ ((optimize("O0"))) void FLUSH_CACHE() {VOLATILE_NOP;}
	void START_TRACE() {
		M_START_TRACE(true, true);
	}
	void STOP_TRACE() {
		M_STOP_TRACE(true, true);
	}
	
	void NEW_TRACE(const char *s) {
		M_NEW_TRACE(s);
	}
	
}
constexpr void* LIMIT {0};

#endif

