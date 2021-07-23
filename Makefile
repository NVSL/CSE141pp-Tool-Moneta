.PHONY:all
all: build install
setup: all

.PHONY:build
build:
	$(MAKE) -C moneta/src
	$(MAKE) -C setup

.PHONY: install
install:
	pip install -r setup/requirements.txt
	pip install -e .
# this is a hack to make notebook use the whole browser window.
	echo ".container{width: 100%;}" >> /opt/conda/lib/python3.7/site-packages/notebook/static/custom/custom.css 
