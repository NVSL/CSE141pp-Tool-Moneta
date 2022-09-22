.PHONY:all
all: build install
setup: all

.PHONY: setup
setup: all
#	python -m pip install -r setup/requirements.txt

.PHONY:build
build:
	$(MAKE) -C moneta/src
	$(MAKE) -C setup

.PHONY: install
install:
#	/opt/conda/bin/pip install -r setup/requirements.txt
	/opt/conda/bin/pip install -e .
