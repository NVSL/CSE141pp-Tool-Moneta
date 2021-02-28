#include <iostream>
#include "../../pin_tags.h"

#define NA 100
#define NB 100
#define NC 100

main(){
	
   int data1[NA][NB], data2[NB][NC], result[NA][NC];

   std::cout<<"MATRIX 1:";   
   for(int i = 0; i<NA; i++){
      std::cout<<"\n[";
      for(int j=0; j<NB;j++){
         data1[i][j] = i+j;
	 std::cout<<data1[i][j]<<", ";
      }
      std::cout<<"]";
   }
   std::cout<<"\n";
   
   std::cout<<"\nMATRIX 2:";   
   for(int i = 0; i<NA; i++){
      std::cout<<"\n[";
      for(int j=0; j<NB;j++){
         data2[i][j] = i-j;
	 std::cout<<data2[i][j]<<", ";
      }
      std::cout<<"]";
   }
   std::cout<<"\n";

   for(int i=0; i<NA;i++){
      for(int j=0; j<NC; j++){
         result[i][j] = 0;
      }
   }

 
    DUMP_START("Matrix 1", &data1[0][0], &data1[NA-1][NB-1], false);
    DUMP_START("Matrix 2", &data2[0][0], &data2[NB-1][NC-1], false);
   
    for(int j =0; j<NB; j++){
        for(int i = 0; i <NA; i++){
            for(int k = 0; k<NC; k++){
                result[i][k] += data1[i][j] * data2[j][k]; 
            }
        }
     }
  
    DUMP_STOP("Matrix 1");
    DUMP_STOP("Matrix 2");

   std::cout<<"\nRESULT:";   
   for(int i = 0; i<NA; i++){
      std::cout<<"\n[";
      for(int j=0; j<NC;j++){
	 std::cout<<result[i][j]<<", ";
      }
      std::cout<<"]";
   }
   std::cout<<"\n";

}
