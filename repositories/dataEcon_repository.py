# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:46:55 2023

@author: mcalcagnotto
"""

#Abstract method import

from abc import ABC, abstractmethod
from datetime import datetime
import os
import pandas as pd


# Resources


from resources import reader


# Abstract class

class currencyType(ABC):
    @abstractmethod
    def dataSource(self,filePath):
        pass  
        
class ciclicaSimple(currencyType): # Read .json from Ciclica without transformation
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\dataeconomic.json'
        typeFile = reader.readJSON()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        return get_data

class PVPCActive(currencyType): # Read .csv with PVPC active hourly prices from 2022
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\PVPCActiva2023.csv'
        typeFile = reader.readCSVdfnoindex()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        # new_index=pd.to_datetime(get_data['datetime'],format='%Y-%m-%dT%H:%M:%S',utc=True)
        # new_index=new_index.dt.strftime('%Y-%m-%d %H:%M:%S')
        # get_data.index=new_index
        # # #get_data['date']=(pd.to_datetime(get_data['date'].astype(str), format='%m/%d/%y')).dt.strftime("%m-%d-%y")
        # # #get_data['date']=(datetime.strptime(get_data['date'], "%d/%m/%y")).strftime("%y-%m-%d")
        # # new_index=pd.to_datetime(get_data['date'] + ' ' + get_data['hour'].astype(str) + ':00')
        df_out=pd.Series()
        df_out=get_data['value'].values/1000 #convert €/MWh in €/kWh
        #PVPC_active=(get_data['value'],index=new_index)
        
        return df_out

class PVPCSurplus(currencyType): # Read .csv with PVPC surplus hourly prices from 2022
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\PVPCExcedente2023.csv'
        typeFile = reader.readCSVdfnoindex()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        # new_index=pd.to_datetime(get_data['datetime'],format='%Y-%m-%dT%H:%M:%S',utc=True)
        # new_index=new_index.dt.strftime('%Y-%m-%d %H:%M:%S') #this only works leaving utc True, but it gives us the hour in utc, so we need to correct it for 1 hour later
        # get_data.index=new_index
        # get_data['date']=(pd.to_datetime(get_data['date'])).dt.strftime("%m-%d-%y")
        # #get_data['date']=(pd.to_datetime(get_data['date'].astype(str), format='%m/%d/%y')).dt.strftime("%y-%m-%d")
        # #(datetime.strptime(get_data['date'], "%d/%m/%y")).strftime("%y-%m-%d")
        # new_index=pd.to_datetime(get_data['date'] + ' ' + get_data['hour'].astype(str) + ':00')
        df_out=pd.Series()
        df_out=get_data['value'].values/1000 #convert €/MWh in €/kWh
       # get_data=get_data.drop('datetime',axis=1)
        # get_data['value']=get_data['value'].values/1000 #convert €/MWh in €/kWh
        # get_data=get_data.drop('datetime',axis=1)
        #PVPC_surplus=pd.DataFrame(get_data,columns='value'index=new_index)
       
        return df_out

class defaultCosts(currencyType): # Read .csv with reference costs for investment and maintainance
    def dataSource(self):
        import sys
        direct = sys.path[0]
        filePath = direct + '\\resources\data\precios_ref.csv'
        typeFile = reader.readCSVdf()
        read = reader.reader(filePath,typeFile)
        get_data = read.start()
        
        return get_data
    
        
    
class project_SQL(currencyType): # Read data from SQL 
    def dataSource(self,filePath):
        pass

class project_CSV(currencyType): # Read data from Excel 
    def dataSource(self,filePath):
        pass
             
    
class dataEcon:
    def __init__(self, typeFile : currencyType):
        self.typeFile = typeFile
         
    def start(self):        
        return self.typeFile.dataSource()
    
    
if __name__ == '__main__':
    typeFile = ciclicaSimple()
    get_data = dataFV(typeFile)
    params = get_data.start()      
  
    
