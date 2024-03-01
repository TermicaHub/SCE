# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 15:07:47 2024

@author: mcalcagnotto
"""
import pandas as pd

# # Abstract method import

# from abc import ABC, abstractmethod


# Resources

from repositories import repositoryConsumption


# Abstract class

# class currencyType(ABC):
#     @abstractmethod
#     #def __init__(self,oc_viv)
#     #def __init__(self,oc_viv,consum_viv,heat_viv,acc_viv,acs_viv,coc_viv,hor_viv):
#         #numero de ocupantes de la vivienda
#         #self.n_occ=oc_viv
#         # self.consum=consum_viv
#         # self.heat=heat_viv
#         # self.acc=acc_viv
#         # self.acs=acs_viv
#         # self.kitchen=coc_viv
#         # self.oven=hor_viv
#     def dataSource(self):
#         pass

class ConsBuilding:
    def __init__(self,n_part,oc_viv,dhw_num,coc_num,hor_num,heat_rad_num,heat_hp_num,acc_split_num,acc_hp_num,area_viv,consum_viv):
        
        self.num_v=n_part
        self.n_occ=oc_viv
        self.n_dhw=dhw_num
        self.n_kitchen=coc_num
        self.n_oven=hor_num
        self.n_heat_rad=heat_rad_num
        self.n_heat_hp=heat_hp_num
        self.n_acc_split=acc_split_num
        self.n_acc_hp=acc_hp_num
        self.area=area_viv
        self.consum=consum_viv
        
    def file_cons(self):
        c_output = repositoryConsumption.SomProfiles(self.n_occ)
        cons = repositoryConsumption.get_data(c_output)
        dataSom = cons.start()
        
        return dataSom
    

    def cons_eq(self):
        profiles_base=self.file_cons()
        profiles_eq=pd.DataFrame(index=profiles_base.index)
        profiles_eq['ConsEq']=[0]*8760
        
        profiles_eq['Base']=profiles_base['ConBase']
        
        if self.n_dhw>0:
            profiles_eq['DHW']=profiles_base['ConDHW']*self.n_dhw

        if self.n_kitchen>0:
            profiles_eq['Stove']=profiles_base['ConStove']*self.n_kitchen

        if self.n_oven>0:
            profiles_eq['Oven']=profiles_base['ConOven']*self.n_oven


        profiles_eq['ConsEq']=profiles_eq.sum(axis=1)
            
        return profiles_eq['ConsEq']
    

    def cons_hvac(self):
        profiles_base=self.file_cons()
        profiles_clima=pd.DataFrame(index=profiles_base.index)
        profiles_clima['ConsClima']=[0]*8760
        if self.n_heat_rad>0:
            #radiador electrico, eficiencia=1, 30% cobertura area y 80% horas
                        
            profiles_clima['ConsHeat']=profiles_base['Qheat']*self.area*0.3*0.8*self.n_heat_rad
        elif self.n_heat_hp>0:
            #bomba de calor, COP=2.63, 100% cobertura area y 80% horas
            profiles_clima['ConsHeat']=(profiles_base['Qheat']*self.area)/2.63*0.8*self.n_heat_hp
            
        if self.n_acc_split>0:
            #split eficiencia=2, 30% cobertura area y 80% horas
            profiles_clima['ConsCool']=(profiles_base['Qcool']*self.area)/2*0.3*0.8*self.n_acc_split

        elif self.n_acc_hp>0:
            #bomba de calor=3.72, 100% cobertura area y 80% horas
            profiles_clima['ConsCool']=(profiles_base['Qcool']*self.area)/3.72*0.8*self.n_acc_hp
        
        profiles_clima['ConsClima']=profiles_clima.sum(axis=1)


        return profiles_clima['ConsClima'] 
 
        
    def cons_total(self):

        profile_sum=pd.DataFrame()
        profile_sum['ConsEq']=self.cons_eq()
        profile_sum['ConsClima']=self.cons_hvac()
        profile_sum['Sum']=profile_sum.sum(axis=1)
        
        # if self.num_v==1:
        #     c_ref=[3400,3850,4000,4150,4450,4800] 
        
        # elif self.num_v>1:
        #     c_ref=[1700,2100,2280,2400,2700,3000]
            
        
        year_cons=profile_sum['Sum'].sum()
        profile_sum['norm']= profile_sum['Sum']/year_cons
        profile_total=pd.DataFrame()
        profile_total['Total']=profile_sum['norm']*self.consum*self.num_v
        
        return profile_total


# class get_data:
#     def __init__(self, typeFile: currencyType):
#         self.typeFile = typeFile

#     def start(self):
#         return self.typeFile.dataSource()