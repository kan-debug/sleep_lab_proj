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
            html.H2(children='Sleep lab history dashboard '),

            html.Div(children='''
                 more sensors will be implemented.
             '''),

            html.Div(className='row',children=[html.Div(dcc.Graph(id='live-graph'), className='col s12 m6 l6')]),
         html.Div(className='row', children=[html.Div(dcc.Graph(id="sentiment-pie", animate=True), className='col s12 m6 l6')]),

         dcc.Interval(
            id='graph-update',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0,
         ),
         dcc.Interval(
             id='sentiment-pie-update',
             interval=1 * 1000,  # in milliseconds
             n_intervals=0,
         ),

     ], style={'backgroundColor': app_colors['background'], 'margin-top': '-30px', 'height': '2000px', },
)



@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    try:
        conn = sqlite3.connect(r'D:\\4th_year\sleep_lab\sleep_lab\data_processor\sleep_lab.db')

        df = pd.read_sql("SELECT * FROM heart_info ORDER BY id DESC LIMIT 10", conn)

        Y = df['bpm']
        X = pd.to_datetime(df['time_stamp'])

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )
        app.logger.info('updating heart_info')
        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),150]),
                                                    title='heart rate vs time'
                                                    )}
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('sentiment-pie', 'figure'),
              [Input('sentiment-pie-update', 'n_intervals')])
def update_pie_chart(n):
    try:
        conn = sqlite3.connect(r'D:\\4th_year\sleep_lab\sleep_lab\data_processor\sleep_lab.db')

        down = pd.read_sql("SELECT count(*) FROM position_info WHERE position = 'facing down' ", conn)
        up = pd.read_sql("SELECT count(*) FROM position_info WHERE position = 'facing up'", conn)
        left = pd.read_sql("SELECT count(*) FROM position_info WHERE position = 'facing left'", conn)
        right = pd.read_sql("SELECT count(*) FROM position_info WHERE position = 'facing right'", conn)
        values = [down.at[0,'count(*)'], up.at[0,'count(*)'],left.at[0,'count(*)'],right.at[0,'count(*)']]

        labels = ['down', 'up' ,'left', 'right']
        print('updating position')

        trace = go.Pie(labels=labels, values=values,
                       hoverinfo='label+percent', textinfo='value',
                       textfont=dict(size=20, color=app_colors['text']),
                       marker=dict(
                                   line=dict(color=app_colors['background'], width=2)))

        return {"data": [trace], 'layout': go.Layout(
            title={'text': 'sleeping position',
                    'y':1,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'})}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')





if __name__ == '__main__':
    app.run_server(debug=True)
