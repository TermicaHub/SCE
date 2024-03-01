# -*- coding: utf-8 -*-
"""

@author: srabadan
"""

from abc import ABC, abstractmethod
import os

class Currencytype(ABC):
    @abstractmethod
    def write(self,data,output,filePath):
        pass              
      
    
class writeTXT(Currencytype):
    def write(self,data,output,filePath):
  
        with open(filePath + output + '.b17','w') as file:
            file.writelines(data)
            
        
class writeCSV(Currencytype):
    def read(self,data,output,filePath):
        print('csv')   
        print(filePath)
        

            
class writer:
    def __init__(self,data_to_write,output_name,filePath , typeFile : Currencytype):
        self.data = data_to_write
        self.output = output_name
        self.filePath = filePath
        self.typeFile = typeFile
        
    def start(self):
        self.typeFile.write(self.data,self.output,self.filePath)   
        

    
if __name__ == '__main__':
    data_to_write = []
    for i in range(10):
        data_to_write.append(i)
    dir_1 = os.getcwd()
    dir_2 = "\output"
    dire = dir_1 + dir_2
    output_name = '\output_p'
    typeFile = writeTXT()
    write = writer(data_to_write,output_name,dire,typeFile)
    write.start()




    
    
    
    
    
