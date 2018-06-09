import abc
import json
import csv
from pathlib import Path
import pandas as pd
import numpy as np

class Writer(object, metaclass=abc.ABCMeta):
    """Write annotation information.

    A base class for writing annotation information
    out after the article has been annotated by
    the user.
    """

    @abc.abstractmethod
    def submit_annotation(self, id_, annotations):
        """Submits an annotation."""
        raise NotImplementedError('Method `submit_annotation` must be defined')

    @abc.abstractmethod
    def get_results(self):
        """Returns results of project."""
        raise NotImplementedError('Method `get_results` must be defined')


class CSVWriter(Writer):
    """Write to CSV files.

    A `Writer` implementation that writes annotation
    information out to a CSV file. If multiple annotations
    for a single article are provided, they are entered
    in separate columns.

    Writes to CSV in form:
    article_id, annotation1, annotation2, ...
    """

    def __init__(self, write_file):
        self.write_file = write_file
        
    """
    Submit the data to a CSV.
    """
    def submit_annotation(self, data):
        row_heading = ['UserID', 'Doctor Reviewed', 'PromptID', 'XML', 'Valid Prompt',
        'Accept Label', 'Accept Reasoning', 'Outcome', 'Intervention', 'Comparator']
                       
                       
        self.update_user_progress(data['userid'])
                
        path = './/all_outputs//out_{}.csv'.format(data['userid'])
        data = self.__finish_data__(data)
        my_file = Path(path)
        not_file = not(my_file.is_file())
        
        with open(r'' + path, 'a', newline = '', encoding = 'utf-8') as f:
            writer = csv.writer(f)
            if (not_file):
                writer.writerow(row_heading)
                
            for d in data:
                writer.writerow([str(x) for x in d])       

        return None
       
    """
    Call this method when the user has finished annotating something. This 
    incriments the persons progress on work!
    """
    def update_user_progress(self, user):
        user_progress = np.genfromtxt('.//data//user_progress.csv', delimiter = ",", dtype = str)
        user_progress = user_progress.reshape((int(user_progress.size / 2), 2))              
        i = 0
        for row in user_progress:
            if (row[0] == user):
                user_progress[i][1] = str(int(user_progress[i][1]) + 1)
                np.savetxt('.//data//user_progress.csv', user_progress, delimiter = ",", fmt = "%s")
                break
            i += 1
           
        
        return None
    

    def get_results(self):
        with open(self.write_file, 'r') as csvfile:
            lines = csvfile.readlines()
        return '<br><br>'.join(lines)
        
    """
    Goal is to format the data into an array.
    """
    def __finish_data__(self, form):
        userid = form['userid']
        dr = form['Doctors Reviewed'].split(",")
        promptid = form['PromptID']
        xml = form['XML']
        label = json.loads(form["Label"])
        valid_prompt = label['Prompt Validity']
        del label["Prompt Validity"]      
        o = form['Outcome']
        i = form['Intervention']
        c = form['Comparator']
        
        data = []
        dr.insert(0, "Annotator 1")
        for d in dr:
            lab = -1
            res = -1
            for person in label.keys():
                if (d in person and "reasoning" in person):
                    res = label[person]
                if (d in person and "answer" in person):
                    lab = label[person]
                    
            tmp = [userid, d, promptid, xml, valid_prompt, lab, res, o, i, c]            
            data.append(tmp)
                        
        return data
        


class SQLiteWriter(Writer):
    """Write to a SQLite database.

    A `Writer` implementation to support writing
    annotation data out to a database. If multiple
    annotations exist for one Article, they will
    be entered as separate rows in the database.

    Expects columns of form:
    article_id, annotation
    """

    def __init__(self, db_file, table):
        self.db_file = db_file
        self.table = table
        self.conn = sqlite3.connect(self.db_file)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.current_pos = 0

    def submit_annotation(self, id_, annotations):
        for annotation in annotations:
            self.cursor.execute('INSERT INTO {0} VALUES({1}, {2})' \
                                .format(self.table, id_, annotation))
        self.cursor.commit()

    def get_results(self):
        self.cursor.execute('SELECT * FROM {0}'.format(self.table))
        rows = self.cursor.fetchall()
        return json.dumps(rows)


def get_writer(writer):
    options = {
        'csv': CSVWriter,
        'sql': SQLiteWriter,
    }
    if writer in options:
        return options[writer]
    raise Exception('{0} not a valid writer.'.format(writer))
