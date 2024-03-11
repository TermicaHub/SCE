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
    def dataSource(self,direction):
        pass  
        
class fileTRNSYS(currencyType): # Read .out weather from TRNSYS 
    def dataSource(self,filePath):
        import pandas as pd
        typeFile = reader.readTRNSYS()
        df = reader.reader(filePath,typeFile)
        df = df.start()
        #el archivo TRNSYS viene con 8761 valores, y hacen referencia a la hora que termina en aquella hora, por lo que borramos el primer valor y los demás los desplazamos a 1h antes
        df=df.drop(df.index[0])
        df.index = [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=(i-1)) for i in df.index]
        df.columns = [namecol.replace(' ', '') for namecol in df.columns]
        # #correction for the time series to start at 01:00 I am shifting the first value to the last (simplification)
        #df = pd.concat([df.iloc[1:], df.iloc[:1]])
        #df.iloc[len(df)-1].index=pd.Timestamp('2022-01-01 00:00')


        return df        
        
    
class file_CSV(currencyType): # Read weather data from CSV
    def dataSource(self,filePath):
        pass


             
    
class dataWeather:
    def __init__(self, typeFile : currencyType,direction):
        self.direction = direction
        self.typeFile = typeFile
         
    def start(self):        
        return self.typeFile.dataSource(self.direction)
    
    
# if __name__ == '__main__':
#     typeFile = fileTRNSYS()
#     dire = r'..\resources\data\C2Barcelona_Airp.out'
#     get_data = dataWeather(typeFile, dire)
#     params = get_data.start()      
  
    
