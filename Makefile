.PHONY:all
all: build install

.PHONY: setup
setup: all
	python -m pip install -r setup/requirements.txt

.PHONY:build
build:
	$(MAKE) -C moneta/src

.PHONY: install
install:
	python -m pip install -e .

#/opt/conda/bin/python `which jupyter-notebook` --allow-root .
