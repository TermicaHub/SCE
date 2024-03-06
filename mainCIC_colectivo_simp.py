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
import copy


# Path

direct  = os.getcwd()
sys.path[0] = direct

# Interactors

from interactors import dataFV,dataWeather, resourceConsumption, dataEconomic, baseConsumption


# Calculations

from utils import radiationFV, energyBalance_FV, coefCalc, compSimplificada, tariffCalc,co2Balance, repartoSomCom




  
#%% Get data for PV calculation <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# >>> Angles 
#the data is read from the json file, with all buildings data included

cubierta=dataFV.somCInputsAdv()
getPVdata = dataFV.insert(cubierta)
#df_PV can be calculated only once, considering the inputs are Lst,Lloc,phi which are the same for all buildings/roofs
parameters_all, df_PV= getPVdata.start()



# >>> Weather
#the weather code comes from the json 

weather = dataWeather.outputTRNSYS(clima = parameters_all[0]['clim'])
getWeatherdata = dataWeather.select(weather)

df_clima = getWeatherdata.start()


#>>>Economic parameters
econ_data = dataEconomic.somCInputsAdv()
getEcondata = dataEconomic.insert(econ_data)
parameters_eco = getEcondata.start()

df_PV_total={}

df_PV_ag=pd.DataFrame({'Pv_base': [0] * 8760}, index = df_clima.index)
df_cons_ag=pd.DataFrame({'Cons_total': [0] * 8760}, index = df_clima.index)
df_cons_total={}
# df_cons_min=pd.DataFrame()
# df_cons_max=pd.DataFrame()
df_cons_prom=pd.DataFrame()

area_list=[]
cost_total=0
n_users_list=[]
#aqui empieza el loop para cada edificio

for i in range(len(parameters_all)):
    parameters=parameters_all[i]
    #cost_total+=float(parameters['pv_cost'])
    area_cubierta=0
#OJO: NOS TIENE QUE DAR EL AREA TOTAL PARA CUBIERTA PLANA, SI NO HAY QUE HACER X2
    
           
    selected_dict = {key: parameters[key] for key in ['pva_n1', 'pva_n2','pva_n3']}
    cubiertas = [var for var, value in selected_dict.items() if value != 0]
    
    # Calculate radiation <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
    b_output = radiationFV.dataframe()
    
    PV_dict = {}
    df_PV_base = pd.DataFrame({'Pv_base': [0] * 8760}, index = df_clima.index)
    df_cons = pd.DataFrame({'Cons_total': [0] * 8760}, index = df_clima.index)
    #df_PV_total[i] = pd.DataFrame({'Pv_base': [0] * 8760}, index = df_clima.index)
   # df_PV_total[i] = pd.DataFrame(index = df_clima.index)
   
   #loop para cada area de produccion
    for j in range(0,len(cubiertas)):
        
        
        cubierta_id=cubiertas[j].split('_')[1]
        area_cubierta+=parameters['pva_'+cubierta_id]
        
        
    #para cubierta plana 
        if parameters['type_roof_'+cubierta_id]=="roof_flat":
            parameters_cubierta={'gamma':parameters['gamma_'+cubierta_id],'beta':parameters['beta_'+cubierta_id],'area':parameters['pva_'+cubierta_id]/2,'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
            b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
            df_PV_new = b.start()
            
            PV_dict.setdefault(cubiertas[j],df_PV_new)
            parameters_cubierta={'gamma':-1*(parameters['gamma_'+cubierta_id]),'beta':parameters['beta_'+cubierta_id],'area':parameters['pva_'+cubierta_id]/2,'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
            b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
            df_PV_new = b.start()
            PV_dict.setdefault(cubiertas[j]+'_opuesto',df_PV_new)
           
           
        #para cubierta inclinada
        elif parameters['type_roof_'+cubierta_id]=="roof_tilt":
            parameters_cubierta={'gamma':parameters['gamma_'+cubierta_id],'beta':parameters['beta_'+cubierta_id],'area':parameters['pva_'+cubierta_id],'theta':parameters['theta_'+cubierta_id],'Lloc':parameters['Lloc'],'Lst':parameters['Lst'],'phi':parameters['phi']}
            
            b = radiationFV.calculo(b_output, df_clima, df_PV, parameters_cubierta , 'Pv_base')
            #b = radiationFV.calculo(b_output, df_clima, df_PV, parameters , 'Pv_base')
            df_PV_new = b.start()
            PV_dict.setdefault(cubiertas[j],df_PV_new)

            
        #ahora se agrega toda la producción
        #todas las cubiertas del edificio
        for key in PV_dict:
            df_PV_base['Pv_base'] = df_PV_base['Pv_base'] + PV_dict[key]['Pv_base']

        #adding additional losses to reduce production of main building PV_total           
        df_PV_base['Pv_base'] = df_PV_base['Pv_base'] * (1-parameters_eco['pvsys_loss'])
        df_PV_total['pv'+str(i)]=df_PV_base
        df_PV_ag+=df_PV_base
       
        # PV_gen_cp_y=df_PV_total['Pv_base'].sum()
        # PV_gen_cel_y=df_PV_cel['Pv_cel'].sum()
        #PV_gen_y[i]=df_PV_total['pv'+str(i)]['Pv_base'].sum()
        

        

    #demanda de cada edificio
        
    data_cons = baseConsumption.ConsSimple(parameters['numV'])
    df_cons=data_cons.cons_total()
    #diccionario con dataframe de consumo de cada edificio                                    
    df_cons_total[i]=df_cons
    df_cons_ag+=df_cons
    n_users_list.append(parameters['numV'])
    
    #añadir el area total de la cubierta a lista de areas

    area_list.append(area_cubierta)
    
#agregar generacion total  
PV_gen_y=df_PV_ag['Pv_base'].sum()

#area total CEL
area_t=sum(area_list)


#consumo promedio
df_cons_prom=df_cons_ag/sum(n_users_list)

#%%Definir el perfil de demanda de cada edificio 


#agregar todos los perfiles de la CEL
#identificar entre todos el consumo maximo, promedio y minimo



# data Som Comunitat, perfiles tipo definidos en el archivo \\resources\\data\\ConsProfiles.csv

# c_output = resourceConsumption.SomCom()
# cons = resourceConsumption.get_data(c_output)
# dataSom = cons.start()

# ## crear un dataframe para todos los consumos
# n_users_vp=parameters['n_part_ep']
# n_users_cel=parameters['p_part_cel']*parameters['numV_cel']
# n_users= n_users_vp+n_users_cel
# name_columns=[None]*n_users 
# name_columns[0]='Cbase'

# for i in range(1,n_users):
#     name_columns[i]='C'+ str(i)

# cons_total=pd.DataFrame(index=df_cons.index,columns=name_columns)
# cons_total['Cbase']=df_cons['Total']
    
#consumo del usuario base (vivienda)
# if parameters['consum_base']<=1500:
#     cons_total['Cbase']=dataSom['C1500']
# elif 1500<parameters['consum_base']<=2000:
#     cons_total['Cbase']=dataSom['C2025']
# elif 2000<parameters['consum_base']<=2500:
#     cons_total['Cbase']=dataSom['C2500']  
# elif parameters['consum_base']>2500:
#     cons_total['Cbase']=dataSom['C3000']  
    
# #consumo de los demás usuarios (ed. base y ed. CEL)
# if parameters['type_consum']=="cons_same":
#     #mismo perfil edificio base
    
#     for i in cons_total.columns[1:]:
#     #this will be based on user input
#     #this will have to be a loop with the profile we decide for users of the CEL
#         cons_total[i]=cons_total['Cbase']

# if parameters['type_consum']=="cons_mean":
#     #perfil promedio "Med"
#     for i in cons_total.columns[1:]:
#     #this will be based on user input
#     #this will have to be a loop with the profile we decide for users of the CEL
#         cons_total[i]=dataSom['Med']


#%% Definir coeficientes proporcionales al consumo
coef=pd.Series()
n_users=0
cons_total=pd.DataFrame()
for key in df_cons_total:
    #para el numero de usuarios
    for j in range(n_users_list[key]):
        n_users+=1
        name_column= 'C'+ str(n_users)
        print (name_column)
        cons_total[name_column]=df_cons_total[key]/n_users_list[key]
        coef[name_column]=cons_total[name_column].sum()/df_cons_ag.values.sum()


#%% Energy balance 

#balance CEL con reparto igualitario

#balance combinado con un coeficiente de reparto para cada usuario 

ebal_out = energyBalance_FV.balanceCombinadoCoefSomCom(cons_total,df_PV_ag,coef)
energy_balance = energyBalance_FV.calculo(ebal_out)
d_energybalanceComb,LoCov_indiv,LoCov_comb = energy_balance.start()


#balance perfil promedio asignandole un coef promedio?
coef_prom=coef.mean()
total_PV_prom=coef_prom*df_PV_ag
ebal_out = energyBalance_FV.balancePropioSomCom(df_cons_prom, total_PV_prom)
energy_balance = energyBalance_FV.calculo(ebal_out)
d_energybalance_prom, LoCov_prom = energy_balance.start()




#%%Economic balance
#>>>Economic parameters:
#economic inputs
econ_data = dataEconomic.somCInputs()
getEcondata = dataEconomic.insert(econ_data)
parameters_eco = getEcondata.start()

#calculo tarifa
myTariff=tariffCalc.tariffHourly(cons_total.index,parameters_eco['tariff_peak'],parameters_eco['tariff_flat'],parameters_eco['tariff_valley'],parameters_eco['tariff_surplus'])
tariff_out=tariffCalc.calculo(myTariff)
tariff_y=tariff_out.start()
    

tariff_new={}
for i in range(0,parameters_eco['pv_life']):
    tariff_new[i]=tariff_y*((1+parameters_eco['tariff_var_y'])**i)
    

#BALANCE ECONÓMICO CEL AGREGADA

data_comp=compSimplificada.balEcoYear(d_energybalanceComb['Total'],area_t,parameters_eco)

#para cada cubierta, asigna un coste y un area

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


# #para balance de la vivienda promedio 

total_PV_prom_y=total_PV_prom['Pv_base'].sum()
#los costes se consideran proporcionales al coef. de reparto

area_reparto=area_t*coef_prom

coste_viv=(coste/area_t)*area_reparto
coste_mant_viv=(coste_mant/area_t)*area_reparto

data_comp_viv=compSimplificada.balEcoYear(d_energybalance_prom,area_reparto,parameters_eco)
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
for i in d_energybalance_prom.columns:
    balance_sum_y_viv[i]=d_energybalance_prom[i].sum()

env_balance=co2Balance.balCO2Year(balance_sum_y_viv)
#prim_savings_viv=env_balance.prim_savings()
co2_y_viv=env_balance.CO2_savings()
eq_trees_viv=co2_y_viv*25/(40)



#%%Outputs

#     # Create the output json for Ciclica
    
results = {
    "energia_disp_viv": total_PV_prom_y,
    "balanc_energ_viv": LoCov_prom,
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




