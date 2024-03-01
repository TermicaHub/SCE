# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:51:06 2022

@author: srabadan
"""

import pandas as pd
from abc import ABC, abstractmethod
import pytz
import math

BXL = pytz.timezone('Europe/Brussels')


class typeBalance(ABC):
    def __init__(self,dataframe_consumption, dataframe_PV):       
        self.dr_cons = dataframe_consumption
        self.ds_FV = dataframe_PV
    @abstractmethod
    def calculation(self):
        pass


class balancePropio(typeBalance):
    def __init__(self, dataframe_consumption, number_of_buildings, dataframe_PV):
        typeBalance.__init__(self, dataframe_consumption, dataframe_PV)
        self.n_buildings=number_of_buildings
    def calculation(self):
        self.ds_FV['Med_cp'] = self.dr_cons['Med'] * self.n_buildings
        self.ds_FV['Sc'] = [min(x) for x in (zip(self.ds_FV.Pv_base, self.ds_FV.Med_cp))]
        self.ds_FV['Dt'] = self.ds_FV['Med_cp'] - self.ds_FV['Sc']
        self.ds_FV['Et'] = self.ds_FV['Pv_base'] - self.ds_FV['Sc']  # CP
        self.ds_FV['Net'] = self.ds_FV['Dt'] - self.ds_FV['Et']  # CP
        if self.ds_FV.Med_cp.sum() !=0:
            LoCov = (self.ds_FV.Sc.sum() / self.ds_FV.Med_cp.sum()) * 100  # CP
        else:
            LoCov = 0
        return self.ds_FV, LoCov


class balanceCEL(typeBalance):
    def __init__(self, dataframe_consumption, number_of_buildings, dataframe_PV):
        typeBalance.__init__(self, dataframe_consumption, dataframe_PV) 
        self.n_buildings=number_of_buildings
    def calculation(self):
        self.ds_FV['Med_cel'] = self.dr_cons['Med'] * self.n_buildings
        self.ds_FV['Sc_cel'] = [min(x) for x in (zip(self.ds_FV.Pv_cel, self.ds_FV.Med_cel))]
        self.ds_FV['Dt_cel'] = self.ds_FV['Med_cel'] - self.ds_FV['Sc_cel']
        self.ds_FV['Et_cel'] = self.ds_FV['Pv_cel'] - self.ds_FV['Sc_cel']  # CP
        self.ds_FV['Net_cel'] = self.ds_FV['Dt_cel'] - self.ds_FV['Et_cel']  # CP
        if self.ds_FV.Med_cel.sum() != 0:
            LoCov = (self.ds_FV.Sc_cel.sum() / self.ds_FV.Med_cel.sum()) * 100  # CP
        else:
            LoCov = 0            
        return self.ds_FV, LoCov


class balanceCombinado(typeBalance):
    def __init__(self, dataframe_consumption, number_of_buildings, dataframe_PV,dataframe_consumption_CEL,number_of_buildings_CEL,dataframe_PV_CEL): 
        self.dr_cons = []
        self.n_buildings = []
        self.dr_cons.append(dataframe_consumption)
        self.dr_cons.append(dataframe_consumption_CEL)
        self.n_buildings.append(number_of_buildings)
        self.n_buildings.append(number_of_buildings_CEL)
        self.df_FV_propio = dataframe_PV
        self.df_FV_CEL = dataframe_PV_CEL
    def calculation(self): 
        ds_FV_propio, LoCov = balancePropio(self.dr_cons[0], self.n_buildings[0], self.df_FV_propio).calculation()
        ds_FV_cel, LoCov_cel = balanceCEL(self.dr_cons[1], self.n_buildings[1], self.df_FV_CEL).calculation()
        ds_FV = pd.concat([ds_FV_propio,ds_FV_cel], axis = 1)
        cons_combinado = pd.DataFrame()
        cons_combinado['Cons'] = ds_FV['Med_cp'] + ds_FV['Med_cel']
        ds_FV['PvT_cp_cel'] = ds_FV['Pv_base'] + ds_FV['Pv_cel']
        ds_FV['Sc_cp_cel'] = [min(x) for x in zip(ds_FV.PvT_cp_cel, cons_combinado.Cons)]
        ds_FV['Dt_cp_cel'] = cons_combinado['Cons'] - ds_FV['Sc_cp_cel']  # CP + CEL
        ds_FV['Et_cp_cel'] = ds_FV['PvT_cp_cel'] - ds_FV['Sc_cp_cel']  # CP + CEL
        ds_FV['Net_cp_cel'] = ds_FV['Dt_cp_cel'] - ds_FV['Et_cp_cel']  # CP + CEL  
        
        if  ds_FV.Med_cel.sum() != 0:
            LoCov_viv = (ds_FV.Sc_cp_cel.sum()-ds_FV.Sc.sum())/ds_FV.Med_cel.sum() * 100  
        else:
            LoCov_viv = 0
        if cons_combinado.Cons.sum() != 0:  
            LoCov_cp_cel = (ds_FV.Sc_cp_cel.sum() /cons_combinado.Cons.sum()) * 100  # CEL
        else:
            LoCov_cp_cel = 0
        LoCov = [LoCov, LoCov_cel,LoCov_viv ,LoCov_cp_cel]
        return ds_FV, LoCov
    
    
class balanceCombinadoCoef(typeBalance):
    def __init__(self, dataframe_consumption, number_of_buildings, dataframe_PV,dataframe_consumption_CEL,number_of_buildings_CEL,dataframe_PV_CEL,coef): 
        self.dr_cons = []
        self.n_buildings = []
        self.dr_cons.append(dataframe_consumption)
        self.dr_cons.append(dataframe_consumption_CEL)
        self.n_buildings.append(number_of_buildings)
        self.n_buildings.append(number_of_buildings_CEL)
        self.df_FV_propio_copy = dataframe_PV.copy(deep = True)
        self.df_FV_CEL = dataframe_PV_CEL
        self.coef = coef
    def calculation(self): 
        
        self.df_FV_propio_copy['Pv_base'] = self.df_FV_propio_copy['Pv_base'].apply(lambda x: x * self.coef)
        ds_FV_propio, LoCov = balancePropio(self.dr_cons[0], self.n_buildings[0], self.df_FV_propio_copy).calculation()
        ds_FV_cel, LoCov_cel = balanceCEL(self.dr_cons[1], self.n_buildings[1], self.df_FV_CEL).calculation()
        ds_FV = pd.concat([ds_FV_propio,ds_FV_cel], axis = 1)
        ds_FV['Cons_total'] = ds_FV['Med_cp'] + ds_FV['Med_cel']
        
        ds_FV['Pv_base_cel'] = self.df_FV_propio_copy['Pv_base'].apply(lambda x: x/self.coef * (1-self.coef))
        ds_FV['Sc_cel_2'] =  [min(x) for x in zip(ds_FV['Pv_base_cel'], ds_FV.Med_cel)]   
        ds_FV['Pv_base'] = ds_FV['Pv_base'].apply(lambda x: x / self.coef)
        ds_FV['PvT_cp_cel'] = ds_FV['Pv_base'] + ds_FV['Pv_cel']
        
        ds_FV['Sc_cp_cel'] = ds_FV.Sc + ds_FV.Sc_cel_2

        
        ds_FV['Dt_cp_cel'] = ds_FV['Cons_total'] - ds_FV['Sc_cp_cel']  # CP + CEL
        ds_FV['Et_cp_cel'] = ds_FV['PvT_cp_cel'] - ds_FV['Sc_cp_cel']  # CP + CEL
        ds_FV['Net_cp_cel'] = ds_FV['Dt_cp_cel'] - ds_FV['Et_cp_cel']  # CP + CEL  
        
        if  ds_FV.Med_cel.sum() != 0:
            LoCov_viv = (ds_FV.Sc_cp_cel.sum()-ds_FV.Sc.sum())/ds_FV.Med_cel.sum() * 100  
        else:
            LoCov_viv = 0
        if ds_FV.Cons_total.sum() != 0:  
            LoCov_cp_cel = (ds_FV.Sc_cp_cel.sum() /ds_FV.Cons_total.sum()) * 100  # CEL
        else:
            LoCov_cp_cel = 0
        LoCov = [LoCov, LoCov_cel,LoCov_viv ,LoCov_cp_cel]
        return ds_FV, LoCov    


class balancePropioSomCom(typeBalance):
    def __init__(self, dataframe_consumption, dataframe_PV):
        self.dr_cons=dataframe_consumption
        #self.ds_FV=dataframe_PV
        self.ds_reparto=dataframe_PV
        #typeBalance.__init__(self, dataframe_consumption,dataframe_PV)
    def calculation(self):
        df_balance=pd.DataFrame(index=self.ds_reparto.index)
        df_balance['Pv_base']=self.ds_reparto
        df_balance['Med'] = self.dr_cons
        df_balance['Sc'] = [min(x) for x in (zip(df_balance.Pv_base, df_balance.Med))]
        df_balance['Dt'] = df_balance['Med'] - df_balance['Sc']
        df_balance['Et'] = df_balance['Pv_base'] - df_balance['Sc']  
        df_balance['Net'] = df_balance['Dt'] - df_balance['Et']  
        if df_balance.Med.sum() !=0:
            LoCov = (df_balance.Sc.sum() / df_balance.Med.sum()) * 100  
        else:
            LoCov = 0
        #self.ds_FV['Med_cp'] = self.dr_cons['Med'] * self.n_buildings
        # self.ds_FV['Med_cp'] = self.dr_cons
        # self.ds_FV['Sc_cp'] = [min(x) for x in (zip(self.ds_FV.Pv_base, self.ds_FV.Med_cp))]
        # self.ds_FV['Dt_cp'] = self.ds_FV['Med_cp'] - self.ds_FV['Sc_cp']
        # self.ds_FV['Et_cp'] = self.ds_FV['Pv_base'] - self.ds_FV['Sc_cp']  # CP
        # self.ds_FV['Net_cp'] = self.ds_FV['Dt_cp'] - self.ds_FV['Et_cp']  # CP
        # if self.ds_FV.Med_cp.sum() !=0:
        #     LoCov = (self.ds_FV.Sc_cp.sum() / self.ds_FV.Med_cp.sum()) * 100  # CP
        # else:
        #     LoCov = 0
        return df_balance, LoCov
    
# class balanceCELSomCom(typeBalance):
#     def __init__(self, dataframe_consumption, dataframe_PV):
#         typeBalance.__init__(self, dataframe_consumption, dataframe_PV)    
#     def calculation(self):
#        # self.ds_FV['Med_cel'] = self.dr_cons['Med'] * self.n_buildings
#         self.ds_FV['Med_cel'] = self.dr_cons['CEL'] 
#         self.ds_FV['Sc_cel'] = [min(x) for x in (zip(self.ds_FV.Pv_cel, self.ds_FV.Med_cel))]
#         self.ds_FV['Dt_cel'] = self.ds_FV['Med_cel'] - self.ds_FV['Sc_cel']
#         self.ds_FV['Et_cel'] = self.ds_FV['Pv_cel'] - self.ds_FV['Sc_cel']  # CP
#         self.ds_FV['Net_cel'] = self.ds_FV['Dt_cel'] - self.ds_FV['Et_cel']  # CP
#         if self.ds_FV.Med_cel.sum() != 0:
#             LoCov = (self.ds_FV.Sc_cel.sum() / self.ds_FV.Med_cel.sum()) * 100  # CP
#         else:
#             LoCov = 0            
#         return self.ds_FV, LoCov
    
# class balanceCombinadoSomCom(typeBalance):
#     def __init__(self, dataframe_consumption, dataframe_PV_total,coef): 
#         # self.dr_cons = []
#         # self.dr_cons.append(dataframe_consumption)
#         # self.dr_cons.append(dataframe_consumption_CEL)
#         self.dr_cons = dataframe_consumption
#        # self.df_FV_total_copy = dataframe_PV_total.copy(deep = True)
#         self.df_FV_total = dataframe_PV_total
#         self.coef = coef

#     def calculation(self): 
#         df_FV_reparto=pd.DataFrame()
#         # self.df_FV_propio_copy['Pv_base'] = self.df_FV_propio_copy['Pv_base'].apply(lambda x: x * self.coef)
#         df_FV_reparto['Pv_base']=self.df_FV_total['Pv_base']*self.coef['Cbase']
#         #self.df_FV_total_copy['Pv_base'] = self.df_FV_total_copy['Pv_base']*self.coef['Cbase']
#         #ds_FV_propio, LoCov_propio = balancePropioSomCom(self.dr_cons, df_FV_reparto.loc[:,['Pv_base']]).calculation()
#         ds_FV_propio, LoCov_propio = balancePropioSomCom(self.dr_cons, df_FV_reparto.loc[:,['Pv_base']]).calculation()
       
#         df_FV_reparto['Pv_cel'] = self.df_FV_total['Pv_base']*self.coef['Ccel']
#         ds_FV_CEL, LoCov_CEL = balanceCELSomCom(self.dr_cons, df_FV_reparto.loc[:,['Pv_cel']]).calculation()
#         ds_FV = pd.concat([ds_FV_propio,ds_FV_CEL], axis = 1)
       
                   
#         ds_FV['Med_total'] =  self.dr_cons['Total']
#         ds_FV['Sc_total'] = ds_FV['Sc_cp'] +   ds_FV['Sc_cel'] 
#         ds_FV['Dt_total'] =  ds_FV['Dt_cp'] +   ds_FV['Dt_cel'] 
#         ds_FV['Et_total'] = ds_FV['Et_cp'] +   ds_FV['Et_cel'] 
#         ds_FV['Net_total'] = ds_FV['Net_cp'] +   ds_FV['Net_cel'] 
        
              
#         if  self.dr_cons['Total'].sum!= 0:  
#             LoCov_total = (ds_FV.Sc_total.sum() /ds_FV.Med_total.sum()) * 100  
#         else:
#             LoCov_total = 0
        
       
#         LoCov = {'LoCov_main':LoCov_propio, 'LoCov_CEL':LoCov_CEL, 'LoCov_agregado':LoCov_total}
#         return ds_FV, LoCov    


class balanceCombinadoCoefSomCom(typeBalance):
    def __init__(self, dataframe_consumption, dataframe_PV_total,coef_reparto): 
        self.dr_cons = dataframe_consumption
        self.df_FV_total = dataframe_PV_total
        self.coef = coef_reparto

    def calculation(self): 
        
        df_FV_reparto=pd.DataFrame()
        df_balance={}
        df_balance['Total']=pd.DataFrame(index=self.dr_cons.index)

        df_total_sc=pd.DataFrame(index=self.dr_cons.index)
        df_total_dt=pd.DataFrame(index=self.dr_cons.index)
        df_total_et=pd.DataFrame(index=self.dr_cons.index)
        df_total_net=pd.DataFrame(index=self.dr_cons.index)
        
        df_Sc_all=pd.Series()
        df_Med_all=pd.Series()
        df_LoCov_all=pd.Series()
        #para cada consumidor del dataframe de consumos
        for i in self.dr_cons.columns:
           
            #df_FV_reparto['Pv_base']=self.df_FV_total['Pv_base'].apply(lambda x: x * self.coef[i])
            df_FV_reparto['Pv_base']=self.df_FV_total['Pv_base']*self.coef[i]
            ds_FV_propio, LoCov_propio = balancePropioSomCom(self.dr_cons[i], df_FV_reparto).calculation()
            

            df_total_sc[i]=ds_FV_propio['Sc']
            df_total_dt[i]=ds_FV_propio['Dt']
            df_total_et[i]=ds_FV_propio['Et']
            df_total_net[i]=ds_FV_propio['Net']
            
            df_Med_all[i]=ds_FV_propio['Med'].sum()
            df_Sc_all[i]=ds_FV_propio['Sc'].sum()
            #guardar resultado de balance horario en un diccionario
            df_balance[i]=ds_FV_propio
            #guardar resultado LoCov invididuales en una serie
            df_LoCov_all[i]=LoCov_propio
            #agregar en el Net y Med total 
            #df_balance['Total']['Net']=df_balance['Total']['Net']+df_balance[i]['Net']
            #df_balance['Total']['Med']=df_balance['Total']['Med']+df_balance[i]['Med']
        df_balance['Total']['Med']=self.dr_cons.sum(axis=1)
        df_balance['Total']['Sc']=df_total_sc.sum(axis=1)
        df_balance['Total']['Dt']=df_total_dt.sum(axis=1)
        df_balance['Total']['Et']=df_total_et.sum(axis=1)
        df_balance['Total']['Net']=df_total_net.sum(axis=1)
        #LoCov para toda la comunidad agregada
        LoCov_ag=(df_Sc_all.sum()/df_Med_all.sum())*100
        return df_balance, df_LoCov_all,LoCov_ag
        
            
            
        # self.df_FV_propio_copy['Pv_base'] = self.df_FV_propio_copy['Pv_base'].apply(lambda x: x * self.coef)
       # df_FV_reparto['Pv_base']=self.df_FV_total['Pv_base']*self.coef['Cbase']
        #self.df_FV_total_copy['Pv_base'] = self.df_FV_total_copy['Pv_base']*self.coef['Cbase']
        #ds_FV_propio, LoCov_propio = balancePropioSomCom(self.dr_cons, df_FV_reparto.loc[:,['Pv_base']]).calculation()
        #ds_FV_propio, LoCov_propio = balancePropioSomCom(self.dr_cons, df_FV_reparto.loc[:,['Pv_base']]).calculation()
       
        #df_FV_reparto['Pv_cel'] = self.df_FV_total['Pv_base']*self.coef['Ccel']
        #ds_FV_CEL, LoCov_CEL = balanceCELSomCom(self.dr_cons, df_FV_reparto.loc[:,['Pv_cel']]).calculation()
        #ds_FV = pd.concat([ds_FV_propio,ds_FV_CEL], axis = 1)
       
                   
        # ds_FV['Med_total'] =  self.dr_cons['Total']
        # ds_FV['Sc_total'] = ds_FV['Sc_cp'] +   ds_FV['Sc_cel'] 
        # ds_FV['Dt_total'] =  ds_FV['Dt_cp'] +   ds_FV['Dt_cel'] 
        # ds_FV['Et_total'] = ds_FV['Et_cp'] +   ds_FV['Et_cel'] 
        # ds_FV['Net_total'] = ds_FV['Net_cp'] +   ds_FV['Net_cel'] 
        
              
        # if  self.dr_cons['Total'].sum!= 0:  
        #     LoCov_total = (ds_FV.Sc_total.sum() /ds_FV.Med_total.sum()) * 100  
        # else:
        #     LoCov_total = 0
        
       
        # LoCov = {'LoCov_main':LoCov_propio, 'LoCov_CEL':LoCov_CEL, 'LoCov_agregado':LoCov_total}
        #return ds_FV, LoCov   


class calculo:
    def __init__(self, outputType: typeBalance):
        self.outputType = outputType

    def start(self):
        return self.outputType.calculation()
