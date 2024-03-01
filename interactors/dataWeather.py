# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:23:34 2022

@author: srabadan
"""

#Abstract method import

from abc import ABC, abstractmethod
import pandas as pd
import os
import sys
import math
import numpy as np

# Resources

from repositories import dataFV_repository
from repositories import dataWeather
from utils import Duffie_Beckman

# Abstract class

class selectDataWeather(ABC):
    @abstractmethod
    def __init__(self):
        pass
    def getWeatherData(self):
        pass  
    
        
        
class outputTRNSYS(selectDataWeather): 
    def __init__(self,clima):
        self.clima = clima
    def getWeatherData(self):
        typeFile_weather = dataWeather.fileTRNSYS()
        dir_1 = sys.path[0]       
        if self.clima == 1:
            filePath_clima = dir_1 + r'\resources\data\C2Barcelona_Airp_20.out'            
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()    
        elif self.clima == 2:
            filePath_clima =  dir_1 + r'\resources\data\C2Barcelona_Airp.out'
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()
        elif self.clima == 3:
            filePath_clima = dir_1 +'r\resources\data\C3-Reus-hour.out'
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()
        elif self.clima == 4:
            filePath_clima = dir_1 +'r\resources\data\D1Vic.out'
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()
        elif self.clima == 5:
            filePath_clima = dir_1 +'r\resources\data\D2GeronaCostaBrava.out'
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()
        elif self.clima == 6:
            filePath_clima = dir_1 +'r\resources\data\D3Lerida_Lleida.out'
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()
        elif self.clima == 7:
            filePath_clima = dir_1 +'r\resources\data\E1Puigcerda.out'
            get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
            df_clima = get_data.start()
        # elif self.clima == 8:
        #     filePath_clima =  dir_1 + r'\resources\data\Irradiation_Palma.out'
        #     get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
        #     df_clima = get_data.start()   
        # elif self.clima == 9:
        #     filePath_clima =  dir_1 + r'\resources\data\C2Bern_2.csv'
        #     get_data = dataWeather.dataWeather(typeFile_weather,filePath_clima)
        #     df_clima = get_data.start()               
        # df_clima = df_clima.head(-1)
        
       # df_clima=df_clima.drop(df_clima.index[0])
        return df_clima
    
    
class select:
    def __init__(self, select : selectDataWeather):
        self.select = select
         
    def start(self):        
        return self.select.getWeatherData()
    
    

    
