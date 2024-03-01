# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:03:37 2022

@author: srabadan
"""

#Abstract method import

from abc import ABC, abstractmethod

# Resources

from resources import reader


# Abstract class

class currencyType(ABC):
    @abstractmethod
    def dataSource(self,filePath):
        pass  
        
class readpvgis_data(currencyType):  
    def dataSource(self,filePath):
        typeFile = reader.readCSV()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        data_output = []
        for i in range(3,len(get_data)):
            data_output.append(get_data[i][1])
        return data_output

             
    
class readpvgis:
    def __init__(self, typeFile : currencyType,filePath):
        self.filePath = filePath
        self.typeFile = typeFile
         
    def start(self):        
        return self.typeFile.dataSource(self.filePath)
    
if __name__ == '__main__':
    read_pvgis = readpvgis_data()
    filePath =  r'..\resources\data\pvgis_data.csv'
    get_data = readpvgis(read_pvgis,filePath)
    data_fv = get_data.start()
    
