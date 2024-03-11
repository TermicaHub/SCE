# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 09:41:54 2024

@author: mcalcagnotto
"""

# Import libraries and packages

import pandas as pd
import os          
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import sys


# Path

direct  = os.getcwd()
sys.path[0] = direct

# Interactors

from interactors import dataFV,dataWeather, resourceConsumption, dataEconomic, baseConsumption


# Calculations

from utils import radiationFV, energyBalance_FV, compSimplificada, tariffCalc,co2Balance, repartoSomCom




  
#%% Get data for PV calculation <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# >>> Angles 
#the data is read from the json file, for the 3 roofs of the main building and the CEL roofs aggregated
#user_mode=0 es usuario basico (perfil indiv) user_mode=1 es usuario avanzado (demás perfiles)
#esto es necesario ahora porque tengo los dos archivos con distintos nombres pero realmente no será necesario después, puede haver un unico metodo si el json siempre tiene el mismo nombre
# user_mode=0
# cubierta=dataFV.somCInputs(user_mode)
# getPVdata = dataFV.insert(cubierta)
# #df_PV can be calculated only once, considering the inputs are Lst,Lloc,phi which are the same for all buildings/roofs
# parameters, df_PV= getPVdata.start()


cubierta=dataFV.somCInputs()
getPVdata = dataFV.insert(cubierta)
#df_PV can be calculated only once, considering the inputs are Lst,Lloc,phi which are the same for all buildings/roofs
parameters, df_PV= getPVdata.start()



# >>> Weather
#the weather code comes from the json 

weather = dataWeather.outputTRNSYS(clima = parameters['clim'])
getWeatherdata = dataWeather.select(weather)

df_clima = getWeatherdata.start()

#>>>Economic parameters:
#economic inputs
econ_data = dataEconomic.somCInputs()
getEcondata = dataEconomic.insert(econ_data)
parameters_eco = getEcondata.start()


#OJO: NOS TIENE QUE DAR EL AREA TOTAL PARA CUBIERTA PLANA, SI NO HAY QUE HACER X2

area_ep=parameters['pva_n1']+parameters['pva_n2']+parameters['pva_n3']
area_list=[area_ep]

for element in parameters['pva_cel']:
    if element>0:
        area_list.append(element)
        
area_cel=sum(parameters['pva_cel'])

area_t=area_ep+area_cel

   
#>>> Calculo CEL, considerando inputs del usuario
#1 edificio base y demás edificios agregados 
   
selected_dict = {key: parameters[key] for key in ['pva_n1', 'pva_n2','pva_n3','pva_cel']}
cubiertas = [var for var, value in selected_dict.items() if value != 0]


# Calculate radiation <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

b_output = radiationFV.dataframe()

PV_dict = {}
PV_dict_cel = {}
df_PV_base = pd.DataFrame({'Pv_base': [0] * 8760}, index = df_clima.index)
df_PV_total = pd.DataFrame({'Pv_base': [0] * 8760}, index = df_clima.index)


for i in range(0,len(cubiertas)):
    #cubierta = dataFV.manualInputs(-15, 41.382, -2.175, gamma[i], beta[i], area[i])
    #cubierta = dataFV.manualInputs(-15, 41.117, -1.250, gamma[i], beta[i], area[i])
    # #cubierta = dataFV.somCInputs()
    #getPVdata = dataFV.insert(cubierta)
    #parameters, df_PV= getPVdata.start()
    
    cubierta_id=cubiertas[i].split('_')[1]
    # gamma={'gamma_'+cubierta_id:parameters['gamma_'+cubierta_id]}
    # beta={'beta_'+cubierta_id:parameters['beta_'+cubierta_id]}
    # area={'pva_'+cubierta_id:parameters['pva_'+cubierta_id]}
    # theta={'theta_'+cubierta_id:parameters['theta_'+cubierta_id]}
    
    #si es CEL, consideramos cubierta plana a doble orientación
    if cubiertas[i]=='pva_cel':
        parameters_cubierta={'gamma':parameters['gamma_'+cubierta_id],'beta':parameters['beta_'+cubierta_id],'area':sum(parameters['pva_'+cubierta_id])/2,'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
        b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
        df_PV_new = b.start()
        PV_dict_cel.setdefault(cubiertas[i],df_PV_new)
        parameters_cubierta={'gamma':-1*(parameters['gamma_'+cubierta_id]),'beta':parameters['beta_'+cubierta_id],'area':sum(parameters['pva_'+cubierta_id])/2,'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
        b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
        df_PV_new = b.start()
        PV_dict.setdefault(cubiertas[i]+'_opuesto',df_PV_new)
    #si la cubierta es del edificio base, chequeamos si es plana o inclinada
    else:
        #para cubierta plana 
        if parameters['type_roof_'+cubierta_id]=="roof_flat":
            parameters_cubierta={'gamma':parameters['gamma_'+cubierta_id],'beta':parameters['beta_'+cubierta_id],'area':parameters['pva_'+cubierta_id]/2,'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
            b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
            df_PV_new = b.start()
            
            PV_dict.setdefault(cubiertas[i],df_PV_new)
            parameters_cubierta={'gamma':-1*(parameters['gamma_'+cubierta_id]),'beta':parameters['beta_'+cubierta_id],'area':parameters['pva_'+cubierta_id]/2,'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
            b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
            df_PV_new = b.start()
            PV_dict.setdefault(cubiertas[i]+'_opuesto',df_PV_new)
   
       
        #para cubierta inclinada
        elif parameters['type_roof_'+cubierta_id]=="roof_tilt":
            parameters_cubierta={'gamma':parameters['gamma_'+cubierta_id],'beta':parameters['beta_'+cubierta_id],'area':parameters['pva_'+cubierta_id],'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
            
            b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
            #b = radiationFV.calculo(b_output, df_clima, df_PV, parameters , 'Pv_base')
            df_PV_new = b.start()
            PV_dict.setdefault(cubiertas[i],df_PV_new)
            
#ahora se agrega toda la producción
#todas las cubiertas del ed. base
for key in PV_dict:
    df_PV_base['Pv_base'] = df_PV_base['Pv_base'] + PV_dict[key]['Pv_base']
df_PV_total['Pv_base']=df_PV_base['Pv_base']
#sumar la producción CEL
for key in PV_dict_cel:
    df_PV_total['Pv_base']= df_PV_total['Pv_base'] + PV_dict_cel[key]['Pv_base']
    
#adding additional losses to reduce production of main building PV_total           
df_PV_total['Pv_base'] = df_PV_total['Pv_base'] * (1-parameters_eco['pvsys_loss'])  

# PV_gen_cp_y=df_PV_total['Pv_base'].sum()
# PV_gen_cel_y=df_PV_cel['Pv_cel'].sum()
PV_gen_y=df_PV_total['Pv_base'].sum()
  
# cubiertas_analizar = ['Cubierta_1','Cubierta_2','Cubierta_3','Cubierta_4','Polideportivo','Pérgola','Viviendas']
#no entiendo muy bien el motivo de esto, es por si no quieres incluir alguna de las cubiertas productoras al 
#de momento voy a poner que es igual a las cubiertas


#cubiertas_analizar = cubiertas


# for i in cubiertas_analizar:
#     if i =='pva_cel':
#         df_PV_cel['Pv_cel'] = df_PV_cel['Pv_cel'] + PV_dict_cel[i]['Pv_base']
#         #adding additional losses to reduce production of CEL PV_cel
#         df_PV_cel['Pv_cel'] = df_PV_cel['Pv_cel'] * (1-parameters_eco['pvsys_loss'])

#     else:    
#         #INCREMENTA LA PRODUCCION PV_total añadiendo todas las cubiertas que vamos a analizar
#         df_PV_total['Pv_base'] = df_PV_total['Pv_base'] + PV_dict[i]['Pv_base']
        

#adding additional losses to reduce production of main building PV_total           
# df_PV_total['Pv_base'] = df_PV_total['Pv_base'] * (1-parameters_eco['pvsys_loss'])  
# print(df_PV_total['Pv_base'].sum())
# #produccion total
# df_PV_cp_cel=pd.DataFrame({'Pv_base':df_PV_total['Pv_base']+df_PV_cel['Pv_cel']})


#df_PV.to_excel('resultPV_components.xlsx')
#df_PV_total.to_excel('resultPV_production.xlsx')




#%% Consumption of each user
# #%%Consumption of dwellings in postcode 07006 "Residencial_3years.csv" in Resoures folder + energy price (example)  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
 
# c_output = resourceConsumption.dataDIS()
# cons = resourceConsumption.get_data(c_output)
# d_multiyearDdis = cons.start()


# #%% Get data and filter the empty values (example) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# c_output = resourceConsumption.dataComercializadora()
# cons = resourceConsumption.get_data(c_output)
# d_yearReal = cons.start()


    

#%%Definir el perfil de demanda del usuario principal

data_cons = baseConsumption.ConsSimple(parameters['numV'])
df_cons=data_cons.cons_total()

# data Som Comunitat, perfiles tipo definidos en el archivo \\resources\\data\\ConsProfiles.csv

# c_output = resourceConsumption.SomCom()
# cons = resourceConsumption.get_data(c_output)
# dataSom = cons.start()

## crear un dataframe para todos los consumos
n_users_ep=parameters['n_part_ep']
n_users_cel=parameters['p_part_cel']*parameters['numV_cel']
n_users= n_users_ep+n_users_cel
name_columns=[None]*n_users 
name_columns[0]='Cbase'

for i in range(1,n_users):
    name_columns[i]='C'+ str(i)

cons_total=pd.DataFrame(index=df_cons.index,columns=name_columns)
cons_total['Cbase']=df_cons['Cons_total']/n_users_ep
    
#consumo del usuario base (vivienda)
# if parameters['consum_base']<=1500:
#     cons_total['Cbase']=dataSom['C1500']
# elif 1500<parameters['consum_base']<=2000:
#     cons_total['Cbase']=dataSom['C2025']
# elif 2000<parameters['consum_base']<=2500:
#     cons_total['Cbase']=dataSom['C2500']  
# elif parameters['consum_base']>2500:
#     cons_total['Cbase']=dataSom['C3000']  
    
#consumo de los demás usuarios (ed. base y ed. CEL)
# if parameters['type_consum']=="cons_same":
    #mismo perfil edificio base
    
for i in cons_total.columns[1:]:
#this will be based on user input
#this will have to be a loop with the profile we decide for users of the CEL
    cons_total[i]=cons_total['Cbase']

# if parameters['type_consum']=="cons_mean":
#     #perfil promedio "Med"
#     for i in cons_total.columns[1:]:
#     #this will be based on user input
#     #this will have to be a loop with the profile we decide for users of the CEL
#         cons_total[i]=dataSom['Med']


#%% Calculating distribution coefficients
#type_coef=1 igual para todos 
#if parameters['type_coef']==1:
coef_input=repartoSomCom.CoefUnicoViv(name_columns)
coefabc=repartoSomCom.calculo(coef_input)
coef=coefabc.start()
    
#type_coef=2 determinado para la vivienda principal  
#si el coef informado es para la vivienda
# if parameters['type_coef']==2:
#     input=repartoSomCom.CoefDifViv(name_columns,parameters['coef_base'])
#     coefabc=coefCalc.calculo(input)
#     coef=coefabc.start()

# #si el coef informado es para el edificio
# if parameters['type_coef']==2:
#     input=repartoSomCom.CoefDifEdif(name_columns,parameters['coef_base'],parameters['numV'])
#     coefabc=coefCalc.calculo(input)
#     coef=coefabc.start()



# #same coefficient for all
# if parameters['type_coef']==1:
#     input=coefCalc.CoefUnico(name_columns)
#     coefabc=coefCalc.calculo(input)
#     coef=coefabc.start()

# #main user has one coefficient, and the rest is split among the others
# elif parameters['type_coef']==2:

#     input=coefCalc.CoefUnico_cp(cons_total,n_users,parameters['coef_base'])
#     coefabc=coefCalc.calculo(input)
#     coef=coefabc.start()


#division based on power contracted
# one value per user (maybe it could be 8760 values, check how this will work)
# P=1
# Pcont=(pd.DataFrame([P,2*P,3*P,P,P])).T
# Pcont.columns=name_columns
    
# #calling the function coefCalc to calculate the coefficients based on contracted power

# input=coefCalc.CoefPow(cons_total,Pcont)
# coefabc=coefCalc.calculo(input)
# coef=coefabc.start()

#variable coefficient based on consumption

# input=coefCalc.CoefVar(cons_total)
# coefabc=coefCalc.calculo(input)
# coef=coefabc.start()

#combinamos coef Cbase y Ccel

# coef_f=pd.Series()
# #coef_f['Cbase] es para la vivienda principal 
# coef_f['Cbase']=coef['Cbase']
# #acumulamos las demás viviendas aquí, sean del ed. principal o de los demás
# coef_f['Ccel']=coef[coef.columns[1:]].sum(axis=1)

#estos dataframes se hacen para usarlos en el balance combinado 
#Cbase es la vivienda principal y CEL son todas las demás agregadas
# df_consumption=pd.DataFrame()
# df_consumption['Cbase']=cons_total['Cbase']
# df_consumption['CEL']=cons_total[cons_total.columns[1:]].sum(axis=1)
# df_consumption['Total']=df_consumption['Cbase']+df_consumption['CEL']


#%% Energy balance

#balance propio DEL EDIFICIO para ed. unifamiliar

#si es unifamiliar, el consumo es Cbase, y la producción es solamente la del edificio base
# if parameters['numV']==1:
#     ebal_out = energyBalance_FV.balancePropioSomCom(cons_total,df_PV_base )
#     energy_balance = energyBalance_FV.calculo(ebal_out)
#     d_energybalance, LoCov = energy_balance.start()
    
#balance propio DEL EDIFICIO para ed. multifamiliar   
#si es multifamiliar,Cbase tiene que ser la suma de todas las viviendas, y se considera toda la producción PV del edificio
# if parameters['numV']>1:
#     cons_total['Cbase']=cons_total[cons_total.columns[0:(parameters['numV']-1)]].sum(axis=1)
    
#     ebal_out = energyBalance_FV.balancePropioSomCom(cons_total, df_PV_total)
#     energy_balance = energyBalance_FV.calculo(ebal_out)
#     d_energybalance, LoCov = energy_balance.start()


#balance combinado con coeficientes de reparto considerando coeficientes iguales para todas las viviendas o un coef para la vivienda base y la diferencia repartida igualmente entre todos
#aqui se considera la produccion PV total y el coeficiente correspondiente para cada usuario 
#los resultados son: Cbase - vivienda principal, CEL - demás viviendas,total - agregado
# ebal_out = energyBalance_FV.balanceCombinadoSomCom(df_consumption,df_PV_total,coef_f)
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalanceComb, LoCov_comb = energy_balance.start()

#balance combinado con un coeficiente de reparto para cada usuario 

ebal_out = energyBalance_FV.balanceCombinadoCoefSomCom(cons_total,df_PV_total,coef)
energy_balance = energyBalance_FV.calculo(ebal_out)
d_energybalanceComb,LoCov_indiv,LoCov_comb = energy_balance.start()

#energia total anual que recibe la vivienda
total_PV_viv=d_energybalanceComb['Cbase']['Pv_base'].sum()

# Energy Balance n building with production (example) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  
# here the PV production considered is from all buildings in cubiertas_analizar
#ebal_out = energyBalance_FV.balancePropio(dataframe_consumption = d_yearReal['CamiloJC_CEIP']['2021'], number_of_buildings = 1, dataframe_PV = df_PV_total.loc[:,['Pv_base']])

# ebal_out = energyBalance_FV.balancePropio(consum_ep,number_of_buildings = 1, dataframe_PV = df_PV_total.loc[:,['Pv_base']])
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalance, LoCov = energy_balance.start()
# # d_energybalance.to_excel('result_balance.xlsx')

# plots

# average_hour=pd.DataFrame()
# average_hour['Consumption']=d_energybalance['Med_cp'].groupby(d_energybalance.index.hour).mean()
# average_hour['Pv_base']=d_energybalance['Pv_base'].groupby(d_energybalance.index.hour).mean()
# average_hour['Net']=d_energybalance['Net'].groupby(d_energybalance.index.hour).mean()

# plt.plot(average_hour.index+1,average_hour['Consumption'],label='consumo')
# plt.plot(average_hour.index+1,average_hour['Pv_base'],label='PV')
# plt.plot(average_hour.index+1,average_hour['Net'],label='Net')
# plt.legend()
# plt.title('consumo anual:'+str(round(d_energybalance['Med_cp'].sum())))
# plt.show()


# average_components=pd.DataFrame()
# average_components['Sc']=d_energybalance['Sc'].groupby(d_energybalance.index.hour).mean()
# average_components['Dt']=d_energybalance['Dt'].groupby(d_energybalance.index.hour).mean()
# average_components['Et']=d_energybalance['Et'].groupby(d_energybalance.index.hour).mean()

# plt.plot(average_hour.index+1,average_components['Sc'],label='autconsumo')
# plt.plot(average_hour.index+1,average_components['Dt'],label='importación red')
# plt.plot(average_hour.index+1,average_components['Et'],label='exportación red')
# plt.legend()
# plt.title('consumo anual:'+str(round(d_energybalance['Med_cp'].sum())))
# plt.show()


# ebal_out = energyBalance_FV.balancePropio(c_school, number_of_buildings = 1, dataframe_PV = df_PV_total.loc[:,['Pv_base']])
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalance, LoCov = energy_balance.start()


# ebal_out = energyBalance_FV.balanceCombinado(c_school,1,df_PV_total.loc[:,['Pv_base']],c_CEL,1,df_PV_cel.loc[:,['Pv_cel']])
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalanceComb, LoCov_comb = energy_balance.start()

# d_energybalanceComb.to_excel('result_balancecom.xlsx')


#%%Economic balance
#>>>Economic parameters:
#economic inputs
econ_data = dataEconomic.somCInputs()
getEcondata = dataEconomic.insert(econ_data)
parameters_eco = getEcondata.start()

# #economic reference costs
# cost_data=dataEconomic.refCost(area_list)
# getCostdata = dataEconomic.insert(cost_data)
# ref_cost_inicial, coste_mant = getCostdata.start()

#>>> seleccion tipo de tarifa

# if parameters_eco['tariff_type']=="tariff_flat":
#     myTariff=tariffCalc.tariffSingle(cons_total.index,parameters_eco['tariff_single'],parameters_eco['tariff_surplus'])
#     tariff_out=tariffCalc.calculo(myTariff)
#     tariff_y=tariff_out.start()
    
# elif parameters_eco['tariff_type']=="tariff_hourly":
myTariff=tariffCalc.tariffHourly(cons_total.index,parameters_eco['tariff_peak'],parameters_eco['tariff_flat'],parameters_eco['tariff_valley'],parameters_eco['tariff_surplus'])
tariff_out=tariffCalc.calculo(myTariff)
tariff_y=tariff_out.start()
    
# elif parameters_eco['tariff_type']=="tariff_pvpc":
    # myTariff=tariffCalc.tariffPVPC(cons_total.index)
    # tariff_out=tariffCalc.calculo(myTariff)
    # tariff_y=tariff_out.start()
    
tariff_new={}
for i in range(0,parameters_eco['pv_life']):
    tariff_new[i]=tariff_y*((1+parameters_eco['tariff_var_y'])**i)
    
    

#balance economico: para la vivienda principal Cbase y para toda la comunidad agregada

#>>> Balance económico del calculo por defecto a nivel vivienda (autoconsumo individual)
# d_energybalance_defecto=d_energybalance_defecto.loc[:,'Med_cp':'Net_cp']
# part_to_drop = '_cp'
# d_energybalance_defecto.columns = d_energybalance_defecto.columns.str.replace(part_to_drop, '')
# data_comp=compSimplificada.balEcoYear(d_energybalance_defecto,area_base,parameters_eco,PV_gen_y_defecto)

# savings_y_base=data_comp.annualSavings(tariff_y)
# pback_base,coste_base=data_comp.simplePayback(savings_y_base,parameters_eco['cost_inv_base'])
# NPV_value_base,payback_c_base=data_comp.calcNPV(coste_base,tariff_y)

# balance_sum_y_defecto=pd.Series()
# for i in d_energybalance_defecto.columns:
#     balance_sum_y_defecto[i]=d_energybalance_defecto[i].sum()

# env_balance=co2Balance.balCO2Year(balance_sum_y_defecto)
# #prim_savings_base=env_balance.prim_savings()
# co2_base=env_balance.CO2_savings()
# co2_base_life=co2_base*parameters_eco['pv_life']

#BALANCE ECONÓMICO CEL AGREGADA

data_comp=compSimplificada.balEcoYear(d_energybalanceComb['Total'],area_t,parameters_eco)

#para cada cubierta, asigna un coste y un area

balance=data_comp.monthlyBalance(tariff_y)
savings_y=data_comp.annualSavings(tariff_y)
#cost_ag=parameters_eco['cost_inv_total']/area_t
#pback,coste=data_comp.simplePayback(savings_y,cost_ag)
#coste=parameters['cost_inv_total']
coste,coste_mant=data_comp.dataCost(area_list)
NPV_value,payback_c=data_comp.calcNPV(coste,tariff_y,coste_mant)


# NPV_life=NPV_value[len(NPV_value)-1]
# data_comp.graphNPV(NPV_value,payback_c)
# LCOE=data_comp.calcLCOE(coste)

balance_sum_y=pd.Series()
for i in d_energybalanceComb['Total'].columns:
    balance_sum_y[i]=d_energybalanceComb['Total'][i].sum()
    
env_balance=co2Balance.balCO2Year(balance_sum_y)
#prim_savings_y=env_balance.prim_savings()
co2_y=env_balance.CO2_savings()
eq_trees=co2_y*25/40



# #para balance de la vivienda dentro de la CEL 

# d_energybalanceComb_base=d_energybalanceComb.loc[:,'Med_cp':'Net_cp']
# part_to_drop = '_cp'
# d_energybalanceComb_base.columns = d_energybalanceComb_base.columns.str.replace(part_to_drop, '')


#los costes se consideran proporcionales al coef. de reparto

area_reparto=area_t*coef['Cbase']

coste_viv=(coste/area_t)*area_reparto
coste_mant_viv=(coste_mant/area_t)*area_reparto

data_comp_viv=compSimplificada.balEcoYear(d_energybalanceComb['Cbase'],area_reparto,parameters_eco)
savings_y_viv=data_comp_viv.annualSavings(tariff_y)
#pback_viv,coste_viv=data_comp.simplePayback(savings_y_viv,cost_ag)
NPV_value_viv,payback_c_viv=data_comp_viv.calcNPV(coste_viv,tariff_y,coste_mant_viv)


#ahorro respecto a un autoconsumo individual de la misma potencia
#coste de referencia para el autoconsumo individual, considerando el area proporcional
area_ind=[area_reparto]
ref_cost_ind, coste_mant_ind = data_comp.dataCost(area_ind)

#caso el coste informado por el usuario para la instalación total sea más alto que el coste de referencia, aplicar este incremento al coste de referencia para la instalación individual
# if parameters['cost_inv_total']>ref_cost_inicial:
#     ref_cost_ind=ref_cost_ind*(parameters['cost_inv_total']/ref_cost_inicial)

#pback_viv_ind,coste_viv_ind=data_comp.simplePayback(savings_y_viv,coste_ind)

NPV_value_viv_ind,payback_c_viv_ind=data_comp_viv.calcNPV(ref_cost_ind,tariff_y,coste_mant_ind)
red_payback= 100*(1-(payback_c_viv/payback_c_viv_ind))
# savings_comp=round(coste_viv/coste_ind*100)

# NPV_life=NPV_value[len(NPV_value)-1]
# data_comp.graphNPV(NPV_value,payback_c)
# LCOE=data_comp.calcLCOE(coste)

balance_sum_y_viv=pd.Series()
for i in d_energybalanceComb['Cbase'].columns:
    balance_sum_y_viv[i]=d_energybalanceComb['Cbase'][i].sum()

env_balance=co2Balance.balCO2Year(balance_sum_y_viv)
#prim_savings_viv=env_balance.prim_savings()
co2_y_viv=env_balance.CO2_savings()
eq_trees_viv=co2_y_viv*25/(40)



#%%Outputs

#     # Create the output json for Ciclica
    
results = {
    "energia_disp_viv": total_PV_viv,
    "balanc_energ_viv": LoCov_indiv['Cbase'],
    "cost_total_viv": coste_viv,
    "estalvi_viv": savings_y_viv,
    "payback_anys_viv": payback_c_viv,
    "red_payback":red_payback,
    "estalvi_CO2_viv": co2_y_viv,
    "arbres_eq_viv": eq_trees_viv,
    "energia_generada": PV_gen_y,
    "balanc_energ_CEL": LoCov_comb,
    "cost_total_CEL": coste,
    "estalvi_CEL": savings_y,
    "payback_anys_CEL": payback_c,
    "estalvi_CO2_CEL": co2_y,
    "arbres_eq_CEL": eq_trees,
}

with open("Resultados.json", 'w') as f:
    json.dump(results, f, indent=4)

# print(results)
print(json.dumps(results))



#considering tarrif increment for grid and surplus we have to calculate the monthly balance again for the whole lifetime of the PV system
#not sure if this can be done outside the main because in compSimplificada is the methode monthlyBalance
# if parameters_eco['tariff_var_y']>0 and parameters_eco['inc_tariff_surplus']>0:
   
#     savings_y_life=[savings_y]
#     for i in range(1,parameters_eco['pv_life']):
#         tariff_g=tariff_g*(1+parameters_eco['inc_tariff_grid'])
#         tariff_s=tariff_s*(1+parameters_eco['inc_tariff_surplus'])
#         balance_m,c_cost_y=data_comp.monthlyBalance(tariff_g,tariff_s)
#         p_cost,savings_m,savings_y=data_comp.annualSavings(tariff_g, balance_m)
#         savings_y_life.append(savings_y)

# else:
#     #savings_y_life=[savings_y]
#     savings_y_life=[(savings_y-parameters_eco['cuota_y'])]
#     for i in range(1,parameters_eco['pv_life']):
#        # savings_y_life.append(savings_y)
#         savings_y_life.append(savings_y-parameters_eco['cuota_y'])




# topay_y=balance_m.sum()+parameters_eco['cuota_y']
# print (LoCov_comb)
# print(coste,savings_y,payback_c,NPV_life,LCOE)




# Energy Balance m buildings  with or without production(example) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 

# ebal_out = energyBalance_FV.balanceCEL(dataframe_consumption = d_multiyearDdis['2021'], number_of_buildings = 20, dataframe_PV= df_PV_cel.loc[:,['Pv_cel']])
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalanceCEL, LoCov_CEL = energy_balance.start()

# Energy Balance building + n dwellings (example) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 

# control = 0
# LoCov_def = 0
# n_dwellings = 0
# while control == 0:
#     n_dwellings = n_dwellings + 1
#     ebal_out = energyBalance_FV.balanceCombinado(d_yearReal['CamiloJC_CEIP']['2021'],1,df_PV_total.loc[:,['Pv_base']],d_multiyearDdis['2021'],n_dwellings,df_PV_cel.loc[:,['Pv_cel']])
#     energy_balance = energyBalance_FV.calculo(ebal_out)
#     d_energybalanceComb, LoCov_comb = energy_balance.start()
#     if d_energybalanceComb['Et_cp_cel'].sum()/df_PV_total['Pv_base'].sum() <= 0.15:
#         control = 1
#         print('n_dwellings',n_dwellings)

# Energy Balance building + n dwellings (example) + Coeficiente propio <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 

# control = 0
# LoCov_def = 0
# n_dwellings = 0

# #coef_propio = 0.1
# export_limit = []
# export_limit.append(0)
# export_max = 0.15
# count = 0

#adding some coefficients for each hour of the day for one user
# a=[0.1,0.2,0.3,0.1,0.2,0.3,0.1,0.2,0.3,0.1,0.2,0.3,0.1,0.2,0.3,0.1,0.2,0.3,0.1,0.2,0.3,0.1,0.2,0.3]
# coef_propio=a
# b=[]

# #calculating the complementary coefficient for the other user
# for i in range(0,24):
#     b.append(1-a[i])

# coef_cel=b

# #copying the same coefficients for every day of the year
# for i in range(0,364):
#     coef_propio=coef_propio+a
#     coef_cel=coef_cel+b

#code created to plot the monthly consumption of the buildings

# mensual=d_yearReal['Can_Ribes']['2021'].groupby(d_yearReal['Can_Ribes']['2021'].index.month).sum()
# mensual['Med']=mensual['Med']/1000

# plt.figure(figsize=(20, 12))
# plt.bar(mensual.index, mensual['Med'])

# plt.xticks(mensual.index)
# plt.ylabel('El_total')
# plt.xlabel('months')
# title='Can_Ribes'
# plt.title(title)

# plt.savefig(title)




#BALANCE CEL
#creating a dataframe with 3 consumers as an example
# cons_total=pd.concat([d_yearReal['CamiloJC_CEIP']['2021'],d_yearReal['CamiloJC_FP']['2021'],d_multiyearDdis['2021']],axis=1)
# n_users=len(cons_total.columns)
# #naming the columns Cbase and C1 to Cn_users
# name_columns=[None]*n_users 
# name_columns[0]='Cbase'
# for i in range(1,n_users):
#     name_columns[i]='C'+ str(i)
#     cons_total.columns=name_columns
    
# input=coefCalc.CoefVar(cons_total,n_users)
# coefabc=coefCalc.calculo(input)
# coef=coefabc.start()
# # #if we want to have an excel with all coefficients (index is timestamp with year 2021, can be modified)
# # coef.to_excel('coefcomplete.xlsx')
# coef_prop=coef['Cbase']
# coef_cel=coef.iloc[:,1:].sum(axis=1)


# ebal_out = energyBalance_FV.balanceCombinadoCoef(cons_total,n_users,df_PV_total.loc[:,['Pv_base']],d_multiyearDdis['2021'],n_dwellings,df_PV_cel.loc[:,['Pv_cel']], coef_prop, coef_cel)
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalanceComb, LoCov_comb = energy_balance.start()
    
# while control == 0:
#     count = count + 1
#     n_dwellings = n_dwellings + 1
#     ebal_out = energyBalance_FV.balanceCombinadoCoef(d_yearReal['CamiloJC_CEIP']['2021'],1,df_PV_total.loc[:,['Pv_base']],d_multiyearDdis['2021'],n_dwellings,df_PV_cel.loc[:,['Pv_cel']], coef_prop, coef_cel)
#     energy_balance = energyBalance_FV.calculo(ebal_out)
#     d_energybalanceComb, LoCov_comb = energy_balance.start()
#     export_limit.append(d_energybalanceComb['Et_cp_cel'].sum()/df_PV_total['Pv_base'].sum())
#     if export_limit[count] <= export_max:
#         control = 1

#     if export_limit[count-1] == export_limit[count]:
#         control = 1
#         print('n_dwellings',n_dwellings)
#         print('No se llega a las exportaciones máximas indicadas, bajar el coeficiente propio')        
                
# print('Med_cp',d_energybalanceComb['Med_cp'].sum())
# print('Med_cel',d_energybalanceComb['Med_cel'].sum())
# print('Sc',d_energybalanceComb['Sc_cp_cel'].sum())
# print('Dt',d_energybalanceComb['Dt_cp_cel'].sum())
# print('Et_cp',d_energybalanceComb['Et'].sum())
# print('Et',d_energybalanceComb['Et_cp_cel'].sum())
# print('Net',d_energybalanceComb['Net_cp_cel'].sum())
# print('LoCov',LoCov_comb)       
        

 



