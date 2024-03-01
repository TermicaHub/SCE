# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 12:32:56 2023

@author: mcalcagnotto
"""

import pandas as pd
from abc import ABC, abstractmethod
import math
import matplotlib.pyplot as plt
import numpy_financial as npf
import numpy as np
from repositories import dataEcon_repository
from interactors import dataEconomic
import calendar


class balEcoYear:
    def __init__(self,df_balance,area_cub,parameters):
        self.balance=df_balance
        self.area=area_cub
        self.params=parameters

    
    #params=getInputs()
    
    
    
    def monthlyBalance(self,tariff):
                

        Net=pd.DataFrame(index=self.balance.index)
        Net['import']=self.balance['Net'][self.balance['Net']>0].fillna(0)
        Net['export']=self.balance['Net'][self.balance['Net']<0].fillna(0)
        
        
        cost_d=pd.DataFrame(index=self.balance.index)
        
        cost_d['import']=(Net['import']*tariff['grid']).fillna(0)
        cost_d['export']=(Net['export']*tariff['surplus']).fillna(0)
        cost_d['balance']=cost_d['import']+cost_d['export']
        
            
            
        #junta el cost daily para cada mes 

        balance_mensual=cost_d['balance'].groupby(cost_d.index.month).sum()
                                      
        #quita los valores negativos
        balance_mensual[balance_mensual < 0] = 0                                       
        balance_mensual=balance_mensual*(1+self.params['iee'])*(1+self.params['iva'])                                                                              
        #current_cost_y=balance_mensual.sum() 
        
        #return balance_mensual,current_cost_y
        return balance_mensual
    
    def monthlyBalanceBS(self,tariff):
                

        Net=pd.DataFrame(index=self.balance.index)
        Net['import']=self.balance['Net'][self.balance['Net']>0].fillna(0)
        Net['export']=self.balance['Net'][self.balance['Net']<0].fillna(0)
        
        # cost_d=pd.Series(index=self.balance.index)
        # for i in range(0,len(Net)):
        #     if Net[i]>0:
        #         cost_d[i]=Net[i]*tariff_g[i]
        #     else:
        #         cost_d[i]=Net[i]*tariff_s[i]
        
        cost_d=pd.DataFrame(index=self.balance.index)
        
        cost_d['import']=(Net['import']*tariff['grid']).fillna(0)
        cost_d['export']=(Net['export']*tariff['surplus']).fillna(0)
        cost_d['balance']=cost_d['import']+cost_d['export']
        
                        
        #junta el cost daily para cada mes 

        balance_mensual=cost_d['balance'].groupby(cost_d.index.month).sum()

        
        #con bono social, solo es necesario si los balances son positivos,si no se quedan en 0
        #calculo de días del año, solo es necesario una vez
        if calendar.isleap(cost_d.index[0].year):
            days_y=366
        else:
            days_y=365
        dif=pd.Series()
        dif[0]=0

        #calculate Net sum
        Net_m=self.balance['Net'].groupby(self.balance.index.month).sum()
        for i in range(1,len(balance_mensual)+1):
            if balance_mensual[i]>0:

                #calculate monthly limit
                
                _, num_days = calendar.monthrange(cost_d.index[0].year, i)
                #aquí se calcula el límite proporcional al número de días más lo que ha sobrado del mes anterior 
                
                limit_m=((self.params['limite_y']/days_y)*num_days)+dif[i-1]
                #si el valor Net del mes no ultrapasa el límite, se calcula el precio con descuento
                if Net_m[i]<=limit_m:
                    balance_mensual[i]=balance_mensual[i]*(1-self.params['bono_social'])
                    dif[i]=limit_m-Net_m[i]
                    #balance_mensual[i]=balance_mensual[i]*(limit_m/Net_m[i])*(1-self.params['bono_social'])
              
                else:
                    print ('Límite excedido en el mes: '+ str(i))
                    dif[i]=0
                    cost_discount=balance_mensual[i]*(limit_m/Net_m[i])
                    cost_nodiscount=balance_mensual[i]-cost_discount
                    balance_mensual[i]=(cost_discount*(1-self.params['bono_social']))+cost_nodiscount
            else:
                dif[i]=0
    
        #quita los valores negativos
        balance_mensual[balance_mensual < 0] = 0                                       
        balance_mensual=balance_mensual*(1+self.params['iee'])*(1+self.params['iva'])                                                       
        #current_cost_y=balance_mensual.sum() 
        
        return balance_mensual

    
     
    def annualSavings(self,tariff):
        balance_mensual=self.monthlyBalance(tariff)
        #savings monthly and annual
        #lo que te habrías gastado en electricidad a cada mes -lo que realmente has gastado, es >0
        previous_cost=self.balance['Med']*tariff['grid']
        previous_cost_m=previous_cost.groupby(previous_cost.index.month).sum()
        #QUITAR ESTO
        previous_cost_m=previous_cost_m*(1+self.params['iee'])*(1+self.params['iva'])
        savings_m=previous_cost_m-balance_mensual
        #savings_m=savings_m+(savings_m*(1+self.params['iee'])*(1+self.params['iva']))
        annual_savings=savings_m.sum()
         
        
        #return previous_cost_m,annual_savings
        return annual_savings
    
    def annualSavingsBS(self,tariff):
        balance_mensual=self.monthlyBalanceBS(tariff)
        #savings monthly and annual
        #lo que te habrías gastado en electricidad a cada mes -lo que realmente has gastado, es >0
        previous_cost=self.balance['Med']*tariff['grid']
        previous_cost_m=previous_cost.groupby(previous_cost.index.month).sum()
               
        
        #calculating the cost before self-consumption, again considering limits 
        Consumption_m=self.balance['Med'].groupby(self.balance.index.month).sum()
        #calculate monthly limit
        #días del año
        if calendar.isleap(self.balance.index[0].year):
            days_y=366
        else:
            days_y=365
        dif=pd.Series()
        #para el mes 1, no se considera ningún sobrante del mes anterior
        dif[0]=0
        #loop de mes en mes, calcula el límite, compara con el consumo mensual y calcula el precio
        for i in range(1,len(previous_cost_m)+1):
            _, num_days = calendar.monthrange(self.balance.index[0].year, i)
            # limit_m=0
            limit_m=((self.params['limite_y']/days_y)*num_days)+dif[i-1]
            #si el valor del mes no ultrapasa el límite, se calcula el precio con descuento
            if Consumption_m[i]<=limit_m:
                previous_cost_m[i]=previous_cost_m[i]*(1-self.params['bono_social'])
                #calcula el sobrante que se acumula para el siguiente mes
                dif[i]=limit_m-Consumption_m[i]
                #previous_cost_m[i]=previous_cost_m[i]*(limit_m/Consumption_m[i])*(1-self.params['bono_social'])
          
            else:
                cost_discount=previous_cost_m[i]*(limit_m/Consumption_m[i])
                cost_nodiscount=previous_cost_m[i]-cost_discount
                previous_cost_m[i]=(cost_discount*(1-self.params['bono_social']))+cost_nodiscount
                dif[i]=0
        
        previous_cost_m=previous_cost_m*(1+self.params['iee'])*(1+self.params['iva'])
                                      
         
        savings_m=previous_cost_m-balance_mensual
        #savings_m=savings_m+(savings_m*(1+self.params['iee'])*(1+self.params['iva']))
        annual_savings=savings_m.sum()
        previous_cost_y=previous_cost_m.sum() 
        
        #return previous_cost_m,savings_m,annual_savings
        return previous_cost_y,annual_savings
    
    def savingsLife(self,tariff):
   
        savings_y_life=[]
        savings_y_life.append(0)
        for i in range(0,self.params['pv_life']):
            # tariff_g=tariff['grid']*(1+parameters_eco['inc_tariff_grid'])
            # tariff_s=tariff['surplus']*(1+parameters_eco['inc_tariff_surplus'])
            tariff_y=tariff*((1+self.params['tariff_var_y'])**i)
            
            savings_y=self.annualSavings(tariff_y)
            savings_y_life.append(savings_y)
            
        return savings_y_life
            
    def savingsLifeBS(self,tariff):
   
        savings_y_life=[]
        savings_y_life[0]=0
        for i in range(0,self.params['pv_life']):
            # tariff_g=tariff['grid']*(1+parameters_eco['inc_tariff_grid'])
            # tariff_s=tariff['surplus']*(1+parameters_eco['inc_tariff_surplus'])
            tariff_y=tariff*(1+self.params['tariff_var_y'])**i
            
            previous_cost,savings_y=self.annualSavingsBS(tariff_y)
            savings_y_life.append(savings_y)
            
        return savings_y_life
                   
    
    def simplePayback(self,annual_savings,cost):

        total_cost=cost*self.area
        total_cost=total_cost-self.params['pv_grants']
 
        # #simple payback
        #aqui no se tiene en cuenta el descuento del IBI
        #aqui no se tiene en cuenta costes de mantenimiento
        if annual_savings>0:
            payback_s=total_cost/annual_savings
            payback_s_round=math.ceil(payback_s)
        else:
            print('No savings!')
        return payback_s_round,total_cost
    
    def dataCost(self,area_cubiertas):
        
        TypeFile_Cost = dataEcon_repository.defaultCosts()
        get_data = dataEcon_repository.dataEcon(TypeFile_Cost)
        data_params = get_data.start()
        
        
        cost_inicial=[]
        cost_anual=[]
        
        for value in area_cubiertas:
            if value<data_params.index[0]:
                coste_inv=data_params['Cost_inv'][data_params.index[0]]*value
                coste_mant=data_params['Cost_mant'][data_params.index[0]]*value
    
            elif value<data_params.index[1]:
                coste_inv=data_params['Cost_inv'][data_params.index[1]]*value
                coste_mant=data_params['Cost_mant'][data_params.index[1]]*value
                
            elif value<data_params.index[2]:
                coste_inv=data_params['Cost_inv'][data_params.index[2]]*value
                coste_mant=data_params['Cost_mant'][data_params.index[2]]*value
                
            elif value<data_params.index[3]:
                coste_inv=data_params['Cost_inv'][data_params.index[3]]*value
                coste_mant=data_params['Cost_mant'][data_params.index[3]]*value
                
            elif value<data_params.index[4]:
                coste_inv=data_params['Cost_inv'][data_params.index[4]]*value
                coste_mant=data_params['Cost_mant'][data_params.index[4]]*value
                
    
            cost_inicial.append(coste_inv)
            cost_anual.append(coste_mant)
        
        cost_ref_inv=sum(cost_inicial)
        cost_mant_y=sum(cost_anual) 
        
        return cost_ref_inv,cost_mant_y
    

    def calcNPV(self,total_cost,tariff,cost_mant):

        annual_savings_life=self.savingsLife(tariff)
        NPV=[]
        cash_flow_ac=[]
        NPV.append((-1)*total_cost)
        cash_flow_ac.append(0)
        #aquí se añade el coste de mantenimiento anual
        
                
        #el descuento del IBI entra como un componente más de los ahorros
        #determina si hay o no descuento del IBI, podría ser también que si no hay el valor sea 0 y lo chequea antes 
        if self.params['discount_ibi']>0:
        #el valor y el tiempo del descuento tienen que ser inputs, he usado 528 que es el promedio del IBI para BCN y 50% durante 3 años también para BCN
            discount_ibi_value=self.params['ibi_value']*self.params['discount_ibi']
        
        #para cada año de la vida util después del primero
        
        for i in range(1,self.params['pv_life']+1):
            if self.params['discount_ibi']>0 and i <self.params['discount_ibi_y']:
                cash_flow=(annual_savings_life[i]+discount_ibi_value-cost_mant)
            else:
                cash_flow=(annual_savings_life[i]-cost_mant+self.params['cuota_y'])
            cash_flow_ac.append(cash_flow)
            NPV.append(NPV[i-1]+(cash_flow_ac[i]/((1+self.params['discount_rate'])**i)))

            
            if NPV[i]>0 and NPV[i-1]<0:
                n_months=(-1*NPV[i-1])/((NPV[i]-NPV[i-1])/12)
                payback_c=round((i-1)+(n_months/12),2)
            if NPV[len(NPV)-1]<0:
                payback_c=None
      

        #irr=npf.irr(cash_flow_ac)
                
        return NPV,payback_c


    def calcNPVBS(self,total_cost,tariff):
        annual_savings_life=self.savingsLifeBS(tariff)
        NPV=[]
        cash_flow_ac=[]
        NPV.append((-1)*total_cost)
        cash_flow_ac.append((-1)*total_cost)
        #aquí se añade el coste de mantenimiento anual
        cost_mant=self.params["cost_mant_y"]*self.area
                
        #el descuento del IBI entra como un componente más de los ahorros
        #determina si hay o no descuento del IBI, podría ser también que si no hay el valor sea 0 y lo chequea antes 
        if self.params['discount_ibi']>0:
        #el valor y el tiempo del descuento tienen que ser inputs, he usado 528 que es el promedio del IBI para BCN y 50% durante 3 años también para BCN
            discount_ibi_value=self.params['ibi_value']*self.params['discount_ibi']
        
        #para cada año de la vida util después del primero
        
        for i in range(0,self.params['pv_life']):
            if self.params['discount_ibi']>0 and i <self.params['discount_ibi_y']:
                cash_flow=(annual_savings_life[i]+discount_ibi_value-cost_mant)
            else:
                cash_flow=(annual_savings_life[i]-cost_mant)
            cash_flow_ac.append(cash_flow)
            NPV.append(NPV[i-1]+((cash_flow/(1+self.params['discount_rate'])**i)))

            
            if NPV[i]>0 and NPV[i-1]<0:
                n_months=(-1*NPV[i-1])/((NPV[i]-NPV[i-1])/12)
                payback_c=round((i-1)+(n_months/12),2)
            if NPV[len(NPV)]<0:
                payback_c=None
      

        #irr=npf.irr(cash_flow_ac)
                
        return NPV,payback_c    
    
    def graphNPV(self,NPV,payback_c):
        plt.figure(figsize=(20, 12))
        plt.plot(range(self.params['pv_life']),NPV,linestyle='-', color='g',label='savings')
        plt.plot(range(self.params['pv_life']),[0]*self.params['pv_life'],linestyle='-', color='r',label='cost')
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        #finding the maximum value of y to position the text
        y_limits = plt.ylim()
        max_y_value = y_limits[1]
        
        #transforming payback time in year + month
        pb_m,pb_y=math.modf(payback_c)
        pb_y=int(pb_y)
        pb_m=math.ceil(pb_m*12)
        #graph labels and title
        plt.ylabel('€',fontsize=16)
        plt.xlabel('anys',fontsize=16)
        title='Valor actual net (VAN)'
        plt.title(title,fontsize=20)
        #adding payback text
        plt.text(16,(max_y_value-200),f"Retorn inversió:{pb_y} anys y {pb_m} mesos",fontsize=20)
        plt.savefig("sample_plot.png", dpi=300, bbox_inches='tight')
        
    
    def calcLCOE(self,total_cost):
        #here we are considering the same yearly generation throughout the lifetime
        #the only cost considered is the initial investment, here we could add operation and maintainance costs as well 
        #we are not taking into account replacement of inverters during the life span
        LCOE=total_cost/(self.params['pv_life']*self.pvgen)
        
        return LCOE
    
    
        
        

# #accumulated balance and graph

# lifetime=25
# inc_tariff_grid=0.02
# inc_tariff_surplus=0.01
# discount_rate=0.03

# #calcular los ahorros acumulados
# annual_savings_ac=[]
# annual_savings_ac.append(annual_savings)
# NPV=[]
# NPV.append((-1)*total_cost)
# #aquí se puede añadir algun coste de mantenimiento, si hubiese 
# total_cost_ac=[total_cost]*lifetime

# #el descuento del IBI entra como un componente más de los ahorros
# #determina si hay o no descuento del IBI, podría ser también que si no hay el valor sea 0 y lo chequea antes 
# discount_ibi=False
# #el valor y el tiempo del descuento tienen que ser inputs, he usado 528 que es el promedio del IBI para BCN y 50% durante 3 años también para BCN
# ibi_value=528
# discount_ibi=0.5
# discount_ibi_value=ibi_value*discount_ibi
# discount_ibi_years=3

# #para cada año de la vida util después del primero
# for i in range(1,lifetime):
#     #calcula el balance mensual considerando el incremento de la tarifa y del surplus
#     balance_mensual_new=(mensual_dt*((1+inc_tariff_grid)**i))-(mensual_et*((1+inc_tariff_surplus)**i))
#     #evalúa si algún balance mensual es negativo y si lo es, lo pone igual a 0
#     for j in range(1,len(balance_mensual_new)+1):
#         if balance_mensual_new[j]<0:
#             balance_mensual_new[j]=0
    
#     savings=((d_energybalance['Med_cp']*tariff_grid*(1+inc_tariff_grid)).groupby(d_energybalance.index.month).sum())-balance_mensual_new
#     if discount_ibi==True and i<=discount_ibi_years:
#         annual_savings=(savings.sum()+discount_ibi_value)/((1+discount_rate)**i)
#     annual_savings=savings.sum()/((1+discount_rate)**i)
#     NPV.append(NPV[i-1]+annual_savings)
#     annual_savings_ac.append(annual_savings_ac[i-1]+annual_savings)
#     if NPV[i]>0 and NPV[i-1]<0:
#         n_months=(-1*NPV[i-1])/((NPV[i]-NPV[i-1])/12)
#         payback_c=round((i-1)+(n_months/12),2)
#     else:
#         payback_c=None
        
    
# plt.figure(figsize=(20, 12))
# plt.plot(range(lifetime),annual_savings_ac,linestyle='-', color='b',label='savings')
# plt.plot(range(lifetime),total_cost_ac,linestyle='-', color='r',label='cost')
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)

# plt.ylabel('€',fontsize=16)
# plt.xlabel('anys',fontsize=16)
# title='Balanç economic'
# plt.title(title,fontsize=20)
# plt.text(18,10000,f"Payback simple:{payback_s_round} anys",fontsize=20)


# plt.figure(figsize=(20, 12))
# plt.plot(range(lifetime),NPV,linestyle='-', color='g',label='savings')
# plt.plot(range(lifetime),[0]*lifetime,linestyle='-', color='r',label='cost')
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)

# plt.ylabel('€',fontsize=16)
# plt.xlabel('anys',fontsize=16)
# title='Net Present Value'
# plt.title(title,fontsize=20)
# plt.text(18,10000,f"Retorn inversió:{payback_c} anys",fontsize=20)
 
    


          
        


