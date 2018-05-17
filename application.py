import flask
import json

import annotator
import config
import reader
from agreement_statistics import get_stats
import numpy as np


application = flask.Flask(__name__)

anne = annotator.Annotator(reader.get_reader(config.reader)(**config.reader_params))
ordering = np.genfromtxt('.//data//ordering_list.txt', dtype = float)
ordering = np.asarray(ordering, dtype = int)

"""
Display the main page.
"""
@application.route('/', methods=['GET'])
def index():
    artid = ordering[0]
    art = anne.get_next_article(artid)
    doct_reason, doct_ans, doct_ans_names, doctor_names, _ = get_stats(artid)
    return flask.render_template('full_article.html',
                                  id = art.id_,
                                  artid = artid,
                                  tabs = art.text,
                                  outcome = art.get_extra()['outcome'],
                                  intervention = art.get_extra()['intervention'],
                                  comparator = art.get_extra()['comparator'],
                                  ordering = ordering.tolist(),
                                  doct_reason = doct_reason,
                                  doct_ans = doct_ans,
                                  doctor_names = doctor_names,
                                  doct_ans_names = doct_ans_names,
                                  answer = art.get_extra()['answer'], reasoning = art.get_extra()['reasoning'],
                                  options = config.options_full)

"""
Grabs a specified article and displays the full text.
"""
@application.route('/annotate_full/<artid>/', methods=['GET'])
def annotate_full(artid):
    art = anne.get_next_article(artid)
    doct_reason, doct_ans, doct_ans_names, doctor_names, _ = get_stats(artid)    

    return flask.render_template('full_article.html',
                                  id = art.id_,
                                  artid = artid,
                                  tabs = art.text,
                                  outcome = art.get_extra()['outcome'],
                                  intervention = art.get_extra()['intervention'],
                                  comparator = art.get_extra()['comparator'],
                                  ordering = ordering.tolist(),
                                  doct_reason = doct_reason,
                                  doct_ans = doct_ans,
                                  doctor_names = doctor_names,
                                  doct_ans_names = doct_ans_names,
                                  answer = art.get_extra()['answer'], reasoning = art.get_extra()['reasoning'],
                                  options = config.options_full)

"""
Run the application.
"""
if __name__ == '__main__':
    application.run(port = 8084, host = '0.0.0.0')
