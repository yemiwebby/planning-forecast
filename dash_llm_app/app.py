import os
from dotenv import load_dotenv
load_dotenv()

import os
assert os.path.exists("data/gdf_lad.shp"), "Shapefile not found!"
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import folium
import geopandas as gpd
import ast
import plotly.graph_objs as go
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from llm_summary.agentic import run_agentic_summary

# Initialize Dash
app = Dash(__name__)
server = app.server

# Load data
df = pd.read_csv('data/output.csv')
years = sorted({int(c.split('_')[0]) for c in df.columns if c.endswith('housing_price')})
years = [str(y) for y in years]

# Load Local Authority shapefile
# gdf_lad = gpd.read_file('data/Local_Authority_Districts_(April_2023)_Names_and_Codes_in_the_United_Kingdom.shp')
# gdf_lad = gdf_lad.to_crs(epsg=4326)
# gdf_lad["geometry"] = gdf_lad["geometry"].simplify(0.01)

gdf_lad = gpd.read_file("data/gdf_lad.shp")
gdf_lad = gdf_lad.rename(columns={'LAD24CD':"LAD23CD",
                                  'LAD24NM':"LAD23NM"})


# — Dash setup (light theme + icons) —
external_styles = [dbc.themes.FLATLY, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css']
app = Dash(__name__, external_stylesheets=external_styles)
server = app.server
# Layout
app.layout = html.Div(style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}, children=[

    dbc.NavbarSimple(
            brand='Predictive data models for housing affordability and supply',
            color='light', dark=False,
            children=[html.Span('Unlocking data-driven decisions for future housing supply', className='navbar-text me-3'), dbc.Button('Info', id='open-info', color='secondary', outline=True, size='sm')]
        ),
        html.Div(style={'padding': '0.5rem 1rem', 'backgroundColor': '#f8f9fa'}, children=[
            html.P("This tool supports data-driven decision-making by integrating population trends, migration patterns, and economic indicators to help councils anticipate and meet housing needs. By improving forecasting accuracy, we can reduce mismatches between housing supply and demand, ease pressure on local services, and guide public investment toward healthier, more resilient communities.")
        ]),

   
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '10px', 'backgroundColor': '#FFF'}, children=[
        html.Div([html.Label('Local Authority'), dcc.Dropdown(id='la-filter', options=[{'label': n, 'value': n} for n in sorted(df['LAD23NM'].unique())], placeholder='Select LA')], style={'width': '30%'}),
        html.Div([html.Label('Year'), dcc.Dropdown(id='year-filter', options=[{'label': y, 'value': y} for y in years], value=years[0])], style={'width': '30%'}),
        html.Div([html.Label('Metric'), dcc.Dropdown(id='metric-filter', options=[
            {'label': 'Housing Price', 'value': 'housing_price'},
            {'label': 'Affordability', 'value': 'housing_affordability'},
            {'label': 'Net Additional Dwellings', 'value': 'net_additional_dwellings'}
        ], value='housing_price')], style={'width': '30%'})
    ]),
    html.Div(style={'flex': '1', 'display': 'flex', 'overflow': 'hidden'}, children=[
        html.Div(style={'flex': '2', 'padding': '10px'}, children=[
            html.Iframe(id='map', style={'width': '100%', 'height': '50%', 'border': 'none'}),
            dcc.Graph(id='forecast-graph', style={'height': '50%'})
        ]),
        html.Div(style={'flex': '1.2', 'padding': '10px', 'backgroundColor': '#F8F9FA', 'overflowY': 'auto'}, children=[
            html.H4('Automated Summary'),
            dcc.Loading(
                id="loading-summary",
                type="circle",
                children=dcc.Markdown(id='llm-summary', dangerously_allow_html=True),
                style={"marginTop": "10px"}
            ),
            html.H5("Key Drivers"),
            dcc.Graph(id='importance-bar')
        ])
    ]),

    dbc.Modal([
        dbc.ModalHeader('Info'),
        dbc.ModalBody([
            html.H6('Affordability index'), html.P('This is a measure of how affordable homes are in an area. It is calculated using house prices and income data. The higher the figure the less affordable housing.'),
            html.H6('Net additional dwellings'), html.P('This is the number of new homes that have been built in an area, taking into account any losses, for example from demolitions.'),
            html.H6('House prices'), html.P('These are average house prices for the area, taken from sales data.'),
            html.H6('Jobs density'), html.P('This is a measure of the number of jobs in an area. The higher the figure the more jobs there are in the area.')
        ]),
        dbc.ModalFooter(dbc.Button('Close', id='close-info', className='ms-auto', n_clicks=0))
    ], id='info-modal', is_open=False, size='lg')
])

# Summary generator
def generate_summary(la, year):
    try:
        result = run_agentic_summary(int(year), la, df)
        return result["html"]
    except Exception as e:
        return f"<p><b>Summary Error:</b> {str(e)}</p>"

# Main callback
@app.callback(
    Output('map', 'srcDoc'),
    Output('forecast-graph', 'figure'),
    Output('importance-bar', 'figure'),
    Output('llm-summary', 'children'),
    Input('la-filter', 'value'),
    Input('year-filter', 'value'),
    Input('metric-filter', 'value')
)
def update(la, year, metric):
    # Forecast chart
    fig_ts = go.Figure()
    avg = df[[f"{y}_{metric}" for y in years]].mean()
    lower = df[[f"{y}_{metric}_ci_lower" for y in years]].mean()
    upper = df[[f"{y}_{metric}_ci_upper" for y in years]].mean()

    fig_ts.add_trace(go.Scatter(x=years, y=avg, mode='lines', name='National Avg', line=dict(shape='spline', width=2)))
    fig_ts.add_trace(go.Scatter(x=years, y=upper, mode='lines', line=dict(width=0), showlegend=False))
    fig_ts.add_trace(go.Scatter(x=years, y=lower, mode='lines', fill='tonexty', name='CI', line=dict(width=0)))

    if la:
        row = df[df['LAD23NM'] == la].iloc[0]
        hi_la = [row[f"{y}_{metric}_ci_upper"] for y in years]
        lo_la = [row[f"{y}_{metric}_ci_lower"] for y in years]
        fig_ts.add_trace(go.Scatter(x=years, y=hi_la, mode='lines', showlegend=False, line=dict(width=0)))

        fig_ts.add_trace(go.Scatter(x=years, y=lo_la, mode='lines', fill='tonexty', name=f'{la} CI', line=dict(width=0)))

        vals = [row[f"{y}_{metric}"] for y in years]
        fig_ts.add_trace(go.Scatter(x=years, y=vals, mode='lines+markers', name=la, line=dict(shape='spline', width=4)))

    yaxis_cfg = {}
    if metric == 'housing_price':
        yaxis_cfg['tickprefix'] = '£'
        yaxis_cfg['hoverformat'] = ',.0f'
    elif metric == 'housing_affordability':
        yaxis_cfg['tickformat'] = '.2f'
        yaxis_cfg['hoverformat'] = '.2f'
    else:
        yaxis_cfg['tickformat'] = ',.0f'
        yaxis_cfg['hoverformat'] = ',.0f'

    fig_ts.update_layout(
        template='plotly_white',
        margin={'l': 20, 'r': 20, 't': 30, 'b': 20},
        hovermode='x unified',
        yaxis=yaxis_cfg
    )

    # Map
    map_df = gdf_lad.merge(df[['LAD23CD', f"{year}_{metric}"]], on='LAD23CD', how='left')

    m = folium.Map(location=[54.0, -2.0], zoom_start=5, tiles='cartodbpositron')
    folium.Choropleth(
        geo_data=map_df.__geo_interface__,
        data=map_df,
        columns=['LAD23CD', f"{year}_{metric}"],
        key_on='feature.properties.LAD23CD',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2
    ).add_to(m)
    folium.GeoJson(
        map_df,
        style_function=lambda f: {'fillColor':'transparent','color':'grey','weight':0.3},
        tooltip=folium.GeoJsonTooltip(
            fields=['LAD23NM', f"{year}_{metric}"],
            aliases=['LA','Value'], localize=True
        )
    ).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    map_html = m.get_root().render()

    # Feature importance
    # fig_imp = go.Figure()
    # if la and year and metric:
    #     col = f"{year}_{metric}_feature_importance"
    #     if col in df.columns:
    #         try:
    #             imp = ast.literal_eval(df.loc[df['LAD23NM'] == la, col].iloc[0])
    #             items = sorted(imp.items(), key=lambda kv: kv[1], reverse=True)
    #             feats_raw, scores = zip(*items)
    #             feats = [f.replace('_',' ').title() for f in feats_raw]
    #             fig_imp.add_trace(go.Bar(x=scores, y=feats, orientation='h'))
    #             fig_imp.update_layout(
    #                 template='plotly_white',
    #                 margin={'l': 80, 'r': 20, 't': 20, 'b': 20},
    #                 xaxis_title='Importance',
    #                 yaxis={'automargin': True, 'categoryorder': 'total descending'},
    #                 showlegend=False
    #             )
    #         except Exception:
    #             pass

    fig_imp = go.Figure()
    if la and year and metric:
        col = f"{year}_{metric}_feature_importance"
        if col in df.columns:
            imp = ast.literal_eval(df.loc[df['LAD23NM']==la, col].iloc[0])
            items = sorted(imp.items(), key=lambda kv: kv[1], reverse=True)
            feats_raw, scores = zip(*items)
            feats = [f.replace('_',' ').title() for f in feats_raw]
            fig_imp.add_trace(go.Bar(x=scores, y=feats, orientation='h'))
    fig_imp.update_layout(
        title='Drivers of Metric Value',
        title_x=0.5,
        template='plotly_white',
        margin={'l':80,'r':20,'t':40,'b':20},
        xaxis_title='Importance',
        yaxis={'automargin':True, 'categoryorder':'total descending'},
        showlegend=False
    )

    # Summary
    if la and year:
        summary = generate_summary(la, year)
    else:
        summary = "<p><i>Select a Local Authority and Year to generate the summary.</i></p>"

    return map_html, fig_ts, fig_imp, summary


# Info modal callback
@app.callback(
    Output('info-modal', 'is_open'),
    Input('open-info', 'n_clicks'), Input('close-info', 'n_clicks'), State('info-modal', 'is_open')
)
def toggle_info(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

if __name__ == '__main__':
    print("✅ Planning Forecast is running at http://127.0.0.1:8050")
    app.run(debug=True)
