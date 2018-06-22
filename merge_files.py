# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 17:40:22 2018

@author: Eric
"""
import pandas as pd
import numpy as np

def merge(name):
    new = '.\\data\\new_out_' + name + '.csv'
    to_be = '.\\data\\out_' + name + '.csv'
    old = '.\\old_data\\out_' + name + '.csv'
    
    # read in first data
    dfo = pd.read_csv(old, header = None, na_values= "")
    dfo.fillna("", inplace=True)
    dfo = np.asarray(dfo)
    
    # read in second data
    dfn = pd.read_csv(new, header = None, na_values= "")
    dfn.fillna("", inplace=True)
    dfn = np.asarray(dfn)
    
    # New data formating
    dfo = np.append(dfo, dfn[len(dfo) - 1:], axis = 0)
    
    df = pd.DataFrame(data=dfo[1:], columns=dfo[0]) 
                 
    df.to_csv(to_be, index = False)
    return None
    
    
names = ['edin', 'milorad', 'lidija']
for n in names:
    merge(n)

             