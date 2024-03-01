# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:23:34 2022

@author: srabadan
"""

#Abstract method import

from abc import ABC, abstractmethod
import pandas as pd
import os

# Resources

from repositories import readpvgis


# Abstract class

class moduleType(ABC):
    @abstractmethod
    def moduleSelection(self):
        pass  
        
class pvgis_mono(moduleType): 
    def moduleSelection(self):
        read_pvgis = readpvgis.readpvgis_data()
        import sys
        dir_1 = sys.path[0] 
        filePath = dir_1 + '\\resources\data\pvgis_data.csv'
        get_data = readpvgis.readpvgis(read_pvgis,filePath)
        data_fv = get_data.start()

        u0 = float(data_fv[0])
        u1 = float(data_fv[1])
        effnom = float(data_fv[2])  
        k1 = float(data_fv[3])
        k2 = float(data_fv[4])
        k3 = float(data_fv[5])
        k4 = float(data_fv[6])
        k5 = float(data_fv[7])
        k6 = float(data_fv[8])    
        return u0, u1, effnom, k1, k2, k3, k4, k5, k6 
    
class pvgis_poly(moduleType): 
    def moduleSelection(self):
        pass
        




             
    
class data_fv:
    def __init__(self, typeModule : moduleType):
        self.typeModule = typeModule
         
    def start(self):        
        return self.typeModule.moduleSelection()
    
    

    
