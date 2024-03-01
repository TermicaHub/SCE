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
    def data(self,filePath):
        pass  

    
class multi_annually(currencyType): # Read csv with more than 1 year data
    def data(self):
        data_out = {}
     
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\Residencial_3years.csv'
        typeFile = reader.readCSVdf()
        read = reader.reader(filePath,typeFile)
        output_reader = read.start()
        output_reader = output_reader.reset_index()
        
        years = (max(output_reader['dataYear'])+1) - min(output_reader['dataYear'])            
        count = 0        
        for i in range(1,years+1):                     
            if output_reader.at[count+59,'dataMonth'] == 2: # Drop 29 February
                data_out[str(int(output_reader.at[count+1,'dataYear']))] = output_reader.iloc[count:count+366]
                data_out[str(int(output_reader.at[count+1,'dataYear']))] = data_out[str(int(output_reader.at[count+1,'dataYear']))].drop([count+59],axis = 0)
                count = count + 1
            else:
                data_out[str(int(output_reader.at[count+1,'dataYear']))] = output_reader.iloc[count:count+365]     
            count = count + 365
        filePath = direct + '\\resources\data\Med_profile.csv'
        typeFile = reader.readCSVdf()
        data_eur = reader.reader(filePath,typeFile)
        data_eur = data_eur.start()
        
        
        
        return data_out, data_eur

             
    
class get_data:
    def __init__(self, typeFile : currencyType):
        self.typeFile = typeFile
         
    def start(self):        
        return self.typeFile.data()
    
    
if __name__ == '__main__':
    typeFile = multi_annually()
    output = get_data(typeFile)
    data_out, data_eur = output.start()      
  
    
