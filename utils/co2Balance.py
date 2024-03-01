# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:20:45 2024

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


class balCO2Year:
    def __init__(self,df_balance_y):
        self.balance_y=df_balance_y
                    
        # Factores de paso
        # Electricidad RED peninsular
        self.Fp_REN = 0.414
        self.Fp_NREN = 1.954
        # Electricidad insitu (PV)
        self.Fp_REN_PV = 1.000
        self.Fp_NREN_PV = 0.000
        # kg CO2/kWh energia final
        self.CO2_coeff = 0.331
    
    def prim_before (self):
        Prim_NREN=self.balance_y['Med']*self.Fp_NREN
        return Prim_NREN
    
    def CO2_before(self):
        CO2_NREN=self.balance_y['Med']*self.CO2_coeff
        return CO2_NREN
    
    def prim_after(self):
        Prim_NREN_grid=self.balance_y['Dt']*self.Fp_NREN
        Prim_REN_autocons=self.balance_y['Sc']*self.Fp_REN_PV
        Prim_REN_volcada=self.balance_y['Et']*self.Fp_REN
        Prim_Total=Prim_NREN_grid+Prim_REN_autocons+Prim_REN_volcada
        return Prim_Total
    
    def CO2_after(self):
        CO2_grid=self.balance_y['Dt']*self.CO2_coeff                 
        return CO2_grid
    
    def prim_savings(self):
        Prim_estalvi=self.prim_before() - self.prim_after()    
        return Prim_estalvi
    
    def CO2_savings(self):
        CO2_estalvi=self.CO2_before() - self.CO2_after()   
        return CO2_estalvi  
        
