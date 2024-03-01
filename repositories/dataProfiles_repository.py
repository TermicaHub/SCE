# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 14:50:07 2024

@author: mcalcagnotto
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
        
class fileProfile(currencyType): # Read .out stochastic profiles 
    def dataSource(self,filePath):
        import pandas as pd
        typeFile = reader.readCSVtab()
        df = reader.reader(filePath,typeFile)
        df = df.start()
        df.columns = [namecol.replace(' ', '') for namecol in df.columns]
        df=df.drop(df.index[0])
        #df.index= [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=i) for i in df.index]
       
        position=filePath.find('DW')
        if filePath[(position + 3)].isdigit():
            i=filePath[(position + 2)]+filePath[(position + 3)]
        else:
            i=filePath[(position + 2)]
        
        cons_df=df.loc[:, 'DW'+i+'_ConStove':'DW'+i+'_ConDHW_W' ]
        cons_df_av=pd.DataFrame()
        
        
        for column in cons_df.columns:
            cons_df_av[column]=(cons_df.groupby(cons_df.index // 20)[column].mean())/1000
        #drop the first value
        cons_df_av=cons_df_av.drop(cons_df_av.index[0])
        cons_df_av=cons_df_av.reset_index(drop=True)
        cons_df_av.index = [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=i) for i in cons_df_av.index]     
        cons_df_av.drop
        # df_out=
        # df.index = [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=i) for i in df.index]
        # df.columns = [namecol.replace(' ', '') for namecol in df.columns]
        # #correction for the time series to start at 01:00 I am shifting the first value to the last (simplification)
        #df = pd.concat([df.iloc[1:], df.iloc[:1]])
        #df.iloc[len(df)-1].index=pd.Timestamp('2022-01-01 00:00')

        
        return cons_df_av    
        
    
class file_CSV(currencyType): # Read weather data from CSV
    def dataSource(self,filePath):
        pass


             
    
class dataProfiles:
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
  
    
