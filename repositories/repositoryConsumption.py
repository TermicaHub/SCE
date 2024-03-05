# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 15:07:47 2024

@author: mcalcagnotto
"""

# Abstract method import

from abc import ABC, abstractmethod


# Resources

from resources import reader


# Abstract class

class currencyType(ABC):
    @abstractmethod
    # def __init__(self,oc_viv):
    #     #numero de ocupantes de la vivienda
    #     self.n_occ=oc_viv
    def dataSource(self):
        pass

class SomProfilesSimple(currencyType):
    def dataSource(self):
        import sys
        import pandas as pd
        direct = sys.path[0]
        filePath = direct + '\\resources\\data\\ConsProfiles_OCC2.57.csv'
        typeFile = reader.readCSVdf()
        read = reader.reader(filePath,typeFile)
        data_out = read.start()
        data_out.index= [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=i) for i in data_out.index]
        return data_out
    
class SomProfiles(currencyType):
    def __init__(self,oc_viv):
        #currencyType.__init__(self,oc_viv)
        self.n_occ=oc_viv
    def dataSource(self):
        import sys
        import pandas as pd
        direct = sys.path[0]
        if self.n_occ==1:
            filePath = direct + '\\resources\\data\\ConsProfiles_OCC1.csv'
        elif self.n_occ==2:
            filePath = direct + '\\resources\\data\\ConsProfiles_OCC2.csv'
        elif self.n_occ==2.57:
            filePath = direct + '\\resources\\data\\ConsProfiles_OCC2.57.csv'
        elif self.n_occ==3:
            filePath = direct + '\\resources\\data\\ConsProfiles_OCC3.csv'
        else:
            filePath = direct + '\\resources\\data\\ConsProfiles_OCC4.csv'
        typeFile = reader.readCSVdf()
        read = reader.reader(filePath,typeFile)
        data_out = read.start()
        data_out.index= [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=i) for i in data_out.index]
        return data_out
    


class get_data:
    def __init__(self, typeFile: currencyType):
        self.typeFile = typeFile

    def start(self):
        return self.typeFile.dataSource()