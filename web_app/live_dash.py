import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app_colors = {
    'background': '#FFFFFF',
    'text': '#00008b',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}


app.layout = html.Div(

     children=[
         html.H2(children='Sleep lab live dashboard '),

         html.Div(children='''
                 more sensors will be implemented.
             '''),

         html.Div(className='row',children=[html.Div(dcc.Graph(id='live-graph',animate=False), className='col s12 m6 l6')]),

         html.Div(id='my-div'),
         dcc.Interval(
             id='my-id',
             interval=1 * 1000,  # in milliseconds
             n_intervals=0,
         ),

         dcc.Interval(
            id='graph-update',
            interval=1 * 2000,  # in milliseconds
            n_intervals=0,
         ),

     ], style={'backgroundColor': app_colors['background'], 'margin-top': '-30px', 'height': '2000px', },
)

@app.callback(
    Output('my-div', 'children'),
    [Input('my-id','n_intervals')]
)
def update_output_div(n):
    conn = sqlite3.connect(r'D:\\4th_year\sleep_lab\sleep_lab\data_processor\sleep_lab.db')
    df = pd.read_sql("SELECT * FROM position_info ORDER BY id DESC LIMIT 1", conn)
    pos = df['position']
    return 'sleeping position: "{}"'.format(pos[0])

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    try:
        address = 'D:\\4th_year\sleep_lab\sleep_lab\data_processor\live.txt'

        output = open(address, "r")
        lineList = output.readlines()
        last_line = lineList[len(lineList)-1]
        loaded_data_json = json.loads(last_line)
        Y = loaded_data_json['heart_raw']
        X = loaded_data_json['id']

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines'
                )
        if not data:
            return 0
        app.logger.info('updating heart_info')

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[0,1000]),
                                                    yaxis=dict(range=[0,5000]),
                                                    title='heart rate vs time'
                                                    )}
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')







if __name__ == '__main__':
    app.run_server(debug=True)
