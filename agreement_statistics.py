# -*- coding: utf-8 -*
"""
Created on Fri Apr 13 09:11:36 2018

@author: Eric
"""

#!/usr/bin/env python
import pandas as pd
import numpy as np
import nltk
import re
import codecs
import glob
 
global doctor_agreement               
doctor_agreement = {}

"""
Conver to a javascript string format for special characters.
< = &lt;
> = &gt;

Attempt 1: #string.replace("\\xe2\\x80\\x93", "–").replace("\xe2\x80\x8a", " ")
Attempt 2: string.encode('utf-8').decode('ascii', 'ignore') 
Attempt 3: string.encode('latin1').decode('utf-8')
"""
def to_js(string): # \\xe2\\x80\\x93
    return codecs.decode(string, 'unicode_escape').encode('latin1').decode('utf-8', "replace")
    
def format_doct_answer(data_ans, loc_art):
    doctor_answer_for_loc_art = []
    last_split = 0

    for data in data_ans:
        last_split = -1
        name = data[loc_art][0]
        data[loc_art][2] = data[loc_art][2]
        data[loc_art][2] = to_js(data[loc_art][2])
        all_commas = [m.start() for m in re.finditer(",", data[loc_art][2])]
        i = 0
        # for every comma location 
        for cl in all_commas:
            if (cl + 1 < len(data[loc_art][2]) and cl - 1 > 0 and data[loc_art][2][cl - 1] != " " and data[loc_art][2][cl + 1] != " "):
                doctor_answer_for_loc_art.append([name + str(i), data[loc_art][2][(last_split + 1):cl]])
                last_split = cl
                i += 1
            
        if (len(all_commas) == 0 or last_split == 0):
            doctor_answer_for_loc_art.append([name, data[loc_art][2]])
        else:
            doctor_answer_for_loc_art.append([name, data[loc_art][2][(last_split+1):]])
       
    
    return doctor_answer_for_loc_art
    
"""
Remove duplicates/the 'Cannot tell based on the abstract' - get only the answer.
"""
def remove_duplicate(name, df):
    data = {}
    ordering = []
    have_seen = set()
    i = 0
    for row in df:
        key = row[1]
        # if we haven't seen this one yet, add it to the ordering of articles
        if not(key in have_seen):
            ordering.append(key)
                     
        have_seen.add(key)
        option = str(row[3]).encode('utf-8').decode('utf-8')
        reason = str(row[4]).encode('utf-8').decode('utf-8')
        data[key] = [option, reason]  
        i += 1            
    
    res_option = []
    res_ans = []
    for o in ordering:
        res_option.append(np.append([name, o], data[o][0]))
        res_ans.append(np.append([name, o], data[o][1]))
        
        if (data[o][0] == "Cannot tell based on the abstract"):
            import pdb; pdb.set_trace()
        
        i += 1
       
    return res_option, res_ans


"""
Extract the answers and convert to integers.
"""               
def load_data(data_loc):        
    data_option = []
    data_ans = []

    for loc in data_loc:
        df = np.asarray(pd.read_csv(loc, engine='python'))
        # THIS IS WHERE THE NAMES COME FROM
        df_opt, df_ans = remove_duplicate(loc[13:-4].capitalize(), df) 
        data_option.append(df_opt)
        data_ans.append(df_ans)
        
        
    return data_option, data_ans 

"""
Determines if the answer is the same as the guess.
"""
def is_same(guess, ans):
    first = {"significantly increased": 1,
             "significantly decreased": 2,
             "no significant difference": 3,
             "invalid prompt": 4}.get(ans.lower(), -1)

    second = {"significantly increased": 1,
              "significantly decreased": 2,
              "no significant difference": 3,
              "invalid prompt": 4}.get(guess.lower(), -1)
    
    if (second == -1 or first == -1):
        import pdb; pdb.set_trace()
   
    if (first == second):
        return 1
    else:
        return 0


"""
Arr is an array of -> [NAME, NUMBER, MC-GUESS]
"""
def convert_answer_to_num(arr):
    for guess in arr:
        second = {"significantly increased": 1,
                  "significantly decreased": 2,
                  "no significant difference": 3,
                  "invalid prompt": 4}.get(guess[2].lower(), -1)
                  
        guess[2] = second
    return arr

"""
Given a key, convert back to a string
"""
def convert_num_to_answer(key):
    return {'1': "Significantly Increased",
            '2': "Significantly Decreased",
            '3': "No Significant Difference",
            '4': "Invalid Prompt"}.get(key, -1)
            
            
"""
Loads the names of the ordering in which the person did work.
"""
def load_names(user):
    old = np.genfromtxt('.//data//first_ordering_list.txt', dtype = float)
    names = np.genfromtxt('.//data//ordering_list_' + user.lower() + '.txt', dtype = float)
    names = np.asarray(np.append(old, names), dtype = int)
    
    seen = set()
    n = []
    # remove duplicates
    #for i in range(len(names) - 1, -1, -1):
    for i in range(len(names)):
        if (names[i] in seen):
            continue
        else:
            n.append(names[i])
            seen.add(names[i])
            
    return n
    
"""
The main function. Also calculates the statistics of the dataset in the 
process.
"""
def get_stat(art_id, user):
    art_id = int(art_id)
    global doctor_agreement               
    doctor_agreement = {}
    tmp_loc = ".//data//"
    data_loc = []
    data_loc.append(tmp_loc + "out_" + user.lower() + ".csv") 
        
    data_opt, data_ans = np.asarray(load_data(data_loc))
    
    doct_reason = []
    doct_ans = []
    doct_ans_dict = {} # dictionary of answers to numbers (frequency)
    
    for j in range(len(data_opt)):
        for i in range(len(data_ans[j])):
            if (int(data_ans[j][i][1]) == art_id):
                # append the doctor name and the doctor answer
                doct_reason.append([data_ans[j][i][0], data_ans[j][i][2]])
                doct_ans.append([data_opt[j][i][0], data_opt[j][i][2]])
                # put into a dictionary to find frequency of answers
                if (data_opt[j][i][2] in doct_ans_dict):
                    doct_ans_dict[data_opt[j][i][2]] += 1
                else: 
                    doct_ans_dict[data_opt[j][i][2]] = 1


    
    # put into a format of Array-of [option, frequency]
    doct_ans_freq = [['Option', 'Frequency']]
    for key in doct_ans_dict.keys():
        doct_ans_freq.append([key, doct_ans_dict[key]])
             
    return doct_reason, doct_ans_freq, doct_ans, [user]

#print(get_stats(82, "Lidija"))