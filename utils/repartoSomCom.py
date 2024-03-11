# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 15:28:42 2024

@author: mcalcagnotto
"""

import pandas as pd
from abc import ABC, abstractmethod
import pytz
import math
import numpy as np

BXL = pytz.timezone('Europe/Brussels')


class typeCoef(ABC):
    def __init__(self,columns_id):
        #numero de viviendas total
        self.column_name=columns_id
        self.n_users=len(self.column_name)
    @abstractmethod
    def calculation(self):
        pass


class CoefUnicoViv(typeCoef):
    def __init__(self,columns_id):
        typeCoef.__init__(self,columns_id)

    def calculation(self):
        coef=pd.Series()
        for i in self.column_name:
        #coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
            coef[i]=1/self.n_users
        return coef
    
           
    
class CoefDifViv(typeCoef):
    def __init__(self, columns_id,coef_cp):
        typeCoef.__init__(self, columns_id)
        self.coef_main=coef_cp
    def calculation(self):
        #coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
        coef=pd.Series()
        #considerando que el coef informado es para la vivienda
        coef['Cbase']=self.coef_main
        for i in self.column_name[1:]:
            coef[i]=(1-self.coef_main)/(self.n_users-1)
        return coef
    
class CoefDifEdif(typeCoef):
    def __init__(self, columns_id,coef_cp,n_viv):
        typeCoef.__init__(self, columns_id)
        self.coef_main=coef_cp
        self.viv_ep=n_viv
    def calculation(self):
        #coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
        coef=pd.Series()
        #considerando que el coef informado es para el edificio
        if self.viv_ep>1:
            #lo reparte igual entre todas las viviendas del edificio 
            coef['Cbase']=self.coef_main/self.viv_ep
            #asigna este mismo valor a todas las viviendas del edificio 
            for i in self.column_name[1:(self.viv_ep-1)]:
                coef[i]=coef['Cbase']
            #a las demás viviendas les asigna la diferencia 
            for i in self.column_name[self.viv_ep:]:
                coef[i]=(1-self.coef_main)/(self.n_users-self.viv_ep)
        else:
            coef['Cbase']=self.coef_main
            for i in self.column_name[1:]:
                coef[i]=(1-self.coef_main)/(self.n_users-self.viv_ep)
        return coef

class CoefVar(typeCoef):
    def __init__(self,consumption_df):
        
        self.consumption=consumption_df
    def calculation(self):
        coef=pd.Series()
        for i in self.consumption.index[:len(self.consumption.index)-1]:
        #coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
            coef[i]=self.consumption[i]/self.consumption['Total']
        return coef
    

class calculo:
    def __init__(self, outputType: typeCoef):
        self.outputType = outputType

    def start(self):
        return self.outputType.calculation()
    