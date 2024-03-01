# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 13:22:41 2023

@author: mcalcagnotto
"""

#Abstract method import

from abc import ABC, abstractmethod
import pandas as pd

import math
import numpy as np
from datetime import datetime

# Resources

from repositories import dataEcon_repository


# Abstract class

class insertionMethod(ABC):
    @abstractmethod
    def __init__(self):
        pass
    def getInputs(self):
        pass  
    
        
class somCInputs(insertionMethod): 
    def __init__(self):
        pass
    def getInputs(self):
        TypeFile_Econ = dataEcon_repository.ciclicaSimple()
        get_data = dataEcon_repository.dataEcon(TypeFile_Econ)
        data_params = get_data.start()
        return data_params

class PVPCData(insertionMethod):
    def __init__(self):
        pass
    def getInputs(self):
        TypeFile_PVPC_active = dataEcon_repository.PVPCActive()
        get_data = dataEcon_repository.dataEcon(TypeFile_PVPC_active)
        active_PVPC=get_data.start()
        
        TypeFile_PVPC = dataEcon_repository.PVPCSurplus()
        get_data = dataEcon_repository.dataEcon(TypeFile_PVPC)
        surplus_PVPC=get_data.start()
                
        return active_PVPC,surplus_PVPC
    

# class refCost (insertionMethod): 
#     def __init__(self):
#         pass
#     def getInputs(self):
        
#         TypeFile_Cost = dataEcon_repository.defaultCosts()
#         get_data = dataEcon_repository.dataEcon(TypeFile_Cost)
#         data_params = get_data.start()
                
#         return data_params
    
    
    
# class PriceInput(insertionMethod):
#     def __init__(self):
#         pass
#     def getTariff(self):
        
        


class insert:
    def __init__(self, insert : insertionMethod):
        self.insert = insert
         
    def start(self):        
        return self.insert.getInputs()
    
    

    
