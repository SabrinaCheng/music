
import sys
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import redis
import json
from datetime import datetime

# stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# specify flask as the server
server = flask.Flask(__name__)
# configure server and stylesheet for dash app
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

redis_password = sys.argv[1]
# connect to Redis
r = redis.Redis(
    host='ec2-34-219-119-131.us-west-2.compute.amazonaws.com',
    port=6379, 
    password=redis_password)


def create_fig(k):
    user_data = r.get(k)
    user_data = json.loads(user_data.decode('utf-8'))
    return {
            'data': [
                {'x': [datetime.fromtimestamp(t) for t in user_data['ts']], \
                 'y': user_data['hr'], 'type': 'line', 'name': 'Heart Rate'},
            ],
            'layout': {
                'title': 'Listening to ' + user_data['title'][-1] + ' by ' + user_data['artist_name'][-1]
            }
        }

dropdown_opt = [{'label': k.decode("utf-8"), 'value': k.decode("utf-8")} for k in r.keys()]

app.layout = html.Div(children=[
    html.H3(children='Beat & Tempo', style={
            'textAlign': 'center'
        }),

    html.Div(children=
        'Workout music recommendation based on heart rate', 
        style={
            'textAlign': 'center'
        }),
    dcc.Dropdown(
        id='user-dropdown',
        options=dropdown_opt,
        placeholder="Select a user",
        style={
            'width': '100%'
        }
    ),
    html.Div(id='dd-output-container'),
])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('user-dropdown', 'value')])
def update_output(value):
    return dcc.Graph(
        id='example-graph',
        figure=create_fig(value)
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter Redis password')


    app.run_server(host="0.0.0.0", debug=True, port=80)
    # app.run_server(debug=True)