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

from utils import radiationFV, energyBalance_FV, compSimplificada, tariffCalc,co2Balance, repartoSomCom




  
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
df_cons_min=pd.DataFrame()
df_cons_max=pd.DataFrame()
df_cons_prom=pd.DataFrame()

area_list=[]
cost_total=0
n_part_total=0
#aqui empieza el loop para cada edificio

for i in range(len(parameters_all)):
    parameters=parameters_all[i]
    cost_total+=float(parameters['pv_cost'])
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
        #si tiene participantes, calcula la demanda
        if parameters['n_part']>0:                                          
            data_cons = baseConsumption.ConsBuilding(parameters['n_part'],parameters['n_occ'],parameters['n_dhw'],parameters['n_stove'],parameters['n_oven'],parameters['n_heat_none'],parameters['n_heat_rad'],parameters['n_heat_hp'],parameters['n_heat_gas'],parameters['n_acc_none'],parameters['n_acc_split'],parameters['n_acc_hp'],parameters['areaV'],parameters['consum_mean'])    
                
            # df_cons_eq=data_cons.cons_eq()
                  
            # df_cons_hvac=data_cons.cons_hvac()
            df_cons['Cons_total'],df_cons_av,factor_c=data_cons.cons_total()
            df_cons_total[i]=df_cons
            df_cons_ag+=df_cons
            
            df_cons_min[i]=data_cons.cons_min(factor_c)
            df_cons_max[i]=data_cons.cons_max(factor_c)
            df_cons_prom[i]=df_cons_av
        
        #si no tiene participantes, deja el consumo total en 0 y no añade nada en df_cons_max, df_cons_min, df_cons_mean
        else:
            df_cons_total[i]=df_cons
            
       
        #añadir el area total de la cubierta a lista de areas

    area_list.append(area_cubierta)
    n_part_total+=parameters['n_part']
        
#agregar generacion total  
PV_gen_y=df_PV_ag['Pv_base'].sum()


#buscar el minimo entre los perfiles minimos de cada edificio
profile_min=pd.DataFrame()
profile_max=pd.DataFrame()
profile_mean=pd.DataFrame()

profile_min['Med']=df_cons_min[df_cons_min.sum().idxmin()]
#buscar el maximo entre los perfiles maximos de cada edificio
profile_max['Med']=df_cons_max[df_cons_min.sum().idxmax()]
#perfil promedio entre todos los edificios
profile_mean['Med']=df_cons_prom.mean(axis=1)

#area total CEL
area_t=sum(area_list)

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


#%% Estimating distribution coefficients + energy balance with share coefficients

if parameters_eco['type_coef']=="coef_share":
    coef=pd.DataFrame(index=[0.5,1,2,3,4,5])
    coef['n_viv']=[parameters_eco['share_0.5'],parameters_eco['share_1'],parameters_eco['share_2'],parameters_eco['share_3'],parameters_eco['share_4'],parameters_eco['share_5']]
   #redondeo la potencia total para 1 decimal
    P_tot=round(area_t*parameters_eco['conv_area'],1)
    #redondear para 0 o para 0.5
    #si el decimal d, d<0.25 redondeo al entero de abajo
    if P_tot-int(P_tot)<0.25:
        P_tot_round=int(P_tot)
    #si 0.25<d<0.5 y 0.<5d<0.75 redondeo a 0.5
    elif P_tot-int(P_tot)>0.25 and P_tot-int(P_tot)<0.75 :
        P_tot_round=int(P_tot)+0.5
    #si d>0.75 redondeo al entero de arriba 
    elif P_tot-int(P_tot)>0.75:
        P_tot_round=int(P_tot)+1
    
    coef['coef_ind']=coef.index/P_tot_round
   # coef['coef_ind']=[0.5/P_tot_round,1/P_tot_round,2/P_tot_round,3/P_tot_round,4/P_tot_round,5/P_tot_round]
    coef['coef_ag']=coef['n_viv']*coef['coef_ind']
    
    #create a dataframe for aggregated consumption of each share 
    
    cons_total=pd.DataFrame(index=df_cons.index)  
    coef_new=pd.Series()
    for i in range (len(coef)):
        name_column='C'+ str(i+1)
        coef_new[name_column]=coef['coef_ag'][coef.index[i]]
        #cons_total[name_column]=coef_new[name_column]*df_cons_ag['Cons_total']
        #considerando el consumo promedio 
        cons_total[name_column]=coef_new[name_column]*profile_mean*coef['n_viv'][coef.index[i]]
        
    #balance combinado con consumos agregados segun coef de reparto
    ebal_out = energyBalance_FV.balanceCombinadoCoefSomCom(cons_total,df_PV_ag,coef_new)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalanceComb,LoCov_indiv,LoCov = energy_balance.start()
    
    #balance perfiles maximo, minimo y promedio - asignar los coeficientes maximo, minimo y promedio de los informados 
    
    coef_min=coef.loc[coef.index[coef['n_viv']!=0].min()]['coef_ind']
    coef_max=coef.loc[coef.index[coef['n_viv']!=0].max()]['coef_ind']
    #average coefficient is the average of the indiividual coefficients, without considering how many users have each of them
    # coef_av=coef.loc[coef.index[coef['n_viv']!=0]]['coef_ind'].mean()
    #average coefficient considering the weighted average
    coef_mean=1/coef['n_viv'].sum()
    
    df_PV_reparto_min=coef_min*df_PV_ag
    ebal_out = energyBalance_FV.balancePropioSomCom(profile_max, df_PV_reparto_min)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance_min, LoCov_min = energy_balance.start()
    
    df_PV_reparto_max=coef_max*df_PV_ag
    ebal_out = energyBalance_FV.balancePropioSomCom(profile_mean, df_PV_reparto_max)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance_max, LoCov_max = energy_balance.start()
    
    df_PV_reparto_mean=coef_mean*df_PV_ag
    ebal_out = energyBalance_FV.balancePropioSomCom(profile_mean, df_PV_reparto_max)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance_mean, LoCov_mean = energy_balance.start()
    
#%% Energy balance 

#balance CEL con reparto igualitario

if parameters_eco['type_coef']=="coef_eq":
     #si el coef es igual, podemos hacer el balance con toda la produccion y el consumo agregados
    ebal_out = energyBalance_FV.balancePropioSomCom(df_cons_ag, df_PV_ag)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance, LoCov = energy_balance.start()

#balance perfiles maximo, minimo y promedio, asignando el mismo coef a todos
    coef_min=1/n_part_total
    df_PV_reparto_min=coef_min*df_PV_ag
    ebal_out = energyBalance_FV.balancePropioSomCom(profile_max, df_PV_reparto_min)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance_min, LoCov_min = energy_balance.start()

    coef_max=1/n_part_total
    df_PV_reparto_max=coef_max*df_PV_ag
    ebal_out = energyBalance_FV.balancePropioSomCom(profile_max, df_PV_reparto_max)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance_max, LoCov_max = energy_balance.start()
    
    coef_mean=1/n_part_total
    df_PV_reparto_mean=coef_mean*df_PV_ag
    ebal_out = energyBalance_FV.balancePropioSomCom(profile_mean, df_PV_reparto_mean)
    energy_balance = energyBalance_FV.calculo(ebal_out)
    d_energybalance_mean, LoCov_mean = energy_balance.start()
    
    
#energia total disponible

total_PV_viv_max=df_PV_reparto_max['Pv_base'].sum()
total_PV_viv_min=df_PV_reparto_min['Pv_base'].sum()
total_PV_viv_mean=df_PV_reparto_mean['Pv_base'].sum()

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

# #balance combinado con un coeficiente de reparto para cada usuario 
# ebal_out = energyBalance_FV.balanceCombinadoCoefSomCom(cons_total,df_PV_total,coef)
# energy_balance = energyBalance_FV.calculo(ebal_out)
# d_energybalanceComb,LoCov_indiv,LoCov_comb = energy_balance.start()

#energia total anual que recibe la vivienda
#total_PV_viv=d_energybalanceComb['Cbase']['Pv_base'].sum()

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


#>>> seleccion tipo de tarifa

if parameters_eco['tariff_type']=="tariff_flat":
    myTariff=tariffCalc.tariffSingle(df_cons_ag.index,parameters_eco['tariff_single'],parameters_eco['tariff_surplus'])
    tariff_out=tariffCalc.calculo(myTariff)
    tariff_y=tariff_out.start()
    
elif parameters_eco['tariff_type']=="tariff_hourly":
    myTariff=tariffCalc.tariffHourly(df_cons_ag.index,parameters_eco['tariff_peak'],parameters_eco['tariff_flat'],parameters_eco['tariff_valley'],parameters_eco['tariff_surplus'])
    tariff_out=tariffCalc.calculo(myTariff)
    tariff_y=tariff_out.start()
    
elif parameters_eco['tariff_type']=="tariff_pvpc":
    myTariff=tariffCalc.tariffPVPC(df_cons_ag.index)
    tariff_out=tariffCalc.calculo(myTariff)
    tariff_y=tariff_out.start()
    
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

#pasar el coste total informado para coste/m2
cost_ag=cost_total/area_t

if parameters_eco['type_coef']=="coef_share":
    data_comp=compSimplificada.balEcoYear(d_energybalanceComb['Total'],area_t,parameters_eco)
    balance_sum_y=pd.Series()
    for i in d_energybalanceComb['Total'].columns:
        balance_sum_y[i]=d_energybalanceComb['Total'][i].sum()
        
elif parameters_eco['type_coef']=="coef_eq":
    data_comp=compSimplificada.balEcoYear(d_energybalance,area_t,parameters_eco)
    balance_sum_y=pd.Series()
    for i in d_energybalance.columns:
        balance_sum_y[i]=d_energybalance[i].sum()
        
        
savings_y=data_comp.annualSavings(tariff_y)
#cost_ag=parameters_eco['cost_inv_total']/area_t
#pback,coste=data_comp.simplePayback(savings_y,cost_ag)
ref_cost_inicial,coste_mant=data_comp.dataCost(area_list)
NPV_value,payback_c=data_comp.calcNPV(cost_total,tariff_y,coste_mant)


# NPV_life=NPV_value[len(NPV_value)-1]
# data_comp.graphNPV(NPV_value,payback_c)
# LCOE=data_comp.calcLCOE(coste)

  
env_balance=co2Balance.balCO2Year(balance_sum_y)
#prim_savings_y=env_balance.prim_savings()
co2_y=env_balance.CO2_savings()
eq_trees=co2_y*25/40


#BALANCE ECONÓMICO PERFILES MAXIMO, MINIMO Y PROMEDIO
#necesito savings, cost, payback

area_reparto_max=area_t*coef_max
cost_viv_max=(cost_total/area_t)*area_reparto_max
coste_mant_viv_max=(coste_mant/area_t)*area_reparto_max

data_comp_viv=compSimplificada.balEcoYear(d_energybalance_max,area_reparto_max,parameters_eco)
savings_y_viv_max=data_comp_viv.annualSavings(tariff_y)
#pback_viv,coste_viv=data_comp.simplePayback(savings_y_viv,cost_ag)
NPV_value_viv_max,payback_c_viv_max=data_comp_viv.calcNPV(cost_viv_max,tariff_y,coste_mant_viv_max)


area_reparto_min=area_t*coef_min
cost_viv_min=(cost_total/area_t)*area_reparto_min
coste_mant_viv_min=(coste_mant/area_t)*area_reparto_min

data_comp_viv=compSimplificada.balEcoYear(d_energybalance_min,area_reparto_min,parameters_eco)
savings_y_viv_min=data_comp_viv.annualSavings(tariff_y)
#pback_viv,coste_viv=data_comp.simplePayback(savings_y_viv,cost_ag)
NPV_value_viv_min,payback_c_viv_min=data_comp_viv.calcNPV(cost_viv_min,tariff_y,coste_mant_viv_min)


area_reparto_mean=area_t*coef_mean
cost_viv_mean=(cost_total/area_t)*area_reparto_mean
coste_mant_viv_mean=(coste_mant/area_t)*area_reparto_mean

data_comp_viv=compSimplificada.balEcoYear(d_energybalance_mean,area_reparto_mean,parameters_eco)
savings_y_viv_mean=data_comp_viv.annualSavings(tariff_y)
#pback_viv,coste_viv=data_comp.simplePayback(savings_y_viv,cost_ag)
NPV_value_viv_mean,payback_c_viv_mean=data_comp_viv.calcNPV(cost_viv_mean,tariff_y,coste_mant_viv_mean)

# area_reparto=area_t*coef['Cbase']

# coste_viv=(parameters['cost_inv_total']/area_t)*area_reparto
# coste_mant_viv=(coste_mant/area_t)*area_reparto

# data_comp_viv=compSimplificada.balEcoYear(d_energybalanceComb['Cbase'],area_reparto,parameters_eco)
# savings_y_viv=data_comp_viv.annualSavings(tariff_y)
# #pback_viv,coste_viv=data_comp.simplePayback(savings_y_viv,cost_ag)
# NPV_value_viv,payback_c_viv=data_comp_viv.calcNPV(coste_viv,tariff_y,coste_mant_viv)

    

#data_comp=compSimplificada.balEcoYear(d_energybalanceComb['Total'],area_t,parameters_eco)
# coste_mant_perarea=data_comp.mantCost()
# savings_y=data_comp.annualSavings(tariff_y)
# #cost_ag=parameters_eco['cost_inv_total']/area_t
# pback,coste=data_comp.simplePayback(savings_y,cost_ag)
# NPV_value,payback_c=data_comp.calcNPV(coste,tariff_y,coste_mant_perarea)


# # NPV_life=NPV_value[len(NPV_value)-1]
# # data_comp.graphNPV(NPV_value,payback_c)
# # LCOE=data_comp.calcLCOE(coste)

# balance_sum_y=pd.Series()
# for i in d_energybalanceComb['Total'].columns:
#     balance_sum_y[i]=d_energybalanceComb['Total'][i].sum()
    
# env_balance=co2Balance.balCO2Year(balance_sum_y)
# #prim_savings_y=env_balance.prim_savings()
# co2_y=env_balance.CO2_savings()
# eq_trees=co2_y/(80/30)



# #para balance de la vivienda dentro de la CEL 

# d_energybalanceComb_base=d_energybalanceComb.loc[:,'Med_cp':'Net_cp']
# part_to_drop = '_cp'
# d_energybalanceComb_base.columns = d_energybalanceComb_base.columns.str.replace(part_to_drop, '')


# #aqui el coste total y el de mantenimiento se calculan en funcion del area, por lo que consideraremos el area proporcional al reparto de la vivienda base
# area_reparto=area_t*coef['Cbase']

# data_comp=compSimplificada.balEcoYear(d_energybalanceComb['Cbase'],area_reparto,parameters_eco)
# savings_y_viv=data_comp.annualSavings(tariff_y)
# pback_viv,coste_viv=data_comp.simplePayback(savings_y_viv,cost_ag)
# NPV_value_viv,payback_c_viv=data_comp.calcNPV(coste_viv,tariff_y,coste_mant_perarea)


# #ahorro respecto a un autoconsumo individual de la misma potencia
# cost_defecto=[286,254,189,171,153,139]

# if area_reparto<23.02:
#     coste_ind=cost_defecto[0]

# elif area_reparto<92.09:
#     coste_ind=cost_defecto[1]
    
# elif area_reparto<230.23:
#     coste_ind=cost_defecto[2]

# elif area_reparto<460.46:
#     coste_ind=cost_defecto[3]

# elif area_reparto<2302.33:
#     coste_ind=cost_defecto[4]
    
# elif area_reparto<4604.65:
#     coste_ind=cost_defecto[5]

    
# pback_viv_ind,coste_viv_ind=data_comp.simplePayback(savings_y_viv,coste_ind)
# coste_mant_perarea_ind=data_comp.mantCost()
# NPV_value_viv_ind,payback_c_viv_ind=data_comp.calcNPV(coste_viv_ind,tariff_y,coste_mant_perarea_ind)
# red_payback= 100*(1-(payback_c_viv/payback_c_viv_ind))
# # savings_comp=round(coste_viv/coste_ind*100)

# # NPV_life=NPV_value[len(NPV_value)-1]
# # data_comp.graphNPV(NPV_value,payback_c)
# # LCOE=data_comp.calcLCOE(coste)

# balance_sum_y_viv=pd.Series()
# for i in d_energybalanceComb['Cbase'].columns:
#     balance_sum_y_viv[i]=d_energybalanceComb['Cbase'][i].sum()

# env_balance=co2Balance.balCO2Year(balance_sum_y_viv)
# #prim_savings_viv=env_balance.prim_savings()
# co2_y_viv=env_balance.CO2_savings()
# eq_trees_viv=co2_y_viv/(80/30)



#%%Outputs

#     # Create the output json for Ciclica
    
results = {
    "energia_disp_viv_max": total_PV_viv_max,
    "balanc_energ_viv_max": LoCov_max,
    "cost_total_viv_max": cost_viv_max,
    "estalvi_viv_max": savings_y_viv_max,
    "payback_anys_viv_max": payback_c_viv_max,
    "energia_disp_viv_min": total_PV_viv_min,
    "balanc_energ_viv_min": LoCov_min,
    "cost_total_viv_min": cost_viv_min,
    "estalvi_viv_min": savings_y_viv_min,
    "payback_anys_viv_min": payback_c_viv_min,
    "energia_disp_viv_mean": total_PV_viv_mean,
    "balanc_energ_viv_mean": LoCov_mean,
    "cost_total_viv_mean": cost_viv_mean,
    "estalvi_viv_mean": savings_y_viv_mean,
    "payback_anys_viv_mean": payback_c_viv_mean,
    "energia_generada": PV_gen_y,
    "balanc_energ_CEL": LoCov,
    "cost_total_CEL": cost_total,
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
        

 



