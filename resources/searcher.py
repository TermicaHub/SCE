# -*- coding: utf-8 -*-
"""

@author: srabadan
"""

from abc import ABC, abstractmethod


class currencyType(ABC):
    @abstractmethod
    def searchValue(self,nameVar,value):
        pass              
      



class Unique(currencyType): 

    def searchValue(self,nameVar,value): # Search value in nameVar (1 variable)
        if value in nameVar:
            return True   # Value found
        if value not in nameVar:
            return False  # Value not found
    
class List(currencyType):

    def searchValue(self,nameVar,value):  # Search value in nameVar (list)
        pos = []
        for i in range(0,len(nameVar)):
            if value in str(nameVar[i]):
                pos.append(i)
        return pos                      # Return position like a list
             
                
class Dict(currencyType):                 # Search value in nameVar (dictionary)
    def searchValue(self,nameVar,value):
        key_pos = {}
        for key, val in nameVar.items():
            count = 0            
            for i in val:
                if i == value:
                    key_pos.setdefault(key,[]).append(count)
                count = count + 1    
        return key_pos           # Return position like a dictionary with key = nameVar.key and value the position 
                       
class dataFrame(currencyType):      # Search value in nameVar (dataFrame)
    def searchValue(self,nameVar,value):
        row_col = {}
        for col, row in nameVar.items():
            for i in row.index:
                if nameVar.at[i,col] == value:
                    row_col.setdefault(i,[]).append(col)
        return row_col            # Return position like a dictionary with key = row and value = column            
     


            
class searcher:
    def __init__(self, typeVar : currencyType, nameVar, value):
        self.typeVar = typeVar
        self.nameVar = nameVar
        self.value = value

        
    def start(self):
        return self.typeVar.searchValue(self.nameVar, self.value)      
        

    
if __name__ == '__main__':
# Test lista
    a = [1, 2, 3, 4, 4]
    b = ['Barcelona', 'Madrid', 'Valencia', ' Baleares']
    c = [20, 30, 50, 'Tarragona norte','Tarragona sur', 'Girona', 'Lleida']    
    nameVar = c
    typeVar = List()
    value = 'Tarragona' 
    search = searcher(typeVar, nameVar, value)
    position = search.start()

# Test diccionario
    # a = {'Enero' : [1, 2, 3, 4, 3,5],'Febrero' : [10, 23 , 3 , 89], 'Provincia' : ['Barcelona', 'Girona', 'Lleida', 'Tarragona']}    
    # nameVar = a
    # typeVar = Dict()
    # value = 3
    # search = searcher(typeVar,nameVar,value)
    # key_pos = search.start()
    
# Test dataFrame    
    # import pandas as pd
    # f = pd.DataFrame()
    # dia = ['Lunes', 'Martes', 'Miércoles','Jueves', 'Viernes']
    # work_package = ['WP1','WP2','WP3','WP4','WP5','WP6','WP8','WP9','WP10']
    # f.index = dia
    # f[work_package] = 0
    # f['WP1'] = [1,3,0,0,1]
    # f['WP4'] = [0,8,0,0,0]
    # f['WP5'] = [0,8,0,0,0]
    # f['WP9'] = [0,0,0,3,1]    
    # nameVar = f
    # typeVar = dataFrame()
    # value = 1
    # search = searcher(typeVar,nameVar,value)
    # row_col = search.start()
    
    
