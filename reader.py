import abc
import csv
import os
import glob
import random
import sqlite3
import xml.etree.ElementTree as ET
import numpy as np
from functools import reduce
import article
import pandas as pd 
import ftfy

class Reader(object, metaclass=abc.ABCMeta):
    """Read article information.
    A base class for providing article information
    to be annotated by the user.
    """

    @abc.abstractmethod
    def get_next_article(self):
        """Gets the next article to be annotated."""
        raise NotImplementedError('Method `get_next_article` must be defined')

class XMLReader(Reader):
    """Read from XML files.
    A `Reader` implementation to read articles from XML files
    that are stored in a given path. Currently expects files to
    be of the form of an NLM article.
    """

    def __init__(self, path):
        self.path = path
        
    def _get_user_progress_(self, user):
        f = 'data/progress/{}.progress'.format(user)
        if not(os.path.exists(f)):
            with open(f, 'w') as tmp:
                tmp.write(str(0))
                
        with open(f) as tmp:
            return int(tmp.read())
        
    def _get_next_file(self, user):
        """ Which file to work on next. """
        up = self._get_user_progress_(user)
        with open('data/order/{}.order'.format(user)) as tmp:
            files = tmp.read().split('\n')[:-1]
        
        next_file = files[up] if len(files) > up else None
        if next_file is None: return None, None
        df = pd.read_csv('data/prompt_gen_data/prompts_merged.csv')
        pmc = df[df['PromptID'] == int(next_file)]['PMCID'].values[0]
        
        return next_file, pmc
            
    def _get_PMC_id(self, article_meta):
        ids = article_meta.findall('article-id')
        id_ = None # the number associated with the xml
        for id in ids:
            if 'pub-id-type' in id.attrib and id.attrib['pub-id-type'].lower() == 'pmc':
                id_ = id.text
                break
        
        return id_

    def _get_title(self, article_meta):
        # grab the title and the text
        title_xml = article_meta.find('title-group').find('article-title') 
        title = ET.tostring(title_xml, encoding='utf8', method='text').decode('utf-8') 
        return title
    
    def _get_sections(self, body):
        """
        Return the article split into sections. It will return an array of pairs, 
        with a given pair having a first entry of the title, and the second entry
        containing the actual text of that section.    
        """
        arr = []
        title = ""
        paragraph = ""
        children = body.getchildren()
        for i in range(len(children)):
            child = children[i]
            if (child.tag == 'sec'):
                sub_sec = self._get_sections(child)
                arr.append(sub_sec)
            elif (child.tag == 'title'):
                title = ET.tostring(child, method = 'text', encoding = 'utf8').decode('utf-8')
            else:
                paragraph += ET.tostring(child).decode('utf-8')
                
        if (title == '' and len(arr) > 0):
            return arr
        elif (len(arr) > 0):
            return [title, arr]
        else:
            return [title, paragraph]
    
    def _get_abstract_(self, article_meta):
        """ Get the abstract from the article meta """ 
        try:
            temp = article_meta.find('abstract')
            if (temp is None):
                abstract = []
            else:   
                abstract_sections = self._get_sections(temp)
                abstract = []        
                for part in abstract_sections:
                    abstract.append([part[0], ET.tostring(part[1]).decode('utf-8')])
        except:
            lop = article_meta.find('abstract').findall('p')
            abstract = reduce((lambda x, y: ''.join([x, ET.tostring(y).decode('utf-8')])), lop, "")        
            if abstract == '': abstract = ET.tostring(article_meta.find('abstract')).decode('utf-8')
    
        return article_meta 
        
    def _get_annotator_answer_(self, prompt):
        """ @return the answer given by an annotator. """
        df_locs = glob.glob('./data/annotator_data/*.csv') 
        for l in df_locs:
            df = pd.read_csv(l)
            row = df[df['ID'] == int(prompt)]
            if len(row) != 0:
                row = row.iloc[0]
                return {'reason': row['Selected Text'],
                        'answer': row['Label'] if row['Label'] != '' else 'Invalid Prompt',
                        'offset': [[row['Start'], row['End']]]}
                
        return None
        
    def _get_prompt_(self, prompt):
        """ @return the prompt generated, and the answer given. """
        df = pd.read_csv('./data/prompt_gen_data/prompts_merged.csv')
        df_ans = pd.read_csv('./data/prompt_gen_data/out_sergii.csv')
        df_ans = df_ans.fillna('')
        row = df[df['PromptID'] == int(prompt)].iloc[0]
        
        # these are still flipped by accident (in out_sergii)
        cmp, out, itv = row['Intervention'], row['Outcome'], row['Comparator']
        row_ans = df_ans[(df_ans['Intervention'] == itv) & 
                         (df_ans['Outcome'] == out) & 
                         (df_ans['Comparator'] == cmp)].iloc[0]
        
        # flip them back here. 
        return {'intervention': ftfy.fix_text(cmp),
                'outcome': ftfy.fix_text(out), 
                'comparator': ftfy.fix_text(itv),
                'reason': ftfy.fix_text(row_ans['Reasoning']),
                'answer': ftfy.fix_text(row_ans['Answer']),
                'offset': [[int(x) if x.isdigit() else 0 for x in row_ans['xml_offsets'].split(':')]]}
        
    def _fix_text_(self, text):
        new_text = []
        for t in text:
            name = t[0]
            parsed_text = t[1]
            if type(parsed_text) == list:
                parsed_text = self._fix_text_(parsed_text)
            elif type(parsed_text) != str:
                parsed_text = ET.tostring(parsed_text).decode('utf-8')
            
            new_text.append([name, parsed_text])
            
        return new_text
        
    def _init_article_(self, next_file, article_meta, body):
        """
        Initialize the article to have the proper fields and extra information.
        """
        title = self._get_title(article_meta)
        pmc_tag = self._get_PMC_id(article_meta)
        abstract = self._get_abstract_(article_meta)
         
        if not(body is None):
            text = self._get_sections(body) 
            text.insert(0, ['Abstract', abstract])
        else:
            text = [['Abstract', abstract]]
            
        # store the path of this file
        text = self._fix_text_(text)
        art = article.Article(id_= next_file, title=title, text=text)
        prompt_info = self._get_prompt_(next_file)
        annotator_info = self._get_annotator_answer_(next_file)
        art.get_extra()['PMC']          = pmc_tag
        art.get_extra()['path']         = next_file
        art.get_extra()['outcome']      = prompt_info['outcome']
        art.get_extra()['comparator']   = prompt_info['comparator']
        art.get_extra()['intervention'] = prompt_info['intervention']
        art.get_extra()['reasoning']    = [prompt_info['reason'], annotator_info['reason']]
        art.get_extra()['answer']       = [prompt_info['answer'], annotator_info['answer']]
        art.get_extra()['offsets']      = prompt_info['offset'] + annotator_info['offset']
        
        #art.text = self._add_text_spans_(pmc_tag, art.get_extra()['offsets'], art.get_extra()['reasoning'])
        return art
    
    def get_next_article(self, user, next_file=None):
        """ Create a structured file of the document specified or for that user. """
        next_file, pmc = next_file or self._get_next_file(user) 
        if next_file is None: return None          
        
        path_to_file =  self.path + '/PMC' + str(pmc) + '.nxml' # the path to XML files
        et = ET.parse(path_to_file) 
        root = et.getroot() 
        
        front = root.find('front')
        article_meta = front.find('article-meta')
        body = root.find('body')

        art = self._init_article_(next_file, article_meta, body)
        return art

def get_reader(reader):
    options = {
        'xml': XMLReader
    }
    if reader in options:
        return options[reader]
    raise Exception('{0} not a valid reader.'.format(reader))
    
