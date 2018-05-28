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
banned = [16, 17, 18, 32]
loc_ban = set()
names = np.genfromtxt('.//data//ordering_list.txt', dtype = float)
for lb in banned:
    loc_ban.add(np.where(lb == names)[0][0])


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
        key = "".join(row[4].split(" ")) + "".join(row[5].split(" ")) + "".join(row[6].split(" ")) + str(row[1])
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
        if not(i in loc_ban):
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
        # THIS IS WHERE THE NAMES COME FROM
        df_opt, df_ans = remove_duplicate(loc[12:-4].capitalize(), df) 
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
    ordering = np.genfromtxt('.//data//ordering_list.txt', dtype = int)
    df = np.asarray(pd.read_csv('.//data//prompt_gen.csv', encoding = 'utf-8'))
    opt = [None] * (len(ordering))
    n = -1
    options = []
    for i in ordering:
        n += 1

        if (i in banned):
            continue
        
        opt[n] = df[i - 1][5]
        
    opt = [x for x in opt if x is not None]
    options.extend(opt)
    
    return options

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
Get the correct number of correct answers.
"""   
def find_number_correct(data, answers):
    accuracy = {} # mapping of doctors -> num-correct
    answer_loc = np.full((len(answers,),), 0) # array of len(articles) -> keeps track of how many right
    names = []
    
    i = 0
    last_doctor = ""
    for d in data:
        name = d[0]
        guess = d[2]
        if (last_doctor == ""):
            accuracy[name] = 0
            names.append(name)
        
        if (last_doctor != "" and last_doctor != name):
            i = 0
            accuracy[name] = 0
            names.append(name)

        is_correct = is_same(guess, answers[i])
        accuracy[name] += is_correct
        answer_loc[i] += is_correct   
        i += 1
        last_doctor = name
            
    # number in total - # you got right
    return accuracy, answer_loc, names

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
Specifically adds my data to the bunch.
"""
def add_eric_option(options, answers):
    ordering = np.genfromtxt('.//data//ordering_list.txt', dtype = int)
    df = np.asarray(pd.read_csv('.//data//prompt_gen.csv', encoding = 'utf-8'))
    opt = [None] * (len(ordering))
    ans = [None] * (len(ordering))
    n = -1
    for i in ordering:
        n += 1

        if (i in banned):
            continue
        
        opt[n] = np.asarray(['Eric', str(n), df[i - 1][5]])
        ans[n] = np.asarray(['Eric', str(n), df[i - 1][6]])
        
    opt = [x for x in opt if x is not None]
    ans = [x for x in ans if x is not None]
    options.extend(opt)
    answers.extend(ans)
    return options, answers   
    
def get_stats(art_id):
    art_id = int(art_id)
    global doctor_agreement               
    doctor_agreement = {}
    data_loc = glob.glob('.//data//*.csv')
    
    try:
        data_loc.remove('.//data\\for-full-text-annotation.csv')
        data_loc.remove('.//data\\prompt_gen.csv')
        #data_loc.remove('.//data\\out_lidija.csv')
        #data_loc.remove('.//data\\out_edin.csv')
        #data_loc.remove('.//data\\out_milorad.csv')
    except:
        data_loc.remove('.//data/for-full-text-annotation.csv')
        data_loc.remove('.//data/prompt_gen.csv')
        
                           
    # has all information for all files
    names = np.genfromtxt('.//data//ordering_list.txt', dtype = float)
    names = np.asarray(names, dtype = int)
    data_opt, data_ans = np.asarray(load_data(data_loc))
    options, answers = flatten(data_opt, data_ans) 
    
    accuracy, answer_loc, doct_name = find_number_correct(options, load_answers())
        
    # Add in my answers from prompt gen
    options, answers = add_eric_option(options, answers)
    options = convert_answer_to_num(options)                   
    
    # get stats for the selected options
    task = nltk.agreement.AnnotationTask(data=options)

    # get stats for the reasoning
    task1 = nltk.agreement.AnnotationTask(data=answers)
    
    how_many_correct = "\n"
    for doc in accuracy.keys():
        how_many_correct += doc + ": " + str(accuracy[doc]) + "/" + str(len(answer_loc)) + "\n"
    
    print("How many correct: {}".format(how_many_correct))
    print("Achieving agreeing values for options: {}".format(np.round(task.alpha(), 3)))
    print("Achieving agreeing values for reasoning: {}".format(np.round(task1.alpha(), 3)))        
    
    doct_reason = []
    doct_ans = []
    doct_ans_dict = {} # dictionary of answers to numbers (frequency)
    i = 0
    # for each article, check if it is equal to the article id given
    for n in names:
        # skip if banned
        if (n in banned):
            continue
        
        # if it is equal to the article id given
        if (n == art_id):
            # loop over all the dcotors
            for j in range(len(data_opt)):
                # append the doctor name and the doctor answer
                doct_reason.append([data_ans[j][i][0], data_ans[j][i][2]])
                doct_ans.append([data_opt[j][i][0], convert_num_to_answer(data_opt[j][i][2])])
                # put into a dictionary to find frequency of answers
                if (data_opt[j][i][2] in doct_ans_dict):
                    doct_ans_dict[data_opt[j][i][2]] += 1
                else: 
                    doct_ans_dict[data_opt[j][i][2]] = 1
            
        i += 1
    
    # put into a format of Array-of [option, frequency]
    doct_ans_freq = [['Option', 'Frequency']]
    for key in doct_ans_dict.keys():
        doct_ans_freq.append([{'1': "Significantly Increased",
                          '2': "Significantly Decreased",
                          '3': "No Significant Difference",
                          '4': "Invalid Prompt"}.get(key, -1), doct_ans_dict[key]])        
     
    return doct_reason, doct_ans_freq, doct_ans, doct_name 

get_stats(82)
