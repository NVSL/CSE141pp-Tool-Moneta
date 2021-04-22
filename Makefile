.PHONY:all
all: build install

.PHONY:build
build:
	$(MAKE) -C moneta/src

.PHONY: install
install:
	pip install -e .
