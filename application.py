import flask
import writer

import annotator
import config
import reader
import numpy as np
from functools import reduce
from flask import jsonify


application = flask.Flask(__name__)

anne = annotator.Annotator(reader.get_reader(config.reader)(**config.reader_params),
                           writer.get_writer(config.writer)(**config.writer_params))

@application.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')
    
@application.route('/finish/', methods=['GET'])
def finish():
    return flask.render_template('finish.html')
    
@application.route('/annotate_full/<userid>/', methods=['GET', 'POST'])
def annotate_full(userid):
    """
    Grabs a specified article and displays the full text.
    """
    # get the article id
    art = anne.get_next_article(userid)
    if art is None: return finish()
    return flask.render_template('full_article.html',
                                  id = art.id_,
                                  userid = userid,
                                  pmc = art.get_extra()['PMC'],
                                  tabs = art.text,
                                  outcome = art.get_extra()['outcome'],
                                  intervention = art.get_extra()['intervention'],
                                  comparator = art.get_extra()['comparator'],
                                  answer = art.get_extra()['answer'], 
                                  reasoning = art.get_extra()['reasoning'])
                               
"""
Submits the article id with all annotations.
"""
@application.route('/submit/', methods=['POST'])
def submit(): 
    userid = flask.request.form['userid']  
    anne.submit_annotation(flask.request.form)
    
    # otherwise go to the next abstract
    id_ = anne.get_next_file(userid)
    if not id_: return flask.redirect(flask.url_for('finish'))
    else: return flask.redirect(flask.url_for('annotate_full', userid = userid))
        
"""
Run the application.
"""
if __name__ == '__main__':
    #application.run()
    application.run(host = '0.0.0.0', port = 8083, threaded = True)
