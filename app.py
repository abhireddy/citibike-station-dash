# https://github.com/plotly/dash-recipes/blob/master/mapbox-lasso.py

import os

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import json
import pandas as pd

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly' +
    '/datasets/master/2011_february_us_airport_traffic.csv')

app = dash.Dash()

server = app.server

app.layout = html.Div([
    html.Div(
        html.Pre(id='lasso', style={'overflowY': 'scroll', 'height': '100vh'}),
        className="three columns"
    ),

    html.Div(
        className="nine columns",
        children=dcc.Graph(
            id='graph',
            figure={
                'data': [{
                    'lat': df.lat, 'lon': df.long, 'type': 'scattermapbox'
                }],
                'layout': {
                    'mapbox': {
                        'accesstoken': (
                            os.environ['MAPBOX_ACCESS_TOKEN']
                        )
                    },
                    'margin': {
                        'l': 0, 'r': 0, 'b': 0, 't': 0
                    },
                }
            }
        )
    )
], className="row")


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(
    Output('lasso', 'children'),
    [Input('graph', 'selectedData')])
def display_data(selectedData):
    return json.dumps(selectedData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
