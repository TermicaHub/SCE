# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:51:06 2022

@author: srabadan
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import math
from interactors import pvgis_FVmodules
import warnings

class outputFormat(ABC):
    @abstractmethod
    def calculation(self):
        pass  


class dataframe(outputFormat):
    def calculation(self,input_df, gamma_nx, beta_nx, pva_nx, theta_in_nx, final_pva_field):                
        # Standard list of the 16 alpha angles of orientation 
       
        def calc_m1_nx(df_temp,gamma_nx, beta_nx, pva_nx, theta_in_nx, final_pva_field):
            alpha = [-180.0, -157.5, -135.0, -112.5, -90.0, -67.5, -45.0, -22.5, 0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5]            
            warnings.filterwarnings("ignore")
            df = df_temp.copy()
        
            def calc_costheta(thetaz2, gammas2, beta_n, gamma_n):
                temp = math.cos(math.radians(thetaz2)) * math.cos(math.radians(beta_n)) + \
                    math.sin(math.radians(thetaz2)) * math.cos(math.radians(gammas2 - gamma_n)) * math.sin(math.radians(beta_n))
                return temp
            df['costheta'] = df.apply(lambda row: calc_costheta(row.thetaz2, row.gammas2, beta_nx, gamma_nx), axis=1)
            df['theta2'] = [math.degrees(math.acos(x)) for x in df.costheta]
        
            # Calculation of beam radiation
            def calc_beam_rad(row):
                #If theta2 (angle of incidence of beam radiation on tilted surface) is greater than 90, the sun is behind the panel, in this case there will be no beam radiation
                if row.theta2>90:
                    return 0
                else:
                    return math.cos(math.radians(row.theta2)) / math.cos(math.radians(row.thetaz2))
            
            df['Rb'] = df.apply(lambda row: calc_beam_rad(row), axis=1)
            df['IbT2'] = df.IbH * df.Rb
        
            # Calculation of diffuse radiation
            Rd = 0.5 * (1 + math.cos(math.radians(beta_nx)))
            df['IdT2'] = Rd * df.IdH
        
            df_shad = pd.DataFrame(index=alpha, data=theta_in_nx, columns=['theta_in_nx'])
        
            # orientación
            if gamma_nx != 0:
                # print(gamma_nx)
                if gamma_nx < 0:
                    # print(gamma_nx)
                    for k in range(abs(int(gamma_nx * 16 / 360))):
                        frstang = df_shad['theta_in_nx'].iloc[0]
                        # print(frstang) # si gamma_nx = -45 frstang = 2
                        for i in range(14):
                            df_shad['theta_in_nx'].iloc[i] = df_shad['theta_in_nx'].iloc[i + 1]
                        df_shad['theta_in_nx'].iloc[15] = frstang
                elif gamma_nx > 0:
                    frstang = df_shad['theta_in_nx'].iloc[15]  # si gamma_nx = -45 frstang = 2
                    for i in range(15, 1, -1):
                        df_shad['theta_in_nx'].iloc[i] = df_shad['theta_in_nx'].iloc[i - 1]
                    df_shad['theta_in_nx'].iloc[0] = frstang
        
            def theta(a, b):  # arguments are alpha and beta in degrees
                a_r = math.radians(a)
                b_r = math.radians(b)
                left = math.tan(b_r) / (1 + (math.tan(b_r))**2)
                # right = math.sqrt((math.tan(a_r))**2 + (1 - math.tan(b_r)**2/(1+math.tan(b_r)**2))**2 + (math.tan(b_r)/(1+math.tan(b_r)**2))**2)
                right = math.sqrt((math.tan(a_r))**2 + (1 - ((math.tan(b_r))**2 / (1 + (math.tan(b_r))**2)))**2 + (math.tan(b_r) / (1 + (math.tan(b_r))**2))**2)
                sigma = math.acos(left / right)  # add condition if right=0 ??
                theta = 90 - math.degrees(sigma)
                return theta
        
            df_shad['theta'] = [theta(alpha, beta_nx) for alpha in df_shad.index]
        
            # Coefficient of shading for diffuse radiation
            numerator = 0
            denominator = 0
            for i in range(len(df_shad)):
                numerator = numerator + 1 - math.cos(math.pi / 2 - math.radians(max(df_shad.theta_in_nx.iloc[i], df_shad.theta.iloc[i])))
                denominator = denominator + 1 - math.cos(math.pi / 2 - math.radians(df_shad.theta.iloc[i]))
            f = numerator / denominator
        
            # Diffuse radiation shaded
            df['IdT2_shad'] = df.IdT2 * f
        
            # gammas is the solar azimuth angle, however it is better to approximate the solar azimuth by one of the 16 values of azimuth
            df['gammas3'] = [df_shad.index[np.abs(df_shad.index - x).argmin()] for x in df.gammas2]
        
            # Solar altitude angle
            df['alphas'] = 90 - df.thetaz2
        
            # simplificacion de bloque anterior
            def are_obstrucction(row):
                alphas = row.alphas
                gammas3 = row.gammas3
                if alphas > df_shad.loc[gammas3].theta_in_nx:
                    return 1
                else:
                    return 0.001
            df['ShadBeam'] = df.apply(are_obstrucction, axis=1)
        
            # Calculation of shaded beam radiation
            df['IbT2_shad'] = df.IbT2 * df.ShadBeam
        
            # Calculation of global radiation beam+diffuse
            df['ItT'] = df.IbT2_shad + df.IdT2_shad
            # PVGIS Constants data monocritaline
            fv_type = pvgis_FVmodules.pvgis_mono()
            data_fv = pvgis_FVmodules.data_fv(fv_type)
            u0, u1, effnom, k1, k2, k3, k4, k5, k6 = data_fv.start()
            # PVGis Equation
            # Calculation of module temperature
            def calc_modul_temperature(Ta, ItT, Wind):
                return Ta + ((ItT) / 3.6) / (u0 + (u1 * (Wind)))
        
            df['Tm'] = calc_modul_temperature(df.Ta.values, df.ItT.values, df.Wind.values)
        
            # Calculation of relative efficienci
        
            def calc_effrel(ItT, Tm):
                return 1 + (k1 * np.log(((ItT) + 0.001) / 3600)) + (k2 * np.log((((ItT) + 0.001) / 3600)**2)) + (k3 * ((Tm) - 25)) + (k4 * ((Tm) - 25) * np.log(((ItT) + 0.001) / 3600)) + (k5 * ((Tm) - 25) * np.log((((ItT) + 0.001) / 3600)**2)) + (k6 * (((Tm) - 25)**2))
        
            df['effrel'] = calc_effrel(df.ItT.values, df.Tm.values)
        
            # Calculation of PV production
        
            def calc_pv_prod(ItT, effrel):
                return ((ItT) / 3600) * (pva_nx) * effnom * (effrel)
        
            df[final_pva_field] = calc_pv_prod(df.ItT.values, df.effrel.values)
            return df
        # Logica de cálculo de SOM COMUNITAT
        
        
        return calc_m1_nx(input_df, gamma_nx, beta_nx, pva_nx, theta_in_nx, final_pva_field)


    
class calculo:
    def __init__(self, outputType : outputFormat,input_clima,input_PV, parameters, final_pva_field):
        self.input_df = pd.concat([input_PV,input_clima], axis = 1)
        self.gamma_nx = parameters['gamma']
        self.beta_nx = parameters['beta']
        self.pva_nx = parameters['area']
        self.theta_in_nx = parameters['theta']
        self.final_pva_field = final_pva_field
        self.outputType = outputType
         
    def start(self):      
        return self.outputType.calculation(self.input_df, self.gamma_nx, self.beta_nx, self.pva_nx, self.theta_in_nx, self.final_pva_field)
        