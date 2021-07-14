.PHONY:all
all: build install
setup: all

.PHONY:build
build:
	$(MAKE) -C moneta/src
	$(MAKE) -C setup

.PHONY: install
install:
	pip install -e .
