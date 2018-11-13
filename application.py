import flask
import writer

import annotator
import config
import reader
import numpy as np
from functools import reduce
from agreement_statistics import get_stat


application = flask.Flask(__name__)

anne = annotator.Annotator(reader.get_reader(config.reader)(**config.reader_params),
                           writer.get_writer(config.writer)(**config.writer_params))

"""
Display the main page.
"""
@application.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')
    
"""

Only go to this if there are no more articles to be annotated.
"""
@application.route('/finish/', methods=['GET'])
def finish():
    return flask.render_template('finish.html')
    
"""
Grabs a specified article and displays the full text.
"""
@application.route('/annotate_full/<userid>/', methods=['GET', 'POST'])
def annotate_full(userid):
    # get the article id
    try:
        art, users = anne.get_next_article(userid)
    except:

        return flask.redirect(flask.url_for('finish'))
        
    
    artid = art.get_extra()['path']
    doct_reason, doct_ans, doct_ans_names, doctor_names = get_stats(artid, users)
    
    # modify the pie-chart to contain the correct answer
    tmp = art.get_extra()['answer'].lower().capitalize()
    print("attempt")

    loc = reduce((lambda y, x: y if doct_ans[x][0] != tmp else x), range(len(doct_ans)), -1)
    if (loc == -1):
        doct_ans.append([tmp, 1])
    else:
        doct_ans[loc][1] += 1
    
    
    return flask.render_template('full_article.html',
                                  id = art.id_,
                                  artid = artid,
                                  userid = userid,
                                  pmc = art.get_extra()['PMC'],
                                  tabs = art.text,
                                  outcome = art.get_extra()['outcome'].replace('&lt;', '<').replace('&gt;', '>'),
                                  intervention = art.get_extra()['intervention'].replace('&lt;', '<').replace('&gt;', '>'),
                                  comparator = art.get_extra()['comparator'].replace('&lt;', '<').replace('&gt;', '>'),
                                  doct_reason = hide_names_arr(doct_reason),
                                  doct_ans = doct_ans,
                                  hide_names = hide_names(doctor_names),
                                  doctor_names = doctor_names,
                                  doct_ans_names = hide_names_arr(doct_ans_names),
                                  answer = art.get_extra()['answer'], reasoning = art.get_extra()['reasoning'],
                                  options = config.options_full)
                                  
"""
Submits the article id with all annotations.
"""
@application.route('/submit/', methods=['POST'])
def submit(): 
    userid = flask.request.form['userid']  

    anne.submit_annotation(flask.request.form)
    # otherwise go to the next abstract
    id_ = anne.get_next_file(userid)
    if not id_:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.redirect(flask.url_for('annotate_full', userid = userid))
        

"""
Hides the names of the doctors.
"""
def hide_names(doct_name):
    new_names = []
    for i in range(len(doct_name)):
        new_names.append("Annotator " + str(i + 2))
        
    return new_names
    
"""
Hide the names of the doctors for an array.
"""
def hide_names_arr(doct_ans):
    for i in range(len(doct_ans)):
        doct_ans[i][0] = "Annotator " + str(i + 2) 
    return doct_ans
    
"""
Gets and then formats the stats.
"""
def get_stats(artid, users):
    # doctor reasoning, doctor answer, doctor names
    doct_reason = [] 
    # pie chart
    doct_ans = [['Option', 'Frequency']]
    doctor_names = []
    doct_ans_names = []
    pie = {}
    for u in users:
        # get info
        dr, da, dan, dn = get_stat(artid, u)
        if len(dr) == 0:
            import pdb; pdb.set_trace()
            
        # fmt info
        doct_reason.append(dr[0])
        doct_ans_names.append(dan[0])
        doctor_names.append(dn[0])
    
        # combine piechart
        for i in range(1, len(da)):
            # add it to the data
            if (da[i][0] in pie):
                pie[da[i][0]] += 1
            else:
                pie[da[i][0]] = 1

    
    # pie chart
    for key in pie.keys():
        doct_ans.append([key, pie[key]])
                
    return doct_reason, doct_ans, doct_ans_names, doctor_names    
    
"""
Run the application.
"""
if __name__ == '__main__':
    #application.run()
    application.run(host = '0.0.0.0', port = 8083, threaded = True)
