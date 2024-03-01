# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:03:37 2022

@author: srabadan
"""

#Abstract method import

from abc import ABC, abstractmethod
import sys
# Resources

from resources import reader


# Abstract class

class currencyType(ABC):
    @abstractmethod
    def data(self,filePath):
        pass  
        
    
# Obsoleto
# class uniqueCSV(currencyType): # Read csv
#     def data(self):
      
#         direct = sys.path[0]
#         filePath = direct + '\\resources\data\Camilo_JoseC_filtrado.csv'
#         typeFile = reader.readCSVdelimeter()
#         read = reader.reader(filePath,typeFile)
#         output_reader = read.start()
        # output_reader = output_reader.reset_index()
        # return output_reader
    
class multiCSV(currencyType): # Read multi CSV
    def data(self):
        import glob
        import os
        import pandas as pd

        typeFile = reader.readCSVdelimeter()
        direct = sys.path[0]
        folderPath = os.listdir(direct + r'\resources\data\realData')
        folders = {} 
        for i in folderPath:
            csv_loc = direct + r'\resources\data\realData' + '\\' + i +  '\\*.csv'
            folders.setdefault(i,)
            data_out = pd.DataFrame()
            for fullPath in glob.glob(csv_loc):
                read = reader.reader(fullPath,typeFile)
                output_reader = read.start()
                data_out = pd.concat([data_out, output_reader])
            data_out = data_out.reset_index(drop=True)                   
            data_out.index = [pd.to_datetime(data_out.iloc[i,1],dayfirst=True) + pd.Timedelta(hours = data_out.iloc[i,2]) for i in data_out.index]                
            folders[i] = data_out     
            
        # filePath = direct + '\\resources\data\Med_profile.csv'
        # typeFile = reader.readCSVdf()
        # data_eur = reader.reader(filePath,typeFile)
        # data_eur = data_eur.start()   
        # return folders, data_eur                        
        return folders  

             
    
class get_data:
    def __init__(self, typeFile : currencyType):
        self.typeFile = typeFile
         
    def start(self):        
        return self.typeFile.data()
    
    
if __name__ == '__main__':
    typeFile = multiCSV()
    output = get_data(typeFile)
    data_out, data_eur  = output.start()      
  
    
