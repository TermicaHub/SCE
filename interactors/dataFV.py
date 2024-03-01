# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:23:34 2022

@author: srabadan
"""

#Abstract method import

from abc import ABC, abstractmethod
import pandas as pd

import math
import numpy as np

# Resources

from repositories import dataFV_repository
from utils import Duffie_Beckman

# Abstract class

class insertionMethod(ABC):
    @abstractmethod
    def __init__(self):
        pass
    def getInputs(self):
        pass  
    
        
        
class somCInputs(insertionMethod): 
    def __init__(self):
        pass
    def getInputs(self):
        typeFile_FV = dataFV_repository.ciclicaSimple()
        get_data = dataFV_repository.dataFV(typeFile_FV)
        data_params=get_data.start()

      

        df = pd.DataFrame(index = list(range(0,8760)))
        df.index = [pd.Timestamp('2021-01-01 0:00') + pd.Timedelta(hours=i) for i in df.index]
        
        dBeck_output = Duffie_Beckman.dataframe()
        dBeck = Duffie_Beckman.calculo(dBeck_output,data_params['Lst'],data_params['Lloc'],df)
        df = dBeck.start() 

        def B_calculation(B):          
            B = 180. / np.pi * (0.006918 - 0.399912 * math.cos(math.radians(B)) + 0.070257 * math.sin(math.radians(B))) + \
                180. / np.pi * (-0.006758 * math.cos(math.radians(2 * B)) + 0.000907 * math.sin(math.radians(2 * B))) + \
                180. / np.pi * (-0.002697 * math.cos(math.radians(3 * B)) + 0.00148 * math.sin(math.radians(3 * B)))
            return B
        df['delta2'] = df.B.apply(B_calculation)
        
        def calc_omegas(delta2,phi):
            return math.degrees(math.acos((-1)*(math.tan(math.radians(phi)))*(math.tan(math.radians(delta2)))))
        
        df['omegas']=df.apply(lambda row: calc_omegas(row.delta2,data_params['phi']), axis=1)
        
        
        def calc_omega(omega2,omega1,omegas):
            #if sunrise occurs in the interval
            if omega2>-omegas and omega1<-omegas:
                omega=0.5*(omega2-omegas)
            #if sunset occurs in the interval
            elif omega2>omegas and omega1<omegas:
                omega=0.5*(omega1+omegas)
            #every other case
            else:
                omega=0.5*(omega2+omega1)
            return omega
     
        df['omega']=df.apply(lambda row: calc_omega(row.omega2,row.omega1,row.omegas), axis=1)
        
        def calc_costhetaz(delta2, omega, omegas):
            if omega<-omegas or omega>omegas:
                temp=0
            else:
                temp = math.sin(math.radians(delta2)) * math.sin(math.radians(data_params['phi'])) + \
                math.cos(math.radians(data_params['phi'])) * math.cos(math.radians(delta2)) * math.cos(math.radians(omega))
            return temp
        
        df['costhetaz'] = df.apply(lambda row: calc_costhetaz(row.delta2, row.omega, row.omegas), axis=1)
        df['thetaz2'] = [math.degrees(math.acos(x)) for x in df.costhetaz]
       
        def calc_singammas(delta2, omega, omegas, thetaz2):
            if omega<-omegas or omega>omegas:
                temp=0
                gammas=-90
            else:
                temp=math.cos(math.radians(delta2)) * math.sin(math.radians(omega)) / math.sin(math.radians(thetaz2))
                gammas=math.degrees(math.asin(temp))
            return temp, gammas
            
        df[['singammas','gammas2']] = df.apply(lambda row: pd.Series(calc_singammas(row.delta2, row.omega, row.omegas, row.thetaz2)), axis=1)

       
        return data_params, df
    
class somCInputsAdv(insertionMethod): 
    def __init__(self):
        pass
    def getInputs(self):
        typeFile_FV = dataFV_repository.ciclicaAdv()
        get_data = dataFV_repository.dataFV(typeFile_FV)
        data_params=get_data.start()

      

        df = pd.DataFrame(index = list(range(0,8760)))
        df.index = [pd.Timestamp('2021-01-01 0:00') + pd.Timedelta(hours=i) for i in df.index]
        
        dBeck_output = Duffie_Beckman.dataframe()
        dBeck = Duffie_Beckman.calculo(dBeck_output,data_params[0]['Lst'],data_params[0]['Lloc'],df)
        df = dBeck.start() 

        def B_calculation(B):          
            B = 180. / np.pi * (0.006918 - 0.399912 * math.cos(math.radians(B)) + 0.070257 * math.sin(math.radians(B))) + \
                180. / np.pi * (-0.006758 * math.cos(math.radians(2 * B)) + 0.000907 * math.sin(math.radians(2 * B))) + \
                180. / np.pi * (-0.002697 * math.cos(math.radians(3 * B)) + 0.00148 * math.sin(math.radians(3 * B)))
            return B
        df['delta2'] = df.B.apply(B_calculation)
        
        def calc_omegas(delta2,phi):
            return math.degrees(math.acos((-1)*(math.tan(math.radians(phi)))*(math.tan(math.radians(delta2)))))
        
        df['omegas']=df.apply(lambda row: calc_omegas(row.delta2,data_params[0]['phi']), axis=1)
        
        
        def calc_omega(omega2,omega1,omegas):
            #if sunrise occurs in the interval
            if omega2>-omegas and omega1<-omegas:
                omega=0.5*(omega2-omegas)
            #if sunset occurs in the interval
            elif omega2>omegas and omega1<omegas:
                omega=0.5*(omega1+omegas)
            #every other case
            else:
                omega=0.5*(omega2+omega1)
            return omega
     
        df['omega']=df.apply(lambda row: calc_omega(row.omega2,row.omega1,row.omegas), axis=1)
        
        def calc_costhetaz(delta2, omega, omegas):
            if omega<-omegas or omega>omegas:
                temp=0
            else:
                temp = math.sin(math.radians(delta2)) * math.sin(math.radians(data_params[0]['phi'])) + \
                math.cos(math.radians(data_params[0]['phi'])) * math.cos(math.radians(delta2)) * math.cos(math.radians(omega))
            return temp
        
        df['costhetaz'] = df.apply(lambda row: calc_costhetaz(row.delta2, row.omega, row.omegas), axis=1)
        df['thetaz2'] = [math.degrees(math.acos(x)) for x in df.costhetaz]
       
        def calc_singammas(delta2, omega, omegas, thetaz2):
            if omega<-omegas or omega>omegas:
                temp=0
                gammas=-90
            else:
                temp=math.cos(math.radians(delta2)) * math.sin(math.radians(omega)) / math.sin(math.radians(thetaz2))
                gammas=math.degrees(math.asin(temp))
            return temp, gammas
            
        df[['singammas','gammas2']] = df.apply(lambda row: pd.Series(calc_singammas(row.delta2, row.omega, row.omegas, row.thetaz2)), axis=1)

       
        return data_params, df

class CIESInputs(insertionMethod): 
    def __init__(self):
        pass
    def getInputs(self):
        typeFile_FV = dataFV_repository.dataCIES()
        get_data = dataFV_repository.dataFV(typeFile_FV)
        data_params = get_data.start()

        df = pd.DataFrame(index = list(range(0,8760)))
        df.index = [pd.Timestamp('2021-01-01 0:00') + pd.Timedelta(hours=i) for i in df.index]
        
        dBeck_output = Duffie_Beckman.dataframe()
        dBeck = Duffie_Beckman.calculo(dBeck_output,data_params['Lst'],data_params['Lloc'],df)
        df = dBeck.start() 

        def B_calculation(B):          
            B = 180. / np.pi * (0.006918 - 0.399912 * math.cos(math.radians(B)) + 0.070257 * math.sin(math.radians(B))) + \
                180. / np.pi * (-0.006758 * math.cos(math.radians(2 * B)) + 0.000907 * math.sin(math.radians(2 * B))) + \
                180. / np.pi * (-0.002697 * math.cos(math.radians(3 * B)) + 0.00148 * math.sin(math.radians(3 * B)))
            return B
        df['delta2'] = df.B.apply(B_calculation)
        
        def calc_omegas(delta2,phi):
            return math.degrees(math.acos((-1)*(math.tan(math.radians(phi)))*(math.tan(math.radians(delta2)))))
        
        df['omegas']=df.apply(lambda row: calc_omegas(row.delta2,data_params['phi']), axis=1)
        
        
        def calc_omega(omega2,omega1,omegas):
            #if sunrise occurs in the interval
            if omega2>-omegas and omega1<-omegas:
                omega=0.5*(omega2-omegas)
            #if sunset occurs in the interval
            elif omega2>omegas and omega1<omegas:
                omega=0.5*(omega1+omegas)
            #every other case
            else:
                omega=0.5*(omega2+omega1)
            return omega
     
        df['omega']=df.apply(lambda row: calc_omega(row.omega2,row.omega1,row.omegas), axis=1)
        
        def calc_costhetaz(delta2, omega, omegas):
            if omega<-omegas or omega>omegas:
                temp=0
            else:
                temp = math.sin(math.radians(delta2)) * math.sin(math.radians(data_params['phi'])) + \
                math.cos(math.radians(data_params['phi'])) * math.cos(math.radians(delta2)) * math.cos(math.radians(omega))
            return temp
        
        df['costhetaz'] = df.apply(lambda row: calc_costhetaz(row.delta2, row.omega, row.omegas), axis=1)
        df['thetaz2'] = [math.degrees(math.acos(x)) for x in df.costhetaz]
       
        def calc_singammas(delta2, omega, omegas, thetaz2):
            if omega<-omegas or omega>omegas:
                temp=0
                gammas=-90
            else:
                temp=math.cos(math.radians(delta2)) * math.sin(math.radians(omega)) / math.sin(math.radians(thetaz2))
                gammas=math.degrees(math.asin(temp))
            return temp, gammas
            
        df[['singammas','gammas2']] = df.apply(lambda row: pd.Series(calc_singammas(row.delta2, row.omega, row.omegas, row.thetaz2)), axis=1)

       
        return data_params, df
    
        
class manualInputs(insertionMethod):
    def __init__(self,standar_meridian_timezone,latitude,longitude,gamma,beta,area,theta = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
        self.Lst = standar_meridian_timezone
        self.phi = latitude
        self.Lloc = longitude
        self.gamma = gamma
        self.beta = beta
        self.theta = theta
        self.area = area

    def getInputs(self):
        data_params = {}
        data_params['Lst'] = self.Lst
        data_params['phi'] = self.phi
        data_params['Lloc'] = self.Lloc
        data_params['gamma'] = self.gamma
        data_params['beta'] = self.beta
        data_params['theta'] = self.theta
        data_params['area'] = self.area
        
        df = pd.DataFrame(index = list(range(0,8760)))
        #df.index = [pd.Timestamp('2021-01-01 00:00') + pd.Timedelta(hours=i) for i in df.index]
        #test so PV will start at hour 1 
        df.index = [pd.Timestamp('2021-01-01 1:00') + pd.Timedelta(hours=i) for i in df.index]
        dBeck_output = Duffie_Beckman.dataframe()
        dBeck = Duffie_Beckman.calculo(dBeck_output,data_params['Lst'],data_params['Lloc'],df)
        df = dBeck.start() 

        
        def B_calculation(B):          
            B = 180. / np.pi * (0.006918 - 0.399912 * math.cos(math.radians(B)) + 0.070257 * math.sin(math.radians(B))) + \
                180. / np.pi * (-0.006758 * math.cos(math.radians(2 * B)) + 0.000907 * math.sin(math.radians(2 * B))) + \
                180. / np.pi * (-0.002697 * math.cos(math.radians(3 * B)) + 0.00148 * math.sin(math.radians(3 * B)))
            return B
        df['delta2'] = df.B.apply(B_calculation)
        
        def calc_omegas(delta2,phi):
            return math.degrees(math.acos((-1)*(math.tan(math.radians(phi)))*(math.tan(math.radians(delta2)))))
        
        df['omegas']=df.apply(lambda row: calc_omegas(row.delta2,data_params['phi']), axis=1)
        
        
        def calc_omega(omega2,omega1,omegas):
            #if sunrise occurs in the interval
            if omega2>-omegas and omega1<-omegas:
                omega=0.5*(omega2-omegas)
            #if sunset occurs in the interval
            elif omega2>omegas and omega1<omegas:
                omega=0.5*(omega1+omegas)
            #every other case
            else:
                omega=0.5*(omega2+omega1)
            return omega
     
        df['omega']=df.apply(lambda row: calc_omega(row.omega2,row.omega1,row.omegas), axis=1)
        
        def calc_costhetaz(delta2, omega, omegas):
            if omega<-omegas or omega>omegas:
                temp=0
            else:
                temp = math.sin(math.radians(delta2)) * math.sin(math.radians(data_params['phi'])) + \
                math.cos(math.radians(data_params['phi'])) * math.cos(math.radians(delta2)) * math.cos(math.radians(omega))
            return temp
        
        df['costhetaz'] = df.apply(lambda row: calc_costhetaz(row.delta2, row.omega, row.omegas), axis=1)
        df['thetaz2'] = [math.degrees(math.acos(x)) for x in df.costhetaz]
       
        def calc_singammas(delta2, omega, omegas, thetaz2):
            if omega<-omegas or omega>omegas:
                temp=0
                gammas=-90
            else:
                temp=math.cos(math.radians(delta2)) * math.sin(math.radians(omega)) / math.sin(math.radians(thetaz2))
                gammas=math.degrees(math.asin(temp))
            return temp, gammas
            
        df[['singammas','gammas2']] = df.apply(lambda row: pd.Series(calc_singammas(row.delta2, row.omega, row.omegas, row.thetaz2)), axis=1)

                                
        return data_params, df
    
    
class insert:
    def __init__(self, insert : insertionMethod):
        self.insert = insert
         
    def start(self):        
        return self.insert.getInputs()
    
    

    
