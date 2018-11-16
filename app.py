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
df = df[df.time_of_day != 'Other'] # filter out non-peak periods
df = df[df.statusValue == 'In Service'] # filter out inactive stations
df['formatted_bike_uptime'] = df.bike_uptime.apply(lambda x: str(round(x*100)))
df['formatted_dock_uptime'] = df.dock_uptime.apply(lambda x: str(round(x*100)))

# get list for time of day dropdown
timePeriods = df.time_of_day.unique()
defaultTime = 'Peak Weekday Morning'

# get list for metrics dropdown
metricDict = {
    'Bikes': 'formatted_bike_uptime',
    'Open Docks': 'formatted_dock_uptime'
}
metrics = metricDict.keys()
defaultMetric = 'Bikes'

# color scale for station availability
scl = [[0, '#C65C2F'],[0.5, '#DCDCDC'],[1, '#4E8681']] # 0% = red, 50% = gray, 100% = green

app = dash.Dash()
server = app.server

app.layout = html.Div(
    id='intro-and-map',
    children=[
    html.H1(
        'Station Availability in the NYC Citi Bike Network',
        className='main-title'),

    html.P([
        'An interactive visualization of the availability of bikes and open docks based on data from September 2018. ',
        'Built with ',
        html.A('Dash',href='https://medium.com/@plotlygraphs/introducing-dash-5ecf7191b503'),
        ' with a map layer from Mapbox.'],
        className='intro-text'),

    html.P([
        'To learn more about my motivation and methodology, please read my ',
        html.A('Medium post',href='https://medium.com/@abhireddy/is-it-hard-to-find-a-citi-bike-or-is-it-just-me-b4d7cb9d1069'),
        '.'],
        className='intro-text'),

    html.Div(
        id='dropdown-div',
        children=[
        dcc.Dropdown(
            id='time-period-dropdown',
            className='cb-dropdown',
            options=[{'label': i, 'value': i} for i in timePeriods],
            value=defaultTime, # default selection
            clearable=False
        ),

        dcc.Dropdown(
            id='metric-dropdown',
            className='cb-dropdown',
            options=[{'label': i, 'value': i} for i in metrics],
            value=defaultMetric, # default selection
            clearable=False
        )]),
    html.Div(
        className="nine columns",
        children=dcc.Graph(id='mapbox-graph')
    )
], className="row")


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css', # default Dash style sheet
    'external_url': "https://fonts.googleapis.com/css?family=Montserrat|Raleway" # custom fonts
    # custom CSS loaded from assets folder
})

@app.callback(
    dash.dependencies.Output('mapbox-graph', 'figure'),
    [dash.dependencies.Input('time-period-dropdown', 'value'),
    dash.dependencies.Input('metric-dropdown', 'value')])
def updateChart(time_of_day, metric):
    filtered_df = df[df.time_of_day == time_of_day]
    metricFieldName = metricDict[metric]

    return {
        'data': [{
            'lat': filtered_df.latitude, 'lon': filtered_df.longitude,
            'marker': {
                'color': filtered_df[metricFieldName],
                'colorscale': scl,
                'size': 8
            },
            'text': filtered_df.stationName + "<br />" + metric.capitalize() + " available " + filtered_df[metricFieldName] + "% of the time",
            'hoverinfo': 'text',
            'type': 'scattermapbox',
        }],
        'layout': {
            'mapbox': {
              "center": {
                    "lat": 40.72706363348306,
                    "lon": -73.99662137031554 # coordinates for the Mercer St & Bleecker St station
                },
                "zoom": 11,
                'accesstoken': (
                    os.environ['MAPBOX_ACCESS_TOKEN']
                )
            },
            'margin': {
                'l': 0, 'r': 0, 'b': 0, 't': 25
            },
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
