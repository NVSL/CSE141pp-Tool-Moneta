
default: libmoneta.so

CPPFLAGS=-I.. -Wall -Werror -fPIC

libmoneta.o: ../pin_tags.h
libmoneta.so: libmoneta.o
	gcc -shared -o $@ $^

.PHONY: clean
clean:
	rm -rf *.o libmoneta.so

