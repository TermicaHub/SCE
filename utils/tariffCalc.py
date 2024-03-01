# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:46:55 2023

@author: mcalcagnotto
"""
import pandas as pd
import numpy as np
import holidays
from datetime import date
from holidays_es import Province, HolidaySpain, Scope
from abc import ABC, abstractmethod
from interactors import dataEconomic

class typeTariff(ABC):
    def __init__(self, index_y):       
        self.index=index_y
        
    @abstractmethod
    def calculation(self):
        pass

class tariffSingle(typeTariff):
    def __init__(self,index_y,tariff_single,tariff_surplus):
        typeTariff.__init__(self,index_y) 
        self.tariff_g=tariff_single
        self.tariff_s=tariff_surplus
    def calculation(self):
        df_tariff=pd.DataFrame(index=self.index)
        df_tariff['grid']=self.tariff_g
        df_tariff['surplus']=self.tariff_s
        return df_tariff

        

#el viernes santo habría que excluirlo de los festivos
class tariffHourly(typeTariff):
    def __init__(self,index_y,tariff_peak, tariff_flat, tariff_valley, tariff_surplus):
        typeTariff.__init__(self,index_y) 
        self.tariff_p=tariff_peak
        self.tariff_f=tariff_flat
        self.tariff_v=tariff_valley
        self.tariff_s=tariff_surplus
    
    def calculation(self):
        
        tariff_d=pd.Series([None]*24,index=range(24))
        for i in range (0,8):
            tariff_d.iloc[i]=self.tariff_v
        for i in [8,9,10,14,15,16,17,22,23]:
            tariff_d.iloc[i]=self.tariff_f
        for i in [10,11,12,13,18,19,20,21]:
            tariff_d.iloc[i]=self.tariff_p

        tariff_w=np.tile(tariff_d,5)
        tariff_wd=np.tile(self.tariff_v,48)
        initial_day=date.weekday(self.index[0])
        
        if initial_day<5:
            tariff_w1=np.tile(tariff_d,(5-initial_day))
            tariff_wd=np.tile(self.tariff_v,48)
            tariff_w2=np.tile(tariff_d,initial_day)
            tariff=np.append(tariff_w1,tariff_wd)
            tariff=np.append(tariff,tariff_w2)
            
        if initial_day==5:
            tariff_wd=np.tile(self.tariff_v,48)
            tariff_w=np.tile(tariff_d,5)
            tariff=np.append(tariff_wd,tariff_w)

        if initial_day==6:
                tariff_wd=np.tile(self.tariff_v,24)
                tariff_w=np.tile(tariff_d,5)
                tariff=np.append(tariff_wd,tariff_w)
                tariff=np.append(tariff,tariff_wd)
                
        tariff_y=np.append((np.tile(tariff,52)),tariff_d)
        

        # for i in range(0, len(tariff_y.index)):
        #     if date(tariff_y.index[i].year,tariff_y.index[i].month,tariff_y.index[i].day) in holidays_es:
        #         tariff_y[i]=self.tariff_v
        
        df_tariff=pd.DataFrame(index=self.index)
        df_tariff['grid']=tariff_y
        df_tariff['surplus']=self.tariff_s
        
        #check if there are holidays and subtitute all hours of a holiday for valley tariff
        #solo festivos nacionales tienen tarifa valle
        #el viernes santo habría que excluirlo de los festivos
        holidays_es=[]
        holidays_es=holidays.country_holidays('ES')
        
        for holiday in holidays_es:
            if holiday in df_tariff.index:
                df_tariff.loc[holiday,'grid']=self.tariff_v
                
        #tariff_y_s=pd.DataFrame(index=index_y,columns='value')
        # tariff_y_s=pd.Series(index=self.index,name='value')
        # for i in range(0, len(tariff_y.index)):
        #     tariff_y_s[i]=tariff_surplus
        # transfoming into dataframe for harmonization
        # tariff_y=pd.DataFrame(tariff_y)
        # tariff_y_s=pd.DataFrame(tariff_y_s)
        
    
        return df_tariff

class tariffPVPC(typeTariff):
    def __init__(self,index_y):
        typeTariff.__init__(self,index_y) 
    def calculation(self):
        datos = dataEconomic.PVPCData()
        getPVPCdata = dataEconomic.insert(datos)
        tariff_g,tariff_s=getPVPCdata.start()
        

        df_tariff=pd.DataFrame(index=self.index)
        
        df_tariff['grid']=tariff_g
        df_tariff['surplus']=tariff_s
        #df_tariff=df_tariff_t.reindex(index=self.index, columns=['grid','surplus'])
        
        return df_tariff

class calculo:
    def __init__(self, outputType: typeTariff):
        self.outputType = outputType

    def start(self):
        return self.outputType.calculation()