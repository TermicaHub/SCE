# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:51:06 2022

@author: srabadan
"""

from abc import ABC, abstractmethod
import pytz
import math

BXL = pytz.timezone('Europe/Brussels')
import pandas as pd


class outputFormat(ABC):
    @abstractmethod
    def calculation(self,Lst,Lloc):
        pass  


class dataframe(outputFormat):
    def calculation(self,Lst,Lloc,df):    
        df['n'] = [date.dayofyear for date in df.index]
        df['B'] = [(n - 1) * 360. / 365. for n in df.n]
        df['E'] = [229.2 * (0.000075 + 0.001868 * math.cos(math.radians(B)) - 0.032077 * math.sin(math.radians(B)) - 0.014615 * math.cos(math.radians(2 * B)) - 0.04089 * math.sin(math.radians(2 * B))) for B in df.B]  # parámetro?
        df['hour'] = [date.hour for date in df.index]
        df['SolarTime'] = df['hour'] + (4 * (Lst - Lloc) + df['E']) / 60
        df['omega2'] = [(-12+hora)*15 for hora in df.SolarTime]  #calculating w from the end of the interval
        df['omega1'] = [(-12+(hora-1))*15 for hora in df.SolarTime] #calculating w from the beggining of the interval
    
        return df
    
class calculo:
    def __init__(self, outputType : outputFormat,Lst,Lloc,df):
        self.Lst = Lst
        self.Lloc = Lloc
        self.df = df
        self.outputType = outputType
         
    def start(self):        
        return self.outputType.calculation(self.Lst,self.Lloc,self.df)
        