
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include "hdf5_pin.cpp"

void convert(const char* csvFileName, const char* h5FileName){
	
	createFile(h5FileName);

	std::fstream fin;
	fin.open(csvFileName);

	std::vector<std::string> row;
	std::string line, word, temp;

	int tag;
	char rw;
	unsigned long long addr;
	while(fin>>temp){
		
		row.clear();

		std::getline(fin, line);

		std::stringstream s(line);

		while(std::getline(s, word, ',')){
			row.push_back(word);
		}

		//these assignments can change depending on order of data in csv file
		tag = std::stoi(row[0]);
		rw = std::stoi(row[1]);
		addr = std::stoull(row[2]);

		writeData(addr, rw, tag);
	}

	flushData();
	closeFile();

	fin.close();

}

