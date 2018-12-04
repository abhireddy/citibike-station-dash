# -*- coding: utf-8 -*-

import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import json
import pandas as pd

df = pd.read_csv('csv/station-availability-by-time-of-day.csv')
df = df[df.time_of_day != 'Other'] # filter out non-peak periods
df = df[df.statusValue == 'In Service'] # filter out inactive stations
df['formatted_bike_uptime'] = df.bike_uptime.apply(lambda x: str(round(x*100)))
df['formatted_dock_uptime'] = df.dock_uptime.apply(lambda x: str(round(x*100)))

# get list for time of day dropdown
timePeriods = df.time_of_day.unique()
defaultTime = 'Peak Weekday Mornings (7-10 AM)'

# get list for metrics dropdown
metricDict = {
    'Bikes': 'formatted_bike_uptime',
    'Open Docks': 'formatted_dock_uptime'
}
metrics = metricDict.keys()
defaultMetric = 'Bikes'

# color scale for station availability
scl = [[0, '#C65C2F'],[0.5, '#DCDCDC'],[1, '#4E8681']] # 0% = red, 50% = gray, 100% = green

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://fonts.googleapis.com/css?family=Montserrat|Raleway']
# additional custom CSS in assets/ folder

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    children=[
    html.H1(
        'Mapping Citi Bike Availability',
        className='main-title'),

    html.P([
        'An interactive map indicating how often Citi Bike stations had at least one bike or open dock available ',
        'during periods of peak usage in September 2018. ',
        'This availability metric can be used to evaluate how well bikes are rebalanced across the network ',
        'to avoid unnecessary detours for riders.'
        ], className='intro-text'),

    html.P([
        'This visualization was built in ',
        html.A('Dash',href='https://medium.com/@plotlygraphs/introducing-dash-5ecf7191b503',target='_blank'),
        ' with mapping provided by Mapbox. ',
        'You can ',
        html.A('read more',href='https://medium.com/@abhireddy/is-it-hard-to-find-a-citi-bike-or-is-it-just-me-b4d7cb9d1069',target='_blank'),
        ' about this project or view the ',
        html.A('source code',href='https://github.com/abhireddy/citibike-station-dash',target='_blank'),
        '.'],
        className='intro-text'),

    html.P([
        'If you\'re having trouble loading the visualization, ' ,
        'please try disabling your ad blocker.'
        ],
        className='intro-text'),

    html.Div(
        id='dropdown-div',
        className="row",
        children=[
            html.Div(
                id="time-period-dropdown-div",
                className="six columns",
                children=[
                html.P('Time Period:', className="dropdown-label"),
                dcc.Dropdown(
                    id='time-period-dropdown',
                    options=[{'label': i, 'value': i} for i in timePeriods],
                    value=defaultTime, # default selection
                    clearable=False
                )]),

                html.Div(
                    id="metric-dropdown-div",
                    className="six columns",
                    children=[
                    html.P('Availability of:', className="dropdown-label"),
                    dcc.Dropdown(
                        id='metric-dropdown',
                        options=[{'label': i, 'value': i} for i in metrics],
                        value=defaultMetric, # default selection
                        clearable=False
                    )]),
        ]),

    html.Div(
        className="twelve columns",
        children=dcc.Graph(
            id='mapbox-graph',
            config={ 'displayModeBar': False }
        )
    )
], className="row")

@app.callback(
    dash.dependencies.Output('mapbox-graph', 'figure'),
    [dash.dependencies.Input('time-period-dropdown', 'value'),
    dash.dependencies.Input('metric-dropdown', 'value')],
    [State('mapbox-graph', 'relayoutData')])
def updateChart(time_of_day, metric, relayout_data):
    # filter data source for the selected metrics
    filtered_df = df[df.time_of_day == time_of_day]
    metricFieldName = metricDict[metric]

    # preserve user's current panning and zoom when they update the map
    if relayout_data and not relayout_data.get('autosize'):
        latitude = relayout_data['mapbox.center']['lat']
        longitude = relayout_data['mapbox.center']['lon']
        zoom = relayout_data['mapbox.zoom']
        pitch = relayout_data['mapbox.pitch']
    else:
        # defaults for first page load
        latitude = 40.72706363348306
        longitude = -73.99662137031554
        zoom = 11
        pitch = 0

    return {
        'data': [{
            'lat': filtered_df.latitude, 'lon': filtered_df.longitude,
            'marker': {
                'color': filtered_df[metricFieldName],
                'colorscale': scl,
                'size': 11
            },
            'text': filtered_df.stationName + "<br />" + metric.capitalize() + " available " + filtered_df[metricFieldName] + "% of the time",
            'hoverinfo': 'text',
            'type': 'scattermapbox',
        }],
        'layout': {
            'mapbox': {
              "center": {
                    "lat": latitude,
                    "lon": longitude # coordinates for the Mercer St & Bleecker St station
                },
                "zoom": zoom,
                "pitch": pitch,
                'accesstoken': (
                    os.environ['MAPBOX_ACCESS_TOKEN']
                )
            },
            'margin': {
                'l': 0, 'r': 0, 'b': 0, 't': 0
            },
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)
