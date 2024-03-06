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

class ConsSimple:
    def __init__(self,numV):
        self.num_v=numV
     
    def file_cons(self):
        c_output = repositoryConsumption.SomProfilesSimple()
        cons = repositoryConsumption.get_data(c_output)
        dataSom = cons.start()
                
        return dataSom
    
    def cons_total(self):

       
        profiles=self.file_cons()
        profile_base=profiles['ConBase']
        
        if self.num_v==1:
            cons_y=profile_base.sum()
            profile_base=profile_base/cons_y*4000
        
        elif self.num_v>1:
            cons_y=profile_base.sum()
            profile_base=self.num_v*profile_base/cons_y*2280
            
        profile_total=pd.DataFrame()
        profile_total['Cons_total']=profile_base
        
        return profile_total
        

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


class ConsBuilding:
    def __init__(self,n_part,oc_viv,dhw_num,coc_num,hor_num,heat_none_num,heat_rad_num,heat_hp_num,heat_gas_num,acc_none_num,acc_split_num,acc_hp_num,area_viv,consum_viv):
        
        self.num_v=n_part
        self.n_occ=oc_viv
        self.n_dhw=dhw_num
        self.n_stove=coc_num
        self.n_oven=hor_num
        self.n_heat_none=heat_none_num
        self.n_heat_rad=heat_rad_num
        self.n_heat_hp=heat_hp_num
        self.n_heat_gas=heat_gas_num
        self.n_acc_none=acc_none_num
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
        
        #profiles_eq_all=pd.DataFrame(index=profiles_base.index)
        
        #profile_empty=pd.DataFrame({'Column0': [0] * 8760},index=profiles_base.index)
        #profiles_eq['ConTot']=[0]*8760
        
        #profiles_eq['ConBase']=profiles_base['ConBase']*self.num_v
        
        if self.n_dhw>0:
            profiles_eq['ConDHW'] = profiles_base['ConDHW']*self.n_dhw
       
        if self.n_stove>0:
            profiles_eq['ConStove'] =profiles_base['ConStove']*self.n_stove
     
        if self.n_oven>0:
            profiles_eq['ConOven']=profiles_base['ConOven']*self.n_oven
            
                   

        profiles_eq['ConTotEq']=profiles_eq.sum(axis=1)
        
        # column_min = (profiles_eq_all.sum()).idxmin()
        # profiles_eq['ConMin']=profiles_eq_all[column_min]    
        
        # column_max = (profiles_eq.sum()).idxmax()
        # profiles_eq['ConMax']=profiles_eq_all[column_max]
        
        #profiles_eq['ConMean']=profiles_eq_all.mean(axis=1)
        
        return profiles_eq
       

    def cons_hvac(self):
        profiles_base=self.file_cons()
        #profiles_clima_all=pd.DataFrame(index=profiles_base.index)
        profiles_clima=pd.DataFrame(index=profiles_base.index)
        #profiles_clima['ConClima']=[0]*8760

        if self.n_heat_rad>0:
            #radiador electrico, eficiencia=1, 30% cobertura area y 80% horas
                    
            profiles_clima['ConHeatRad']=profiles_base['Qheat']*self.area*0.3*0.8*self.n_heat_rad
        if self.n_heat_hp>0:
            #bomba de calor, COP=2.63, 100% cobertura area y 80% horas
            profiles_clima['ConHeatHP']=profiles_base['Qheat']*self.area/2.63*0.8*self.n_heat_hp
        
                
        if self.n_acc_split>0:
            #split eficiencia=2, 30% cobertura area y 80% horas
            profiles_clima['ConCoolSplit']=profiles_base['Qcool']*self.area/2*0.3*0.8*self.n_acc_split

        if self.n_acc_hp>0:
            #bomba de calor=3.72, 100% cobertura area y 80% horas
            profiles_clima['ConCoolHP']=profiles_base['Qcool']*self.area/3.72*0.8*self.n_acc_hp
        
                
        profiles_clima['ConTotClima']=profiles_clima.sum(axis=1)
        # column_min = (profiles_clima_all.sum()).idxmin()
        # profiles_clima['ConMin']=profiles_clima_all[column_min]    
        
        # column_max = (profiles_clima.sum()).idxmax()
        # profiles_clima['ConMax']=profiles_clima_all[column_max]
        
        # profiles_clima['ConMean']=profiles_clima_all.mean(axis=1)
        
        return profiles_clima
 
        
    def cons_total(self):

      
        profiles_base=self.file_cons()
        profile_eq=self.cons_eq()
        profile_clima=self.cons_hvac()
        
        # multiplicar el consumo base por el número de viviendas
        profile_base_tot=profiles_base['ConBase']*self.num_v
        #sumar todo
        profile_all=pd.concat([profile_base_tot,profile_eq['ConTotEq'],profile_clima['ConTotClima']],axis=1)
        profile_sum=profile_all.sum(axis=1)
        profile_av=profile_sum/self.num_v
    
        #si el perfil promedio calculado y el informado tienen más de 5% de discrepancia
        if abs(1-(self.consum/profile_av.sum()))>0.05:
            #lo corregimos directamente
            f_corr=self.consum/profile_av.sum()
            profile_sum=self.num_v*(profile_av*f_corr)
            profile_av=profile_av*f_corr
        else:
            f_corr=0
        
   
        #determinar perfil total
        
        
        # if self.num_v==1:
        #     c_ref=[3400,3850,4000,4150,4450,4800] 
        
        # elif self.num_v>1:
        #     c_ref=[1700,2100,2280,2400,2700,3000]
        # cons_users=self.consum*self.num_v
        # year_cons=(profile_sum['Sum'].sum())*self.num_v
        
        # #lo compara con el valor informado por el usuario 
        # #si hay un error más alto del 5% hay que ajustar el perfil base
        # if abs(1-(cons_users/year_cons))>0.05:  
        #     new_cons_base=cons_users-(profile_sum['ConClima'].sum())-(profile_sum['ConEq'].sum())
        #     profile_sum['ConBasenew']=(profile_sum['ConBase']/profile_sum['ConBase'].sum())*new_cons_base
        # profile_sum['Sum']=profile_sum['ConBasenew','ConClima','ConEq'].sum(axis=1)

        # # year_cons=profile_sum['Sum'].sum()
        # # profile_sum['norm']= profile_sum['Sum']/year_cons
        # profile_total=pd.DataFrame()
        # profile_total['Total']=profile_sum['Sum']
            

        return profile_sum, profile_av,f_corr
    
    def cons_min(self,corr_av):
        
        profiles_base=self.file_cons()
        profile_min=pd.DataFrame(index=profiles_base.index)
        profile_min['Cons_total']=[0]*8760
        
        
        #para buscar el perfil minimo, si todas las viviendas tienen dhw cocina y horno, hay que sumar este consumo, si alguna no tiene, se queda en 0
        if self.n_dhw==self.num_v:
            profile_min['Cons_total'] += profiles_base['ConDHW']

        if self.n_stove==self.num_v:
            profile_min['Cons_total'] += profiles_base['ConStove']

        if self.n_oven==self.num_v:
            profile_min['Cons_total'] += profiles_base['ConOven']


        #si no hay ninguna vivienda sin calefaccion, hay que sumar calefaccion
        
        if self.n_heat_none==0 and self.n_heat_gas==0:
            #la calefaccion con consumo más bajo es bomba de calor
            if self.n_heat_hp>0:
                profile_min['Cons_total'] += profiles_base['Qheat']*self.area/2.63*0.8
            else:
                profile_min['Cons_total'] += profiles_base['Qheat']*self.area*0.3*0.8

        #si no hay ninguna vivienda sin aire acondicionado, hay que sumar el aire acondicionado
        if self.n_acc_none==0:
                            
            if self.n_acc_hp>0:
                #bomba de calor=3.72, 100% cobertura area y 80% horas
                profile_min['Cons_total'] += profiles_base['Qcool']*self.area/3.72*0.8
            
            else:
                #split eficiencia=2, 30% cobertura area y 80% horas
                profile_min['Cons_total'] += profiles_base['Qcool']*self.area/2*0.3*0.8
    
        #sumar el perfil base
        profile_min['Cons_total'] +=profiles_base['ConBase']
        
        #si se ha corregido el perfil antes, se tiene que corregir el minimo tambien
        if corr_av>0:
            profile_min['Cons_total']= profile_min['Cons_total']*corr_av
            
        
        return profile_min
    

    def cons_max(self,corr_av):
      
        profiles_base=self.file_cons()
        profile_max=pd.DataFrame(index=profiles_base.index)
        profile_max['Cons_total']=[0]*8760
        #para buscar el perfil maximo, si alguna vivienda tiene dhw cocina y horno, hay que sumar este consumo, si todas no tienen, se queda en 0
        if self.n_dhw>0:
            profile_max['Cons_total'] += profiles_base['ConDHW']
    
        if self.n_stove>0:
            profile_max['Cons_total'] += profiles_base['ConStove']
    
        if self.n_oven>0:
            profile_max['Cons_total'] += profiles_base['ConOven']
    
    
        #si hay alguna vivienda con calefaccion eletrica, hay que sumarla 
        
        if self.n_heat_rad>0 or self.n_heat_hp>0:
            #la calefaccion con consumo más alto es radiador
            if self.n_heat_rad>0:
                profile_max['Cons_total'] += profiles_base['Qheat']*self.area*0.3*0.8
            else:
                profile_max['Cons_total'] += profiles_base['Qheat']*self.area/2.63*0.8
                
        #si hay alguna vivienda con dicionado, hay que sumar el aire acondicionado
        if self.n_acc_hp>0 or self.n_acc_split>0:
            #la calefaccion con consumo más alto es el split
            if self.n_acc_split>0:
                #split eficiencia=2, 30% cobertura area y 80% horas
                profile_max['Cons_total'] += profiles_base['Qcool']*self.area/2*0.3*0.8
            
            else:
                #bomba de calor=3.72, 100% cobertura area y 80% horas
                profile_max['Cons_total'] += profiles_base['Qcool']*self.area/3.72*0.8
        
        #sumar el perfil base
        profile_max['Cons_total'] +=profiles_base['ConBase']
        
        #si se ha corregido el perfil antes, se tiene que corregir el minimo tambien
        if corr_av>0:
            profile_max['Cons_total']= profile_max['Cons_total']*corr_av
            
        
        return profile_max

# class get_data:
#     def __init__(self, typeFile: currencyType):
#         self.typeFile = typeFile

#     def start(self):
#         return self.typeFile.dataSource()