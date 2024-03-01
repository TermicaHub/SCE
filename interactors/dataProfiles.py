# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:06:44 2024

@author: mcalcagnotto
"""

#Abstract method import

from abc import ABC, abstractmethod
import pandas as pd
import os
import sys
import math
import numpy as np

# Resources

from repositories import dataProfiles_repository


# Abstract class

class selectDataProfiles(ABC):
    @abstractmethod
    def __init__(self):
        pass
    def getConsumptionData(self):
        pass  
    
        
        
class outputProfiles(selectDataProfiles): 
    def __init__(self):
        pass
    def getConsumptionData(self):
        import glob

            
        typeFile_profile = dataProfiles_repository.fileProfile()
     
        
        direct = sys.path[0]
        folderPath = os.listdir(direct + r'\resources\data\profiles')

        df_folderPath=pd.DataFrame(folderPath)
        df_folderPath.columns=['name']
        folders = {} 
        names=[]
        for i in range(0,len(folderPath)):
            
            position=folderPath[i].find('DW')
            if folderPath[i][(position + 3)].isdigit():
                j=int(folderPath[i][(position + 2)]+folderPath[i][(position + 3)])
            else:
                j=int(folderPath[i][(position + 2)])
            names.append(int(j))

            
        df_folderPath.index=names
        df_folderPath=df_folderPath.sort_index()
        new_df={}
        for i in df_folderPath.index:         
            #out_loc = direct + r'\resources\data\profiles' + '\\' + i +  '\\*.out'
            out_loc = direct + r'\resources\data\profiles' + '\\' + df_folderPath['name'][i]
            folders.setdefault(i,)
            #data_out = pd.DataFrame()
            
            get_data = dataProfiles_repository.dataProfiles(typeFile_profile,out_loc)
            df_consumption = get_data.start()   
            #data_out = pd.concat([data_out, df_consumption])
                
            # for fullPath in glob.glob(out_loc):
            #     get_data = dataProfiles_repository.dataProfiles(typeFile_profile,fullPath)
            #     df_consumption = get_data.start()   
            #     data_out = pd.concat([data_out, df_consumption])
            # data_out = data_out.reset_index(drop=True)                   
            # data_out.index = [pd.to_datetime(data_out.iloc[i,1],dayfirst=True) + pd.Timedelta(hours = data_out.iloc[i,2]) for i in data_out.index]                
            # d_energybalance_defecto=d_energybalance_defecto.loc[:,'Med_cp':'Net_cp']
            # part_to_drop = '_cp'
            # d_energybalance_defecto.columns = d_energybalance_defecto.columns.str.replace(part_to_drop, '')
            columns_to_sum = df_consumption.columns[3:14].tolist()
            columns_to_sum=columns_to_sum+[df_consumption.columns[1]]
            new_df=pd.DataFrame()
            new_df['ConStove']=df_consumption[df_consumption.columns[0]]
            new_df['ConOven']=df_consumption[df_consumption.columns[2]]
            new_df['ConDHW']=df_consumption[df_consumption.columns[18]]                        
            new_df['Sum']=df_consumption[columns_to_sum].sum(axis=1)
            #folders[i] = df_consumption  
            folders[i] = new_df 
            
        return folders
    
    
class select:
    def __init__(self, select : selectDataProfiles):
        self.select = select
         
    def start(self):        
        return self.select.getConsumptionData()