# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:03:37 2022

@author: srabadan
"""

#Abstract method import

from abc import ABC, abstractmethod
import os


# Resources


from resources import reader


# Abstract class

class currencyType(ABC):
    @abstractmethod
    def dataSource(self,filePath):
        pass  
        
class ciclicaSimple(currencyType): # Read .json from Ciclica without transformation
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\data3.json'
        typeFile = reader.readJSON()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        return get_data
    
    
class ciclicaAdv(currencyType): # Read .json from Ciclica without transformation
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\datacol.json'
        typeFile = reader.readJSON()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        return get_data
    

class dataCIES(currencyType): # Read .json from Ciclica without transformation
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\dataCIES.json'
        typeFile = reader.readJSON()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        return get_data
    
    
class project_SQL(currencyType): # Read data from SQL 
    def dataSource(self,filePath):
        pass

class project_CSV(currencyType): # Read data from Excel 
    def dataSource(self,filePath):
        pass
             
    
class dataFV:
    def __init__(self, typeFile : currencyType):
        self.typeFile = typeFile
         
    def start(self):        
        return self.typeFile.dataSource()
    
    
if __name__ == '__main__':
    typeFile = ciclicaSimple()
    get_data = dataFV(typeFile)
    params = get_data.start()      
  
    
