import sys
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import redis
import json

# stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# specify flask as the server
server = flask.Flask(__name__)
# configure server and stylesheet for dash app
# app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# app.layout = html.Div(children=[
#     html.H1(children='Hello Dash'),

#     html.Div(children='''
#         Dash: A web application framework for Python.
#     '''),

#     dcc.Graph(
#         id='example-graph',
#         figure={
#             'data': [
#                 {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
#                 {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
#             ],
#             'layout': {
#                 'title': 'Dash Data Visualization'
#             }
#         }
#     )
# ])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter Redis password')

    password = sys.argv[1]

    # connect to Redis
    # r = redis.Redis(
    #     host='ec2-34-219-119-131.us-west-2.compute.amazonaws.com',
    #     port=6379, 
    #     password=password)
    
    # for k in r.keys():
    #     print(k)
    #     user_data = r.get(k)
    #     user_data = json.loads(user_data.decode('utf-8'))
        # print(user_data.keys())
        # print(user_data['ts'])
        # print(user_data['hr'])
    
    # app.run_server(host="0.0.0.0", debug=True, port=80)
    app.run_server(debug=True)