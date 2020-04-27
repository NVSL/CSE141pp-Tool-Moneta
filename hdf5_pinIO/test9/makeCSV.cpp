#include <fstream>
#include <string>
#include <iostream>

int main(){
	std::ofstream myfile("file.txt");
	for(int count = 0; count<1000000; count++){
		int count1 = count+1;
		int count2 = count+2;
		std::string line = "" + std::to_string(count) + "," + std::to_string(count1) 
			+ "," +std::to_string(count2) + "\n";
		myfile << line;
	}	
	myfile.close();
}
