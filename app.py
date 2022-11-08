from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from flask import Flask
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], title="US Police Shootings Analysis")

def load_data(dt_file):
    dt = pd.read_csv(dt_file)
    return dt

def convert_dtypes(data):
    for col in data.columns:
        if data[col].dtype not in ['float64', '<M8[ns]', 'bool']:
            data[col] = data[col].astype('category')
    return data

def treat_missing(data):
    for col in data.columns:
        if data[col].dtype == 'float64':
            data[col].fillna(data[col].mean(), inplace=True)
        if data[col].dtype == 'category':
            data[col].fillna(method='bfill', inplace=True)
    return data

df = load_data('US Police shootings in from 2015-22.csv')

def extract_from_date(data, cols):
    for col in cols:
        data[col] = pd.to_datetime(data[col])
        # for fet in ['year', 'month_name', 'day_name']:
        data['year'] = data[col].dt.year
        data['month'] = data[col].dt.month
        data['day_name'] = data['date'].dt.day_name()
    return data
df = extract_from_date(df, ['date'])
df = convert_dtypes(df)
df = treat_missing(df)
df['age'] = df['age'].astype('int64')

ordered_months = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June",
      7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
# manner of death
manner_death_df = df.groupby(['manner_of_death', 'armed']).size().reset_index(name='counts')
manner_death_fig = go.Figure(
    go.Pie(
    values=manner_death_df['manner_of_death'].value_counts(),
    labels=manner_death_df['manner_of_death'].unique(),
    textinfo='label+percent',
    insidetextorientation='radial',
    hole=.5
        )
    )
manner_death_fig.update_traces(
    title = dict(
        font = dict(
            size=24
        ),
        text = 'Manner of Death',
        position = 'top left'
    ),
    marker=dict(
        line=dict(
            color='black',
            width=1
        )
    )
)

# age
age_df = df.groupby(['age']).size().reset_index(name='count')
age_fig = go.FigureWidget()
age_fig.add_scatter(name='age', x=age_df['age'], y=age_df['count'], fill='tonexty')
#TODO: Add annotations for mean and quantiles
# age_fig.add_annotation()
age_fig.update_layout(title='Age distribution')

# Time data
year_fig = go.FigureWidget()
for t in df['year'].unique():
    mt_df = df[df['year'] == t].groupby(['month']).size().reset_index(name='count')
    year_fig.add_scatter(name=t, x=mt_df['month'].replace(ordered_months), y=mt_df['count'], mode='lines+markers')
year_fig.update_layout(title='Shootings Timeline')


# city
city_df = df.groupby(['state']).size().reset_index(name='counts').sort_values(['counts'], ascending=False)
city_fig = go.FigureWidget()
city_fig.add_bar(x=city_df['state'], y=city_df['counts'])
city_fig.update_layout(title='Total Shootings for Cities')

# visualize in map
df_state_year = df.groupby(['year', 'state']).size().reset_index(name='count')
state_map = px.choropleth(df_state_year, locations='state', locationmode='USA-states', color='count',
                        color_continuous_scale='Viridis_r', scope='usa', animation_frame='year', title='Shootings Observed in each State over the Year')

# median age by state
age_state_df = df.groupby(['state']).median()[['age']].reset_index()
age_map = px.choropleth(age_state_df, locationmode="USA-states", locations='state', color='age',
                        color_continuous_scale='Viridis_r', scope='usa', title='Median Age Observed In Each State')

# title component
header_component = html.H1("US Police Shootings Analysis", style={'color': 'darkblue'})

menu_items = [dbc.DropdownMenuItem(x) for x in city_df['state'].unique()]

# app layout
app.layout = html.Div([
    # row 1
    dbc.Row([
        header_component
    ]),
    # row 2
    html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='md_arm_fig',
                    figure = manner_death_fig
                )
            ], md=5), 
        dbc.Col([
            dcc.Graph(
                figure = age_fig
            )
        ], md=6)
    ], justify='between'),
    ]),
    # row 3
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=year_fig
            ),
        ]),

        dbc.Col([
            dcc.Graph(
                figure = city_fig
            )
        ])
    ]),
    # row 4
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=state_map
            )
        ]),

        dbc.Col([
            dcc.Graph(
                figure=age_map
            )
        ])
    ])
])

app.run_server(debug=True)