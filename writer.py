import abc
import json
import csv
import os
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
        
    def _create_out_file_(self, user_id):
        """ Create an output file for this user if it doesn't exist """
        f = 'all_outputs/{}.csv'.format(user_id)
        row_heading = ['UserID', 'Doctor Reviewed', 'PromptID', 'XML', 'Valid Prompt', 'Accept Label', 'Accept Reasoning']
        if not(os.path.exists(f)):
            df = pd.DataFrame(columns = row_heading)
            df.to_csv(f, index = False)
            
    """
    Submit the data to a CSV.
    """
    def submit_annotation(self, data):
        self._create_out_file_(data['userid'])
        labels  = json.loads(data['Label'])
        valid_p = labels['Prompt Validity']
        path = 'all_outputs/{}.csv'.format(data['userid'])
        df = pd.read_csv(path)
        for i, d in enumerate(labels.keys()):
            if not('annotator' in d.lower()): continue
            df = df.append({'UserID': data['userid'],
                            'Doctor Reviewed': d,
                            'PromptID': data['PromptID'],
                            'XML': data['XML'],
                            'Valid Prompt': valid_p,
                            'Accept Label': labels[d][0],
                            'Accept Reasoning': labels[d][1]}, 
                        ignore_index=True)
        
        df.to_csv(path, index = False)        
        self.update_user_progress(data['userid'])
        return None
       
    def update_user_progress(self, user):
        f = './data/progress/{}.progress'.format(user)
        with open(f) as tmp: idx = int(tmp.read())
        with open(f, 'w') as tmp: tmp.write(str(idx + 1))
        
def get_writer(writer):
    options = {
        'csv': CSVWriter,
    }
    if writer in options:
        return options[writer]
    raise Exception('{0} not a valid writer.'.format(writer))
