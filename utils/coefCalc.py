# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 11:43:59 2023

@author: mcalcagnotto
"""
import pandas as pd
from abc import ABC, abstractmethod
import pytz
import math
import numpy as np

BXL = pytz.timezone('Europe/Brussels')


class typeCoef(ABC):
    def __init__(self,dataframe_consumption):       
        self.dr_cons = dataframe_consumption
    @abstractmethod
    def calculation(self):
        pass


# class CoefUnico(typeCoef):
#     def __init__(self, dataframe_consumption):
#         typeCoef.__init__(self, dataframe_consumption)
#         self.n_users=len(self.dr_cons.columns)
#     def calculation(self):
#         coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
#         for i in coef.columns:
#             coef[i]=1/self.n_users
#         return coef


class CoefUnico(typeCoef):
    def __init__(self, dataframe_consumption,num_v):
        typeCoef.__init__(self, dataframe_consumption)
        self.n_users=num_v
    def calculation(self):
        coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
        for i in coef.columns:
            coef[i]=1/self.n_users
        return coef
    
           
    
class CoefUnico_cp(typeCoef):
    def __init__(self, dataframe_consumption, num_v, coef_cp):
        typeCoef.__init__(self, dataframe_consumption)
        self.n_users=num_v
        self.coef_main=coef_cp
    def calculation(self):
        coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
        coef['Cbase']=self.coef_main
        for i in coef.columns[1:]:
            coef[i]=(1-self.coef_main)/(self.n_users-1)
        return coef

class CoefVar(typeCoef):
    def __init__(self, dataframe_consumption):
        typeCoef.__init__(self, dataframe_consumption)
        self.total=self.dr_cons.sum(axis=1)
    def calculation(self):
        #self.dr_cons['Total']=self.dr_cons.sum(axis=1)
        #self.dr_cons=pd.concat([self.dr_cons,self.dr_cons.sum(axis=1)],axis=1)
        # coef=pd.DataFrame(columns=self.dr_cons.columns)
        coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
        for i in coef.columns:
            coef[i]=self.dr_cons[i]/self.total
        
        #coef=coef.drop('Total',axis=1,inplace='True')
        return coef
    
    # coef=pd.DataFrame(index=cons_total.index,columns=cons_total.columns)
    # for column in cons_total.columns:
    #     coef[column]=cons_total[column]/cons_total['Total']

# class CoefVarW(typeCoef):
#   def __init__(self, dataframe_consumption):
#       typeCoef.__init__(self, dataframe_consumption)
#       self.total=self.dr_cons.sum(axis=1)
#   def calculation(self):
#       coef=pd.DataFrame(index=self.dr_cons.index,columns=self.dr_cons.columns)
#       for i in coef.columns:
#           for self.dr_cons.index.weekday()<5:
#               coef_wk=self.dr_cons[i].sum/self.total.sum
#           for self.dr_cons.index.weekday()>5:
#               coef_wd=self.dr_cons[i].sum/self.total.sum
    
        

#input contracted_P is a file with one line and n_users number of contracted Powers
#if the input has two contracted powers (punta y valle), we should add a line to compare and if they are different, select the maximum 
#eso hay que corregirlo para repetir
class CoefPow(typeCoef):
    def __init__(self, dataframe_consumption,power_contracted):
        typeCoef.__init__(self, dataframe_consumption)
        self.power=power_contracted
    def calculation(self):
        coef=pd.DataFrame(index=self.power.index,columns=self.power.columns)
        P_total=self.power.sum(axis=1)
        for i in coef.columns:
            coef[i]=self.power[i]/P_total
        return coef
    
    

    
    
# class balanceCEL(typeCoef):
#     def __init__(self, dataframe_consumption, number_of_users, dataframe_PV):
#         typeCoef.__init__(self, dataframe_consumption, number_of_users, dataframe_PV)    
#     def calculation(self):
#         self.ds_FV['Med_cel'] = self.dr_cons['Med'] * self.n_buildings
#         self.ds_FV['Sc_cel'] = [min(x) for x in (zip(self.ds_FV.Pv_cel, self.ds_FV.Med_cel))]
#         self.ds_FV['Dt_cel'] = self.ds_FV['Med_cel'] - self.ds_FV['Sc_cel']
#         self.ds_FV['Et_cel'] = self.ds_FV['Pv_cel'] - self.ds_FV['Sc_cel']  # CP
#         self.ds_FV['Net_cel'] = self.ds_FV['Dt_cel'] - self.ds_FV['Et_cel']  # CP
#         if self.ds_FV.Med_cel.sum() != 0:
#             LoCov = (self.ds_FV.Sc_cel.sum() / self.ds_FV.Med_cel.sum()) * 100  # CP
#         else:
#             LoCov = 0            
#         return self.ds_FV, LoCov


# class balanceCombinado(typeCoef):
#     def __init__(self, dataframe_consumption, number_of_users, dataframe_PV,dataframe_consumption_CEL,number_of_users_CEL,dataframe_PV_CEL): 
#         self.dr_cons = []
#         self.n_buildings = []
#         self.dr_cons.append(dataframe_consumption)
#         self.dr_cons.append(dataframe_consumption_CEL)
#         self.n_buildings.append(number_of_users)
#         self.n_buildings.append(number_of_users_CEL)
#         self.df_FV_propio = dataframe_PV
#         self.df_FV_CEL = dataframe_PV_CEL
#     def calculation(self): 
#         ds_FV_propio, LoCov = balancePropio(self.dr_cons[0], self.n_buildings[0], self.df_FV_propio).calculation()
#         ds_FV_cel, LoCov_cel = balanceCEL(self.dr_cons[1], self.n_buildings[1], self.df_FV_CEL).calculation()
#         ds_FV = pd.concat([ds_FV_propio,ds_FV_cel], axis = 1)
#         cons_combinado = pd.DataFrame()
#         cons_combinado['Cons'] = ds_FV['Med_cp'] + ds_FV['Med_cel']
#         ds_FV['PvT_cp_cel'] = ds_FV['Pv_base'] + ds_FV['Pv_cel']
#         ds_FV['Sc_cp_cel'] = [min(x) for x in zip(ds_FV.PvT_cp_cel, cons_combinado.Cons)]
#         ds_FV['Dt_cp_cel'] = cons_combinado['Cons'] - ds_FV['Sc_cp_cel']  # CP + CEL
#         ds_FV['Et_cp_cel'] = ds_FV['PvT_cp_cel'] - ds_FV['Sc_cp_cel']  # CP + CEL
#         ds_FV['Net_cp_cel'] = ds_FV['Dt_cp_cel'] - ds_FV['Et_cp_cel']  # CP + CEL  
        
#         if  ds_FV.Med_cel.sum() != 0:
#             LoCov_viv = (ds_FV.Sc_cp_cel.sum()-ds_FV.Sc.sum())/ds_FV.Med_cel.sum() * 100  
#         else:
#             LoCov_viv = 0
#         if cons_combinado.Cons.sum() != 0:  
#             LoCov_cp_cel = (ds_FV.Sc_cp_cel.sum() /cons_combinado.Cons.sum()) * 100  # CEL
#         else:
#             LoCov_cp_cel = 0
#         LoCov = [LoCov, LoCov_cel,LoCov_viv ,LoCov_cp_cel]
#         return ds_FV, LoCov
    
    
# class balanceCombinadoCoef(typeCoef):
#     def __init__(self, dataframe_consumption, number_of_users, dataframe_PV,dataframe_consumption_CEL,number_of_users_CEL,dataframe_PV_CEL,coef,coef_2): 
#         self.dr_cons = []
#         self.n_buildings = []
#         self.dr_cons.append(dataframe_consumption)
#         self.dr_cons.append(dataframe_consumption_CEL)
#         self.n_buildings.append(number_of_users)
#         self.n_buildings.append(number_of_users_CEL)
#         self.df_FV_propio_copy = dataframe_PV.copy(deep = True)
#         self.df_FV_CEL = dataframe_PV_CEL
#         self.coef = coef
#         self.coef_2=coef_2
#     def calculation(self): 
        
#        # self.df_FV_propio_copy['Pv_base'] = self.df_FV_propio_copy['Pv_base'].apply(lambda x: x * self.coef)
#         self.df_FV_propio_copy['Pv_base'] = self.df_FV_propio_copy['Pv_base']*self.coef
#         ds_FV_propio, LoCov = balancePropio(self.dr_cons[0], self.n_buildings[0], self.df_FV_propio_copy).calculation()
#         ds_FV_cel, LoCov_cel = balanceCEL(self.dr_cons[1], self.n_buildings[1], self.df_FV_CEL).calculation()
#         ds_FV = pd.concat([ds_FV_propio,ds_FV_cel], axis = 1)
#         ds_FV['Cons_total'] = ds_FV['Med_cp'] + ds_FV['Med_cel']
        
#        # ds_FV['Pv_base_cel'] = self.df_FV_propio_copy['Pv_base'].apply(lambda x: x/self.coef * (1-self.coef))
#         ds_FV['Pv_base_cel'] = self.df_FV_propio_copy['Pv_base']/self.coef*self.coef_2
#         ds_FV['Sc_cel_2'] =  [min(x) for x in zip(ds_FV['Pv_base_cel'], ds_FV.Med_cel)]   
#       #  ds_FV['Pv_base'] = ds_FV['Pv_base'].apply(lambda x: x / self.coef)
#         ds_FV['Pv_base'] = ds_FV['Pv_base']*self.coef
#         ds_FV['PvT_cp_cel'] = ds_FV['Pv_base'] + ds_FV['Pv_cel']
        
#         ds_FV['Sc_cp_cel'] = ds_FV.Sc + ds_FV.Sc_cel_2

        
#         ds_FV['Dt_cp_cel'] = ds_FV['Cons_total'] - ds_FV['Sc_cp_cel']  # CP + CEL
#         ds_FV['Et_cp_cel'] = ds_FV['PvT_cp_cel'] - ds_FV['Sc_cp_cel']  # CP + CEL
#         ds_FV['Net_cp_cel'] = ds_FV['Dt_cp_cel'] - ds_FV['Et_cp_cel']  # CP + CEL  
        
#         if  ds_FV.Med_cel.sum() != 0:
#             LoCov_viv = (ds_FV.Sc_cp_cel.sum()-ds_FV.Sc.sum())/ds_FV.Med_cel.sum() * 100  
#         else:
#             LoCov_viv = 0
#         if ds_FV.Cons_total.sum() != 0:  
#             LoCov_cp_cel = (ds_FV.Sc_cp_cel.sum() /ds_FV.Cons_total.sum()) * 100  # CEL
#         else:
#             LoCov_cp_cel = 0
#         LoCov = [LoCov, LoCov_cel,LoCov_viv ,LoCov_cp_cel]
#         return ds_FV, LoCov    


class calculo:
    def __init__(self, outputType: typeCoef):
        self.outputType = outputType

    def start(self):
        return self.outputType.calculation()
    
    np.array
