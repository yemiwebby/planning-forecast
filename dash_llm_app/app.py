import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import folium
import geopandas as gpd
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go
from llm_summary.agentic import run_agentic_summary
import time

import dash
import dash.exceptions
# Initialize Dash
app = Dash(__name__)
server = app.server

# Load forecasting data
df = pd.read_csv('data/output_mock.csv')
years = sorted({int(c.split('_')[0]) for c in df.columns if c.endswith('housing_price')})
years = [str(y) for y in years]

# Load Local Authority shapefile
gdf_lad = gpd.read_file('data/Local_Authority_Districts_(April_2023)_Names_and_Codes_in_the_United_Kingdom.shp')

# Layout
app.layout = html.Div(style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}, children=[
    html.Div(style={'padding': '10px', 'backgroundColor': '#EFEFEF'}, children=[
        html.H1('Housing Forecast Dashboard', style={'margin': '0'}),
        html.P('Explore forecasts of housing price, affordability ratio, and net additional dwellings for UK local authorities.', style={'margin': '5px 0 0 0'})
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
    html.Div(style={'flex': '1', 'display': 'flex', 'overflow': 'auto'}, children=[
        html.Div(style={'flex': '2', 'position': 'relative'}, children=[
            html.Iframe(id='map', style={'width': '100%', 'height': '100%', 'border': 'none'})
        ]),
        html.Div(style={'flex': '1.2', 'padding': '10px', 'backgroundColor': '#F8F9FA', 'overflowY': 'auto'}, children=[
            html.H4('Automated Summary'),
            dcc.Markdown(id='llm-summary', dangerously_allow_html=True),
        ])
    ]),
    html.Div(style={'padding': '10px', 'height': '30%'}, children=[
        dcc.Graph(id='forecast-graph', style={'height': '100%'})
    ])
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
    Output('llm-summary', 'children'),
    Input('la-filter', 'value'),
    Input('year-filter', 'value'),
    Input('metric-filter', 'value')
)
def update(la, year, metric):
    fig_ts = go.Figure()
    avg = df[[f"{y}_{metric}" for y in years]].mean()
    lower = df[[f"{y}_{metric}_ci_lower" for y in years]].mean()
    upper = df[[f"{y}_{metric}_ci_upper" for y in years]].mean()
    fig_ts.add_trace(go.Scatter(x=years, y=avg, mode='lines', name='Average'))
    fig_ts.add_trace(go.Scatter(x=years, y=lower, mode='lines', line=dict(width=0), showlegend=False))
    fig_ts.add_trace(go.Scatter(x=years, y=upper, mode='lines', fill='tonexty', name='CI'))

    if la:
        row = df[df['LAD23NM'] == la].iloc[0]
        vals = [row[f"{y}_{metric}"] for y in years]
        fig_ts.add_trace(go.Scatter(x=years, y=vals, mode='lines+markers', name=la, line=dict(width=3)))

    fig_ts.update_layout(title=metric.replace('_', ' ').title(), margin={'l': 20, 'r': 20, 't': 30, 'b': 20})

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
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'grey', 'weight': 0.5},
        tooltip=folium.GeoJsonTooltip(
            fields=['LAD23NM', f"{year}_{metric}"],
            aliases=['LA', 'Value'],
            localize=True,
            sticky=True
        )
    ).add_to(m)

    folium.LayerControl().add_to(m)
    map_html = m.get_root().render()

    summary = ''
    if la and year:
        summary = generate_summary(la, year)

    return map_html, fig_ts, summary


# @app.callback(
#     Output("copy-box", "value"),
#     Output("copy-status", "children"),
#     Input("copy-btn", "n_clicks"),
#     State("llm-summary", "children"),
#     prevent_initial_call=True
# )
# def copy_to_clipboard(n_clicks, summary_html):
#     if not summary_html:
#         raise dash.exceptions.PreventUpdate

#     # Strip tags for plain text or keep as is
#     from bs4 import BeautifulSoup
#     soup = BeautifulSoup(summary_html, "html.parser")
#     plain_text = soup.get_text()

#     return plain_text, "✅ Copied to clipboard — use Ctrl+C / Cmd+C"


if __name__ == '__main__':
    print("✅ Planning Forecast app is running at http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the server.")
    app.run(debug=True)
