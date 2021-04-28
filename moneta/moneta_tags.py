import ctypes
import pathlib

#libname = pathlib.Path().absolute() / "libmoneta.so"
libname = "libmoneta.so"
c_lib = ctypes.CDLL(libname)

DUMP_START_ALL=lambda tag, create_new :c_lib.DUMP_START_ALL(ctypes.c_char_p(tag.encode('utf-8')), create_new)
DUMP_STOP=lambda tag: c_lib.DUMP_STOP(ctypes.c_char_p(tag.encode('utf-8')))
FLUSH_CACHE=c_lib.FLUSH_CACHE
START_TRACE=c_lib.START_TRACE
STOP_TRACE=c_lib.STOP_TRACE
NEW_TRACE=lambda name :c_lib.NEW_TRACE(ctypes.c_char_p(name.encode('utf-8')))
