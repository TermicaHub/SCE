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
#         # self.stove=coc_viv
#         # self.oven=hor_viv
#     def dataSource(self):
#         pass

class ConsBase:
    def __init__(self,oc_viv,dhw_viv,coc_viv,hor_viv,heat_viv,acc_viv,area_viv,numV,consum_viv):
        self.n_occ=oc_viv
        self.dhw=dhw_viv
        self.stove=coc_viv
        self.oven=hor_viv
        self.heat=heat_viv
        self.acc=acc_viv
        self.area=area_viv
        self.num_v=numV
        self.consum=consum_viv
        
    def file_cons(self):
        c_output = repositoryConsumption.SomProfiles(self.n_occ)
        cons = repositoryConsumption.get_data(c_output)
        dataSom = cons.start()
        
        return dataSom
    

    def cons_eq(self):
        profiles_base=self.file_cons()
        profiles_eq=pd.DataFrame(index=profiles_base.index)
        profiles_eq['ConEq']=[0]*8760
        
        #profiles_eq['Base']=profiles_base['ConBase']
        
        if self.dhw==1:
            profiles_eq['DHW']=profiles_base['ConDHW']

        if self.stove==1:
            profiles_eq['Stove']=profiles_base['ConStove']

        if self.oven==1:
            profiles_eq['Oven']=profiles_base['ConOven']


        profiles_eq['ConEq']=profiles_eq.sum(axis=1)
            
        return profiles_base['ConBase'],profiles_eq['ConEq']
    

    def cons_hvac(self):
        profiles_base=self.file_cons()
        profiles_clima=pd.DataFrame(index=profiles_base.index)
        profiles_clima['ConClima']=[0]*8760
        if self.heat=="heat_rad":
            #radiador electrico, eficiencia=1, 30% cobertura area y 80% horas
                        
            profiles_clima['ConHeat']=profiles_base['Qheat']*self.area*0.3*0.8
        elif self.heat=="heat_hp":
            #bomba de calor, COP=2.63, 100% cobertura area y 80% horas
            profiles_clima['ConHeat']=(profiles_base['Qheat']*self.area)/2.63*0.8
            
        if self.acc=="acc_split":
            #split eficiencia=2, 30% cobertura area y 80% horas
            profiles_clima['ConCool']=(profiles_base['Qcool']*self.area)/2*0.3*0.8

        elif self.acc=="acc_hp":
            #bomba de calor=3.72, 100% cobertura area y 80% horas
            profiles_clima['ConCool']=(profiles_base['Qcool']*self.area)/3.72*0.8
        
        profiles_clima['ConClima']=profiles_clima.sum(axis=1)


        return profiles_clima['ConClima'] 
 
        
    def cons_total(self):

        profile_sum=pd.DataFrame()
        profile_sum['ConBase'],profile_sum['ConEq']=self.cons_eq()
        profile_sum['ConClima']=self.cons_hvac()
        profile_sum['Sum']=profile_sum.sum(axis=1)
        #suma consumo total estimado
        year_cons=profile_sum['Sum'].sum()
        
        #lo compara con el valor informado por el usuario 
        #si hay un error más alto del 5% hay que ajustar el perfil base
        if abs(1-(self.consum/year_cons))>0.05:  
            new_cons_base=self.consum-(profile_sum['ConClima'].sum())-(profile_sum['ConEq'].sum())
            #asegurarse que el consumo clima y consumo eq. sumados no son más altos que el consumo informado por el usuario
            if (profile_sum['ConClima'].sum()+profile_sum['ConEq'].sum())<self.consum:
                profile_sum['ConBasenew']=(profile_sum['ConBase']/profile_sum['ConBase'].sum())*new_cons_base
                profile_sum['Sum']=profile_sum[['ConBasenew','ConClima','ConEq']].sum(axis=1)
            #si lo es, ajustamos el consumo agregado, no solo el perfil base
            else:
                profile_sum['Sum']=profile_sum['Sum']/year_cons*self.consum
        
        #profile_sum['Sum']=profile_sum[['ConBasenew','ConClima','ConEq']].sum(axis=1)

        # year_cons=profile_sum['Sum'].sum()
        # profile_sum['norm']= profile_sum['Sum']/year_cons
        profile_total=pd.DataFrame()
        profile_total['Total']=profile_sum['Sum']
        
        return profile_total

        

# class get_data:
#     def __init__(self, typeFile: currencyType):
#         self.typeFile = typeFile

#     def start(self):
#         return self.typeFile.dataSource()