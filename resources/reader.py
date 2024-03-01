# -*- coding: utf-8 -*-
"""

@author: srabadan
"""

from abc import ABC, abstractmethod
import os
import csv
import json
import pandas as pd

class currencyType(ABC):
    @abstractmethod
    def read(self,filePath):
        pass              
      
      
    
class readTXT(currencyType):  # Read .txt line by line
    def read(self,filePath):
        with open(filePath, "r") as file:
            return file.readlines()
        
        
class readJSON(currencyType): # Read .json with dict as output
    def read(self,filePath):
        with open(filePath) as file:
            data = file.read()
            data = json.loads(data)
            return data
        
        
class readTRNSYS(currencyType): # Read TRNSYS .out with weather data
    def read(self,filePath):
        df = pd.read_csv(filePath, index_col=0)  
        return df
        
        

class readCSV(currencyType): 
    def read(self,filePath):
        with open(filePath) as file:
            csv_output = csv.reader(file)
            rows = []
            for row in csv_output:
                rows.append(row)
            return rows            

        
class readCSVdf(currencyType): 
    def read(self,filePath):
        df = pd.read_csv(filePath, index_col=0) 
        return df  
    
class readCSVdfnoindex(currencyType): 
    def read(self,filePath):
        df = pd.read_csv(filePath) 
        return df  
    
class readCSVdelimeter(currencyType): # Not done
    def read(self,filePath):
        df = pd.read_csv(filePath,sep=';')
        return df  

class readCSVtab(currencyType): # Not done
    def read(self,filePath):
        df = pd.read_csv(filePath,sep='\t')
        return df  
            
class reader:
    def __init__(self,filePath , typeFile : currencyType):
        self.filePath = filePath
        self.typeFile = typeFile
        
    def start(self):
        return self.typeFile.read(self.filePath)  
    
        

    
if __name__ == '__main__':
    # dir_1 = os.getcwd()
    # print(dir_1)
    # dir_2 = '\data\PISO_v07_copia_seg.b17'
    # dire = dir_1 + dir_2
    
    # typeFile = readTXT()    
    # read = reader(dire,typeFile)
    # data_storage_b17 = read.start()
    
    # dir_2 = '\data\city7.obj'
    # dire = dir_1 + dir_2
    # read = reader(dire,typeFile)
    # data_storage_obj = read.start()

    dir_1 = os.getcwd()
    dir_2 = '\data\data2.json'
    dire = dir_1 + dir_2
    
    typeFile = readJSON()    
    read = reader(dire,typeFile)
    data_CSV = read.start()
 
    

    
    
    
    
