SRC_DIR := ./examples/src
EXE_DIR := ./examples/build
SRC_FILES := $(wildcard $(SRC_DIR)/*.cpp)
EXECUTABLES := $(patsubst $(SRC_DIR)/%.cpp,%,$(SRC_FILES))


all: $(EXECUTABLES)

${EXECUTABLES}: % : $(SRC_DIR)/%.cpp
	g++ $< -O0 -o $(EXE_DIR)/$@

clean:
	@rm -rf $(EXE_DIR)/*
