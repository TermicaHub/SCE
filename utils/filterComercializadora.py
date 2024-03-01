# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:51:06 2022

@author: srabadan
"""

from abc import ABC, abstractmethod
import pandas as pd
import warnings

class outputFormat(ABC):
    @abstractmethod
    def calculation(self,data_in):
        pass  


class dataframe(outputFormat):
    def calculation(self,data_in):
        
        # warnings.filterwarnings("ignore")
        # count_row = 0
        # data_date = pd.DataFrame()
        # time_0year = data_in.index[100].strftime("%Y")
        # data_date.index = [pd.Timestamp(year = int(time_0year), month = 1, day = 1) + pd.Timedelta(hours=i) for i in range(0,8760)]
        # data_out = pd.DataFrame() 
        # for i in data_date.index:
        #     if i in data_in.index.values:
        #         pass
        #     else:
        #         data_in.loc[i,'CUPS'] = data_in.iloc[0,0] #CUPS
        #         data_in.loc[i,'Fecha'] = i.strftime("%d/%m/%Y") #Fecha
        #         data_in.loc[i,'Hora'] = int(i.strftime("%H")) #Hora                
        #         data_in.loc[i,'REAL/ESTIMADO'] = 'E'
        #             # data_in.loc[i,'AE_kWh'] = (float(data_in.loc[n,'AE_kWh'].replace(',','.'))+float(data_in.loc[m,'AE_kWh'].replace(',','.')))/2            
                
        #     count_row = count_row + 1 
        data_in = data_in.sort_index() 
        def filtro_general(data_in):           
            for i in data_in.index:
                if str(data_in.loc[i,'AE_kWh']) == 'nan':
                    n = i + pd.Timedelta(hours=1)
                    m = i - pd.Timedelta(hours=1)
                    # Interpolar entre el valor anterior y el siguiente cuando sea posible.
                    try:
                        if str(data_in.loc[n,'AE_kWh']) != 'nan' and str(data_in.loc[m,'AE_kWh']) != 'nan':
                            d_1 = float(data_in.loc[n,'AE_kWh'].replace(',','.'))
                            d_2 = float(data_in.loc[m,'AE_kWh'].replace(',','.')) 
                            data_in.loc[i,'AE_kWh'] = (d_1+d_2)/2    
                    except:
                        pass
                if str(data_in.loc[i,'AE_kWh']) == 'nan':        
                    n = i + pd.Timedelta(weeks=1)
                    m = i - pd.Timedelta(weeks=1)       
                    try:
                        if str(data_in.loc[n,'AE_kWh']) != 'nan' and str(data_in.loc[m,'AE_kWh']) != 'nan':
                            d_1 = float(data_in.loc[n,'AE_kWh'].replace(',','.'))
                            d_2 = float(data_in.loc[m,'AE_kWh'].replace(',','.')) 
                            data_in.loc[i,'AE_kWh'] = (d_1+d_2)/2
                    except:
                        pass                                
                if str(data_in.loc[i,'AE_kWh']) == 'nan':
                    n = i + pd.Timedelta(weeks=4)
                    m = i - pd.Timedelta(weeks=4)
                    try:
                        if str(data_in.loc[n,'AE_kWh']) != 'nan' and str(data_in.loc[m,'AE_kWh']) != 'nan':
                            d_1 = float(data_in.loc[n,'AE_kWh'].replace(',','.'))
                            d_2 = float(data_in.loc[m,'AE_kWh'].replace(',','.')) 
                            data_in.loc[i,'AE_kWh'] = (d_1+d_2)/2
                    except:
                        pass                                
                if str(data_in.loc[i,'AE_kWh']) == 'nan':
                    n = i + pd.Timedelta(weeks=8)
                    m = i - pd.Timedelta(weeks=8)
                    try:
                        data_in.loc[n,'AE_kWh']
                        data_in.loc[m,'AE_kWh']
                    except:
                        continue
                    if str(data_in.loc[n,'AE_kWh']) != 'nan' and str(data_in.loc[m,'AE_kWh']) != 'nan':
                        d_1 = float(data_in.loc[n,'AE_kWh'].replace(',','.'))
                        d_2 = float(data_in.loc[m,'AE_kWh'].replace(',','.')) 
                        data_in.loc[i,'AE_kWh'] = (d_1+d_2)/2
            return data_in 
        def filtro_enero_diciembre(data_in):
            
            data_temp_anterior = data_in.copy()
            data_temp_anterior = data_temp_anterior.reset_index(drop = True)
            year_base =  data_in.index.strftime("%Y")
            year_base = int(year_base[0]) - 1
            time_0 = str(year_base) + '-01-01 00:00'
            data_temp_anterior.index = [pd.Timestamp(time_0) + pd.Timedelta(hours=i) for i in data_temp_anterior.index]
            
            data_temp_siguiente = data_in.copy()
            data_temp_siguiente = data_temp_siguiente.reset_index(drop = True)
            year_base =  data_in.index.strftime("%Y")
            year_base = int(year_base[0]) + 1
            time_0 = str(year_base) + '-01-01 00:00'
            data_temp_siguiente.index = [pd.Timestamp(time_0) + pd.Timedelta(hours=i) for i in data_temp_siguiente.index]           
            data_in = pd.concat([data_temp_anterior, data_in, data_temp_siguiente], axis=0)
            data_in = filtro_general(data_in)
            data_in = data_in.iloc[8760:17520,:]
            return data_in

            
        count = 0
        while count < 5: # 5 pases por el filtro para completar datos
            data_in = filtro_general(data_in)
            count = count + 1            
        data_out = data_in
        
        # count = 0        
        # while count < 1: # 3 pases por el filtro para completar datos
        #     data_in = filtro_enero_diciembre(data_in)
        #     count = count + 1 
        # data_out = data_in
        # data_out = data_out.shift(periods = -1, fill_value = data_out['AE_kWh'][-1])
        # #data_out.index = [pd.Timestamp(year = int(time_0year), month = 1, day = 1) + pd.Timedelta(hours=i) for i in range(0,8760)]        
        return data_out
    
class calculo:
    def __init__(self, outputType : outputFormat,data_in):
        self.data_in = data_in
        self.outputType = outputType
         
    def start(self):  
        return self.outputType.calculation(self.data_in)
    
    
    
    
        