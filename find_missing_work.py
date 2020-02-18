# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 19:06:47 2018

@author: Eric
"""
import numpy as np 
import pandas as pd

person = 'hazel'

def find_missing_work(user):
    # load in the ordering list
    todo = np.loadtxt(".//data//ordering_list_" + user + ".txt", dtype = str, delimiter = " ")  
    
    # load in the work that the person has done
    work = pd.read_csv(".//all_outputs//out_" + user + ".csv", engine = "python"); work.fillna(""); work = np.asarray(work)
    
    # find the last one they did, and curtail 
    last = work[-1][2]
    i = 1
    name = ""
    while (work[-1*i][2] == last):
        n = work[-1*i][1] # temporary name
        if not(n == "Annotator 1"):
            name = n + "," + name
        
        i += 1


    last = name + str(last)
    
    # new ordering list based off of what has been done (in a set)
    supposed_done = set(todo[:np.where(todo == last)[0][0]])
    done = {}
    for row in work:
        if (row[1] == "Annotator 1" or (row[2] in done and row[1] in done[row[2]])):
            continue
        if (row[2] in done): 
            done[row[2]] += row[1] + ","
        else:
            done[row[2]] = row[1] + ","
          
    actually_done = set()
    for k in done.keys():
        actually_done.add(done[k] + str(k))
    
    missing = supposed_done - actually_done
    return missing

users = ["ahmed", "hazel", "daniela"]
todo = set()
for u in users:
    tmp = find_missing_work(u)
    todo = tmp.union(todo)

todo.remove("Lidija,4526")
redoing = set(np.loadtxt("./data/ordering_list_hazel1.txt", dtype = str, delimiter = " ")) 
work = [ x for x in iter(todo - redoing) ]
"""
f = open('./data/ordering_list_' + person + '.txt','ab')
np.savetxt(f, work, delimiter = " ", fmt = "%s")
f.close()

"""
