# -*- coding: utf-8 -*-
import requests
import pathlib
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from datetime import datetime

from texts import (text_data, text_data_two)

first_currency = 'BTC'
second_currency = 'USD'

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

server = app.server

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

def get_url(timestamp, currency_one, currency_two):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={currency_one}&tsym={currency_two}&limit=2000"
    if timestamp is None:
        return url
    else:
        return url + f'&toTs={timestamp}'

def get_proper_timestamp(data_points):
    if len(data_points) == 0:
        return None
    else:
        min = None
        for data_point in data_points:
            if min is None:
                min = data_point['time']
            else:
                if data_point['time'] < min:
                    min = data_point['time']

        return min


def get_df_data(currency_one, currency_two):
    our_data = []
    timestamp = None

    for i in range(0, 2):
        timestamp = get_proper_timestamp(our_data)
        next_url = get_url(timestamp, currency_one, currency_two)
        response = requests.request('GET', next_url)

        json_result = None
        if response.status_code == 200:
            json_result = response.json()
        else:
            print("Problem with requests")

        new_data = json_result['Data']['Data']
        our_data = new_data + our_data

    df = pd.DataFrame(our_data)
    df['time'] = df['time'].apply(timestamp_to_date)
    return df

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)

df = get_df_data(first_currency, second_currency)

data = go.Data([
            go.Scatter(
              y = df.open,
              x = df.time,
              orientation='h'
        )])

figure_layout = go.Layout(
    colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
    template='plotly_dark',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    margin={'b': 15},
    hovermode='x',
    autosize=True,
    title={'text': 'Cryptocurrencies Historical chart', 'font': {'color': 'white'}, 'x': 0.5},
    xaxis={
        "title": {
            "text": "Time"
        }
    },
    yaxis={
        "title": {
            "text": "Price"
        }
    }
)

fig = go.Figure(
    data=data,
    layout=figure_layout
)


currencies = [
    {'label': 'BTC', 'value': 'BTC'},
    {'label': 'ETH', 'value': 'ETH'},
    {'label': 'LTC', 'value': 'LTC'},
    {'label': 'USD', 'value': 'USD'}
]


current_layout = html.Div(
    [
        dcc.Graph(
            id='example-graph-2',
            figure=fig
        )
    ]
)

left_side = html.Div(
    className='four columns div-user-controls',
    children=[
        html.H2('CRYPTOCURRENCIES HISTORICAL CHART'),
        html.P(text_data),
        html.P(text_data_two),
        html.P('''Please choose a currency from the dropdown menu below.'''),
        dcc.Dropdown(
            id='demo-dropdown-one',
            options=currencies,
            value=first_currency,
            placeholder="Select a currency",
            searchable = False,
            optionHeight = 35,
        ),
        dcc.Dropdown(
            id='demo-dropdown-two',
            options=currencies,
            value=second_currency,
            placeholder="Select a currency",
            searchable = False,
            optionHeight = 35,
        )
    ]
)  # Define the left element

right_side = html.Div(
    className='eight columns div-for-charts bg-grey',
    children=[current_layout]
)  # Define the right element

app.layout = html.Div(
    children=[
        html.Div(
            className='row',  # Define the row element
            children=[
                left_side,
                right_side
            ]
        )
    ]
)

#Dropdown


@app.callback(
    dash.dependencies.Output('example-graph-2', 'figure'),
    [
        dash.dependencies.Input('demo-dropdown-one', 'value'),
        dash.dependencies.Input('demo-dropdown-two', 'value')
    ])
def update_first_output(first, second):
    df = get_df_data(first, second)

    data = go.Data([
        go.Scatter(
            y=df.open,
            x=df.time,
            orientation='h'
        )])

    fig = go.Figure(
        data=data,
        layout=figure_layout
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
