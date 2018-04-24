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
        last_split = 0
        name = data[loc_art][0]
        print(data[loc_art][2])
        data[loc_art][2] = data[loc_art][2][2:-2]
        data[loc_art][2] = to_js(data[loc_art][2])
        all_commas = [m.start() for m in re.finditer(",", data[loc_art][2])]
        # for every comma location 
        for cl in all_commas:
            if (cl + 1 < len(data[loc_art][2]) and cl - 1 > 0 and data[loc_art][2][cl - 1] != " " and data[loc_art][2][cl + 1] != " "):
                doctor_answer_for_loc_art.append([name, data[loc_art][2][:cl]])
                last_split = cl
            
        if (len(all_commas) == 0 or last_split == 0):
            doctor_answer_for_loc_art.append([name, data[loc_art][2]])
        else:
            doctor_answer_for_loc_art.append([name, data[loc_art][2][(last_split+1):]])
       
    """
    new_ans = []
    for data in doctor_answer_for_loc_art:
        name = data[0]
        txt = data[1]
        all_loc_o = [m.start() for m in re.finditer('\(', txt)]
        all_loc_c = [m.start() for m in re.finditer('\)', txt)]
        for i in range(len(all_loc_o)):
            new_ans.append([name, txt[:all_loc_o[i]]])
            new_ans.append([name, txt[all_loc_o[i]:all_loc_c[i] + 1]])
            
        new_ans.append([name, txt])
        
        import pdb; pdb.set_trace()
    """
        
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
        key = "".join(row[4].split(" ")) + "".join(row[5].split(" ")) + "".join(row[6].split(" ")) + row[1]
        # if we haven't seen this one yet, add it to the ordering of articles
        if not(key in have_seen):
            ordering.append(key)
                        
            
        have_seen.add(key)
        option = row[2]
        reason = row[3]
        data[key] = [option, reason]  
        i += 1            
    
    res_option = []
    res_ans = []
    i = 0
    for o in ordering:
        res_option.append(np.append([name, i], data[o][0]))
        res_ans.append(np.append([name, i], data[o][1]))
        i += 1
        
    return res_option, res_ans


"""
Extract the answers and convert to integers.
"""               
def load_data(data_loc):        
    data_option = []
    data_ans = []

    for loc in data_loc:
        df = np.asarray(pd.read_csv(loc, encoding = 'utf-8'))
        df_opt, df_ans = remove_duplicate(loc[13:-4], df) # hard-coded
        data_option.append(df_opt)
        data_ans.append(df_ans)
     
    return data_option, data_ans 


"""
Helper function that flattens the list.
"""
def flatten(data_opt, data_ans):
    options = []
    answers = []
    
    # flatten all the lists
    for i in range(len(data_opt)):
        for j in range(len(data_opt[i])):
            options.append(data_opt[i][j])
            
        for j in range(len(data_ans[i])):
            answers.append(data_ans[i][j])
            
    return options, answers
 
"""
Loads in the answers.
"""   
def load_answers():
    location = './/data//for-full-text-annotation.csv'
    df = np.asarray(pd.read_csv(location, encoding = 'utf-8'))
    data = {}
    for f in df:
        data[f[0]] = f[10]
        
    return data

"""
Determines if the answer is the same as the guess.
"""
def is_same(guess, ans):
    first = {'sig diff, pos': 1, 'sig diff, neg': 2, 'no sig diff': 3}.get(ans, -1)

    second = {"b'Significantly increased'": 1,
              "b'Significantly decreased'": 2, 
              "b'No significant difference'": 3, 
              "b'Invalid Prompt'": 4}.get(guess, -1)
    
    if (second == -1 or first == -1):
        import pdb; pdb.set_trace()
   
    if (first == second):
        return 1
    else:
        return 0
   
def find_number_correct(data, answers, ordering):
    right_or_wrong = []
    i = 0

    for art in ordering:
        ans = answers[art] # get the answer for this file
        guess = data[i][2] # it is in the format of [name, # art, answer]
        is_cor = is_same(guess, ans) # determine if they are the same
        right_or_wrong.append(is_cor) # add this to our list
        
        # add this to the global agreement variable
        if art in doctor_agreement:
            doctor_agreement[int(float(art))].append([data[i][0], guess])
        
        else:
            doctor_agreement[int(float(art))] = [[data[i][0], guess]]
            
        i += 1

            
                            # number in total - # you got right
    return right_or_wrong, len(right_or_wrong) - np.sum(right_or_wrong), ans
    
def get_stats(art_id):
    global doctor_agreement               
    doctor_agreement = {}
    data_loc = ['.//data//out_lidija.csv', './/data//out_edin.csv',
                './/data//out_milorad.csv', './/data//out_sergii.csv',
                './/data//out_krystie.csv']    
                           
    # has all information for all files
    names = np.genfromtxt('.//data//ordering_list.txt', dtype = float)
    names = np.asarray(names, dtype = int)
    loc_art = names.tolist().index(float(art_id))
    data_opt, data_ans = np.asarray(load_data(data_loc))
    options, answers = flatten(data_opt, data_ans)
    ans_dict = load_answers()
    
    all_doctor_res = [] # a list of which ones were missed and hit
    num_missed = [] # a list of how many records each doctor missed
    answer = -1
    for doctor in data_opt: # for each doctor
        # get their results - an array of 0's or 1's if they got it right, and the number missed
        return_val = find_number_correct(doctor, ans_dict, names)
        all_doctor_res.append(return_val[0])
        num_missed.append(return_val[1])
        answer = return_val[2]
        
        
    # the columns = # of people who got the answer wrong   
    how_many_correct = np.sum(all_doctor_res, axis = 0)
    num_missed = list(map((lambda i: [data_loc[i][13:-4], str(len(names) - num_missed[i]) + '/' + str(len(names))]), range(len(data_loc))))    
    doctor_names = list(map(lambda i: data_loc[i][13:-4].capitalize(), range(len(data_loc))))
    
    
    # The texts highlighted:  
    doctor_answer_for_loc_art = format_doct_answer(data_ans, loc_art)              
        
    
    # get stats for the selected options
    task = nltk.agreement.AnnotationTask(data=options)

    # get stats for the reasoning
    task1 = nltk.agreement.AnnotationTask(data=answers)
    
    """
    print("How many correct: {}".format(how_many_correct))
    print("Performance: {}".format(num_missed))   
    print("Achieving agreeing values for options: {}".format(np.round(task.alpha(), 3)))
    print("Achieving agreeing values for reasoning: {}".format(np.round(task1.alpha(), 3)))        
    """  
        
    #print(doctor_agreement[int(names[loc_art])])

    doct_answer = doctor_agreement[int(float(names[loc_art]))]
    data = {}
    all_answers = set()
    i = 0
    for d in doct_answer:
        ans = d[1][2:-1] # fix without "b' and '"
        doct_answer[i][1] = ans
        doct_answer[i][0] = str(doct_answer[i][0]).capitalize()
        all_answers.add(ans)
        if ans in data:
            data[ans] = data[ans] + 1
        else:
            data[ans] = 1
         
        i += 1

    doct_answer_n_names = [['Doctor Answer', 'Occurances']]
    for ans in all_answers:
          doct_answer_n_names.append([ans, data[ans]])   
          
    return doctor_answer_for_loc_art, doct_answer_n_names, doct_answer, doctor_names, answer

