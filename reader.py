import abc
import csv
import os
import random
import sqlite3
import xml.etree.ElementTree as ET
from data.by_row_description import by_row_description
import numpy as np
from functools import reduce


import article


class Reader(object, metaclass=abc.ABCMeta):
    """Read article information.
    A base class for providing article information
    to be annotated by the user.
    """

    @abc.abstractmethod
    def get_next_article(self):
        """Gets the next article to be annotated."""
        raise NotImplementedError('Method `get_next_article` must be defined')


class CSVReader(Reader):
    """Read from CSV files.
    A `Reader` implementation to support reading article data
    from a CSV file. Uses a buffer to preload a preset number
    of articles to speed up accessing the next article.
    """

    '''
    @param read_file represents a csv file location
    '''
    def __init__(self, read_file, buffer_size=None):
        self.read_file = read_file

        self.buffer = []
        self.current_pos = 0
        if not buffer_size:
            with open(self.read_file, 'r') as csvfile:
                lines = csv.DictReader(csvfile)
                file_length = sum(1 for line in lines)
                buffer_size = max(file_length // 10, 100)
        self.buffer_size = buffer_size
        self._add_to_buffer()
        import pprint; pprint.pprint(self.buffer)
        
    def _add_to_buffer(self):
        with open(self.read_file, 'r') as csvfile:
            lines = csv.DictReader(csvfile)
            for i, line in enumerate(lines):
                if i < self.current_pos:
                    continue
                self.current_pos += 1
                self.buffer.append(line)

    def get_next_article(self):
        if not self.buffer:
            self._add_to_buffer()
        try:
            entry = self.buffer.pop(0)
        except IndexError:
            # we have gone through the entire file
            return None
        return article.Article(id_=entry['id'],
                               title=entry['title'],
                               text=entry['text'])


class SQLiteReader(Reader):
    """Read from a SQLite database.
    A `Reader` implementation to read articles from
    a SQLite database. Requires that there exist columns
    titled 'title' and 'text' and that the rows are
    uniquely id'd beginning at 0.
    """

    def __init__(self, db_file, table):
        self.db_file = db_file
        self.table = table
        self.conn = sqlite3.connect(self.db_file)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.current_pos = 0

    def get_next_article(self):
        self.cursor.execute('SELECT title, text FROM {0} WHERE id={1}' \
                            .format(self.table, self.current_pos))
        articles = self.cursor.fetchall()
        if not articles or len(articles) != 1:
            return None
        art = article.Article(id_=self.current_pos,
                              title=articles[0][0],
                              text=articles[0][1])
        self.current_pos += 1
        return art


class XMLReader(Reader):
    """Read from XML files.
    A `Reader` implementation to read articles from XML files
    that are stored in a given path. Currently expects files to
    be of the form of an NLM article.
    """

    def __init__(self, path):
        self.path = path
        self.by_row_description = by_row_description()

        
    """
    Given the path that leads to a folder of ONLY XML files, the function
    will pick one and then return the name of it.
    """
    def _get_next_file_random(self):
        try:
            paths = os.listdir(self.path)
            if ('desktop.ini' in paths): # issue with internal works of windows
                paths.remove('desktop.ini')
            next_file = random.choice(paths)
        except IndexError as _:
            # Provided path has no files
            return None
        return next_file
        
    """
    Given the path that leads to a folder of ONLY XML files, the function
    will pick one and then return the name of it.
    """
    def _get_next_file(self, user):
        user_progress = np.genfromtxt('.//data//user_progress.csv', delimiter = ",", dtype = str)
        user_progress = user_progress.reshape((int(user_progress.size / 2), 2))      
        ordering = np.loadtxt('.//data//ordering_list_' + user + '.txt', dtype = str)
        

        # Find which to take in the user progress if possible
        i = 0
        for row in user_progress:
            row_val = int(float(row[1]))
            if (row[0] == user and len(ordering) > row_val):
                return ordering[row_val] # return their ordering here if we find it
            elif (row[0] == user and not(len(ordering) > row_val)):
                return None
            i += 1
           
        user_progress = user_progress.tolist()
        user_progress.append([user, 0])
        np.savetxt('.//data//user_progress.csv', np.asarray(user_progress), delimiter = ",", fmt = "%s")
        return ordering[0]
        
    """
    Return the proper ids associated with this specific XML file.
    
    @param article_meta is the XML element that holds the article title.
    """
    def _get_PMC_ids(self, article_meta):
        ids = article_meta.findall('article-id')
        id_ = None # the number associated with the xml
        for id in ids:
            if 'pub-id-type' in id.attrib and id.attrib['pub-id-type'].lower() == 'pmc':
                id_ = id.text
        
        return id_
    
    
    """
    Return the proper ids associated with this specific XML file.
    
    @param article_meta is the XML element that holds the article title.
    """
    def _get_ids(self, article_meta):
        ids = article_meta.findall('article-id')
        id_ = None # the number associated with the xml
        for id in ids:
            if 'pub-id-type' in id.attrib and id.attrib['pub-id-type'].lower() == 'pmc':
                id_ = id.text
        
        return id_
    
    
    """
    Return the title of the article.
    
    @param article_meta is the XML element that holds the article title.
    """
    def _get_title(self, article_meta):
        # grab the title and the text
        title_xml = article_meta.find('title-group').find('article-title') 
        title = ET.tostring(title_xml, encoding='utf8', method='text').decode('utf-8') 
        return title
    
    """
    Return the article split into sections. It will return an array of pairs, 
    with a given pair having a first entry of the title, and the second entry
    containing the actual text of that section.
    
    @param body represents the whole article.
    """
    def _get_sections(self, body):
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
         
    
    """
    Return all of the text in an XML file.
    
    @param body represents the main portion of the XML with the data.
    """
    def _get_full_text(self, body):
        text = ET.tostring(body).decode('utf-8')
        return text

        
    """
    Initialize the article to have the proper fields and extra information.
    """
    def _init_article_(self, next_file, article_meta, body):
        id_ = self._get_ids(article_meta)
        title = self._get_title(article_meta)
        pmc_tag = self._get_PMC_ids(article_meta)
        pmid = self._get_ids(article_meta)
        try:
            temp = article_meta.find('abstract')
            if (temp is None):
                abstract = []
            else:   
                abstract_sections = self._get_sections(temp)
                abstract = []        
                for part in abstract_sections:
                    abstract.append([part[0], part[1]])
        except:
            lop = article_meta.find('abstract').findall('p')
            abstract = reduce((lambda x, y: ''.join([x, ET.tostring(y).decode('utf-8')])), lop, "")        
            if abstract == '':
                abstract = ET.tostring(article_meta.find('abstract')).decode('utf-8')
            
                   
        if not(body is None):
            text = self._get_sections(body) #self._get_full_text(body)
            text.insert(0, ['Abstract', abstract])
        else:
            text = [['Abstract', abstract]]
            
        # store the path of this file
        art = article.Article(id_= id_, title=title, text=text)
        art_data = self.by_row_description[int(next_file)][0]
        art.get_extra()['path'] = next_file
        
        try:
            art.get_extra()['outcome'] = art_data['Outcome'].encode('cp1252').decode('utf-8')
        except:
            art.get_extra()['outcome'] = art_data['Outcome']
            
        try:
            art.get_extra()['comparator'] = art_data['Comparator'].encode('cp1252').decode('utf-8')
        except:
            art.get_extra()['comparator'] = art_data['Comparator']
            
        try: 
            art.get_extra()['intervention'] = art_data['Intervention'].encode('cp1252').decode('utf-8')
        except:
            art.get_extra()['intervention'] = art_data['Intervention']
            
        try:
            art.get_extra()['reasoning'] = art_data['Reasoning'].encode('cp1252').decode('utf-8')
        except:
            art.get_extra()['reasoning'] = art_data['Reasoning']
            
        art.get_extra()['answer'] = art_data['Answer']
        art.get_extra()['PMC'] = pmc_tag
                        
        # only get the abstract if the next_file is None or it doesn't exist
        if (not(abstract is None) and not(next_file is None)):
            art.get_extra()['abstract'] = abstract # add the abstract in  
            
        return art
    
    """
    Grabs a random XML article and displays it.
    If the next_file is not equal to 'None', then it will grab the full article.
    Otherwise, it will only display the abstract.
    """
    def get_next_article(self, user, next_file=None):
        # next file is in the form of "Person,...Person,Number".
        # there must be at least 1 person
        next_file = next_file or self._get_next_file(user) 
        if not next_file:
            return None
            
        arr = next_file.split(",")
        next_file = arr[-1]
        users = arr[:-1]            
        
        pmc = self.by_row_description[int(next_file)][0]['XML']
        path_to_file =  self.path + '//PMC' + str(pmc) + '.nxml' # the path to XML files
        et = ET.parse(path_to_file) 
        root = et.getroot() 
        
        front = root.find('front')
        article_meta = front.find('article-meta')
        body = root.find('body')

        art = self._init_article_(next_file, article_meta, body)
        return art, users
        

"""
Builder pattern for readers.
"""
def get_reader(reader):
    options = {
        'csv': CSVReader,
        'sql': SQLiteReader,
        'xml': XMLReader
    }
    if reader in options:
        return options[reader]
    raise Exception('{0} not a valid reader.'.format(reader))
    