SRC_DIR := ./Examples/src
EXE_DIR := ./Examples/build
SRC_FILES := $(wildcard $(SRC_DIR)/*.cpp)
EXECUTABLES := $(patsubst $(SRC_DIR)/%.cpp,%,$(SRC_FILES))


all: $(EXECUTABLES)

${EXECUTABLES}: % : $(SRC_DIR)/%.cpp
	g++ $< -o $(EXE_DIR)/$@

clean:
	@rm -rf $(EXE_DIR)/*
