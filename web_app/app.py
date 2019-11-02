
from flask import Flask, render_template,jsonify
from modules.heart_rate_analysis import data_analysis_bpm
from modules.file_tail import FileTail
from modules.file_play import FilePlay
from modules.heart_info import HeartInfo
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import logging
import datetime
import heartpy as hp
import numpy as np

import matplotlib
matplotlib.use('Agg')

# set up
server = Flask(__name__) # name of the module
heart_info =  HeartInfo()
#file_name = "D:\\program files\\Lithic\\data\\live.txt"
file_name = "D:\\program files\\Lithic\\data\\Data_1\\1_longtime_Data_1_2019-11-01T21-17-30.txt"
file = FilePlay(file_name)
X = list()
X.append(0)
Y = list()
Y.append(0)




@server.route("/")
@server.route("/home") # home page of the website
def home():
    bpm = 0
    heart = heart_info.get_measures()
    try:
        if 'bpm' in heart.keys():
            bpm = float("{0:.2f}".format(heart['bpm']))
    except :
        print("ERROR")
    return render_template('home.html', bpm = bpm)



@server.route("/readme") # home page of the website
def readme():
    return render_template('readme.html')

def process_time(y):
    if len(X) >= 1250:
        measures = 0
        working_data = 0
        try:
            working_data, measures = hp.process(np.array(Y), 250.0)
        except:
            print("bad signal for this one")
        X.clear()
        X.append(0)
        Y.clear()
        Y.append(0)
        print(measures)
        heart_info.set_measures(measures)

    X.append(X[-1]+4)
    Y.append(y)
    return datetime.datetime.now()

app = dash.Dash(__name__, server = server, routes_pathname_prefix='/dash/')

app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*500,
            n_intervals = 0
        ),
    ]
)

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    for i in range(100):
        next_line = file.next()
        this_y = float(next_line.split(',')[2])
        now = process_time(this_y)

    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines'
    )
    logging.debug(X)
    logging.debug(Y)

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[0,5000]),
                                                yaxis=dict(range=[0,4000]),)}



if __name__ == '__main__':
    app.run_server(debug=True)
    print('done')