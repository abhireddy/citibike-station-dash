# https://github.com/plotly/dash-recipes/blob/master/mapbox-lasso.py

import os

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import json
import pandas as pd

# df = pd.read_csv(
#     'https://raw.githubusercontent.com/plotly' +
#     '/datasets/master/2011_february_us_airport_traffic.csv')

df = pd.read_csv('csv/station-availability-by-time-of-day.csv')
df['formatted_bike_uptime'] = df.bike_uptime.apply(lambda x: str(round(x*100,0)))
df['formatted_dock_uptime'] = df.dock_uptime.apply(lambda x: str(round(x*100,0)))

df = df[df.time_of_day == 'Peak Weekday Morning']

scl = [[0, 'rgb(238,64,53)'],[1, 'rgb(123,192,67)']]

app = dash.Dash()

server = app.server

app.layout = html.Div([
    # html.Div(
    #     html.Pre(id='lasso', style={'overflowY': 'scroll', 'height': '100vh'}),
    #     className="three columns"
    # ),
    html.H1('Station Availability in the NYC Citi Bike Network'),

    html.Div(
        className="nine columns",
        children=dcc.Graph(
            id='graph',
            figure={
                'data': [{
                    'lat': df.latitude, 'lon': df.longitude,
                    'marker': {
                        'color': df.bike_uptime,
                        'colorscale': scl,
                    },
                    'text': df.stationName + "<br />" + df.formatted_bike_uptime + "% bike uptime",
                    'hoverinfo': 'text',
                    'type': 'scattermapbox',
                }],
                'layout': {
                    'mapbox': {
                      "center": {
                            "lat": 40.68382604,
                            "lon": -73.97632328
                        },
                        "zoom": 11,
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


# @app.callback(
#     Output('lasso', 'children'),
#     [Input('graph', 'selectedData')])
# def display_data(selectedData):
#     return json.dumps(selectedData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
