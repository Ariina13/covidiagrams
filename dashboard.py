# -*- coding: utf-8 -*-
"""
@author: Marina Inglin
"""

import pandas as pd
import plotly.express as px
import numpy as np
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "CoviDiagrams"
server = app.server
app.config.suppress_callback_exceptions = True
#-------------------------------------------------------
# DATEN
#-------------------------------------------------------

#Daten am Bildschirm ausgeben
import plotly.io as pio
pio.renderers.default = "browser"

#Covid-Daten einlesen
df = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")
#Codebook einlesen
df_codebook = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/28810794703c2e8ff1b37b8d08fef6e8f69880c2/public/data/owid-covid-codebook.csv")
#Liste der Variablen aus Codebook
df_attribute_codebook = df_codebook['column'].tolist()

#Leerzellen rausfiltern und Zeilen bei denen continent keinen Wert haben löschen
df.replace("", np.NaN, inplace=True)
df.dropna(subset=['continent'], axis=0, inplace=True)
df.dropna(subset=['location'], axis=0, inplace=True)

#Länderliste aus Datenquelle um Länder-Dropdown automatisch zu erstellen
location_column = df['location'].tolist()
location_list = []
for i in location_column:
    if i not in location_list:
        location_list.append(i)
        
#Kontinentliste aus Datenquelle um Kontinent-Dropdown automatisch zu erstellen
continent_column = df['continent'].tolist()
continent_list = []
for i in continent_column:
    if i not in continent_list:
        continent_list.append(i)

#Start- und Enddatum aus Datenquelle für Date-Picker
date_column = df['date'].tolist()
oldest_date = min(date_column)
newest_date = max(date_column)
#Defaultwerte die Daten
startdatum=oldest_date
#-- startdatum = (datetime.strptime(newest_date, "%Y-%m-%d")) - timedelta(days=7)
enddatum = newest_date

#Liste der Attribute die in den Dropdown Filter zur Auswahl stehen sollen
attribute_list = df.columns.tolist()
#Attribute die nicht zur Auswahl stehen sollen entfernen
if 'iso_code' in attribute_list:
    attribute_list.remove('iso_code')

if 'continent' in attribute_list:
    attribute_list.remove('continent')    

if 'location' in attribute_list:
    attribute_list.remove('location')  

if 'date' in attribute_list:
    attribute_list.remove('date')    

if 'tests_units' in attribute_list:
    attribute_list.remove('tests_units')      
                 

#-------------------------------------------------------
#LAYOUT
#-------------------------------------------------------

app.layout = html.Div(
    [       
         #Header
         dbc.Row(dbc.Col(html.H1("CoviDiagrams"), className="header", width=12)),
     
         #Tabs
         dbc.Row(dbc.Col(children=[
                 dbc.CardHeader(
                 dbc.Tabs(
                        [
                            dbc.Tab(label="By Country", tab_id="tab-1"),
                            dbc.Tab(label="By Continent", tab_id="tab-2"),
                            dbc.Tab(label="About", tab_id="tab-3", tab_style={"marginLeft": "auto"}),
                        ],
                        id="card-tabs",
                        active_tab="tab-1",
                 )),
                 dbc.CardBody(id="card-content", className="card-text"),
             ], className="tabs", width=12)),
                
         #Footer
         dbc.Row(dbc.Col(html.Div(children=[
                html.P(['The complete COVID-19 dataset is a collection of the COVID-19 data maintained by ', 
                        html.A("Our World in Data.", href ="https://ourworldindata.org/coronavirus", target="_blank"),
                        html.Br(), 
                        'The dataset and more information about it can be found ',
                        html.A("here.", href ="https://github.com/owid/covid-19-data/tree/master/public/data", target="_blank")
                        ]),

                ]), className="footer", width=12)),    
],className = 'container')

#-----------------
#TABS
#-----------------
@app.callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    if active_tab is not None:
        #TAB1 - LÄNDER
        if active_tab == "tab-1":
            return  dbc.Row(
                        [   #GLOBALER FILTER
                            dbc.Col(html.Div(children=[
                                html.H2("Filter options"),
                                html.Br(),
                                #DROPDOWN LÄNDERAUSWAHL
                                html.H3("Select country:"),     
                                     dcc.Dropdown(id='location-dropdown',
                                     options = [{'label': x, 'value': x} for x in location_list
                                                ],
                                     value = ["Switzerland", "Austria", "Germany"],
                                     multi = True,
                                     searchable=True,
                                     clearable=False,
                                     placeholder="Select country",
                                     persistence=True,
                                     persistence_type="memory",
                                     style = {"width": "100%"}, 
                                     className="dropdown"), 
                                html.Br(),
                                     
                                #DATE-PICKER ZEITRAUMAUSWAHL
                                html.H3("Select time period:"),
                                     dcc.DatePickerRange(id='my-date-picker-range',
                                     #Erlaubte Auswahl
                                     min_date_allowed=oldest_date,
                                     max_date_allowed=newest_date,
                                     #Standard-Auswahl
                                     start_date=startdatum,
                                     end_date=enddatum,
                                     persistence=True,
                                     persistence_type="memory",
                                     ),
                                ]), className="global_filter", lg=2, md=12),
                            
                            #DIAGRAMM1
                            dbc.Col(html.Div(children=[
                                #DROPDOWN1
                                html.H2("Diagram 1"),
                                dcc.Dropdown(id='diagramm1_auswahl',
                                            options = [
                                                 {"label": "line diagram", "value": '1'},
                                                 {"label": "bar chart", "value": '2'},
                                                 {"label": "scatter plot", "value": '3'},
                                                 ],
                                            value = '1',
                                            multi = False,
                                            persistence=True,
                                            persistence_type="memory",
                                            style = {"width": "100%"}), 
                                #GRAPH1
                                dcc.Graph(id='diagramm1_graph'),
                                #FILTER1
                                    #Attribut Filter unter Diagramm 1
                                    #Filter X Attribut von Diagramm 1
                                    html.Div(id="diagramm1_x_attribute_filter", 
                                        children = [
                                            #Radio Filter X Attribut Diagramm 1
                                            dcc.RadioItems(id='diagramm1_x_radio_filter',
                                                options=[
                                                    {'label': ' Values per day', 'value': 'on'},
                                                    {'label': ' Average value over the selected time period', 'value': 'off'}
                                                    ],
                                                value='on',
                                                persistence=True,
                                                persistence_type="memory",
                                                labelStyle={'display': 'block'}), 
                                            
                                            html.Br(),  
                                            #Dropdown X Attribut von Diagramm 1
                                            html.H3("Select X-Axis:"),
                                            dcc.Dropdown(id='diagramm1_dropdown_x_attribute',
                                                    options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                               ],
                                                    value = 'new_deaths_per_million',
                                                    persistence=True,
                                                    persistence_type="memory"),
                                                    #X Variable Description für Diagamm 1
                                                    html.Div(id='diagramm1_description_x_attribut', className="variableDescription" )               
                                                    ], style= {'display': 'block'}), 
                                       
                                    #Filter Y Attribut von Diagramm 1
                                    html.Div(id="diagramm1_y_attribute_filter", 
                                        children = [
                                        #Dropdown Y Attribut von Diagramm 1
                                        html.H3("Select Y-Axis:"),
                                        dcc.Dropdown(id='diagramm1_dropdown_y_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                value = 'new_cases_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #Y Variable Description für Diagramm 1
                                                html.Div(id='diagramm1_description_y_attribut', className="variableDescription" )               
                                                ], style= {'display': 'block'}),
                                    
                                ]), className="diagramm", lg=5, md=12),


                            #DIAGRAMM2
                            dbc.Col(html.Div(children=[
                                #DROPDOWN2
                                html.H2("Diagram 2"),
                                dcc.Dropdown(id='diagramm2_auswahl',
                                            options = [
                                                 {"label": "line diagram", "value": '1'},
                                                 {"label": "bar chart", "value": '2'},
                                                 {"label": "scatter plot", "value": '3'},
                                                 ],
                                            value = '2',
                                            multi = False,
                                            persistence=True,
                                            persistence_type="memory",
                                            style = {"width": "100%"}),   
                                #GRAPH2
                                    dcc.Graph(id='diagramm2_graph'),
                                #FILTER2
                                  #Attribut Filter unter Diagramm2
                                  #Filter X-Attribut von Diagramm 2
                                  html.Div(id="diagramm2_x_attribute_filter", 
                                      children = [
                                      #Radio Filter X Attribut Diagramm 2
                                      dcc.RadioItems(id='diagramm2_x_radio_filter',
                                      options=[
                                                  {'label': ' Values per day', 'value': 'on'},
                                                  {'label': ' Average value over the selected time period', 'value': 'off'}
                                                  ],
                                      value='on',
                                      persistence=True,
                                      persistence_type="memory",
                                      labelStyle={'display': 'block'}),   
                                      
                                      html.Br(),  
                                      #Dropdown X Attribut von Diagramm 2 
                                      html.H3("Select X-Axis:"),
                                      dcc.Dropdown(id='diagramm2_dropdown_x_attribute',
                                              options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                         ],                                    
                                              value = 'new_deaths_per_million',
                                              persistence=True,
                                              persistence_type="memory"),
                                              #X Variable Description für Diagamm 2
                                              html.Div(id='diagramm2_description_x_attribut', className="variableDescription" )               
                                              ], style= {'display': 'block'}),
                                  
                                  
                                  #Filter Y-Attribut von Diagramm 2
                                  html.Div(id="diagramm2_y_attribute_filter", 
                                      children = [
                                      #Dropdown Y Attribut von Diagramm 2
                                      html.H3("Select Y-Axis:"),
                                      dcc.Dropdown(id='diagramm2_dropdown_y_attribute',
                                              options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                         ],                                        
                                              value = 'new_cases_per_million',
                                              persistence=True,
                                              persistence_type="memory"),
                                              #Y Variable Description für Diagamm 2
                                              html.Div(id='diagramm2_description_y_attribut', className="variableDescription" )               
                                              ], style= {'display': 'block'}),
                                                    
                                ]), className="diagramm", lg=5, md=12),
                        ]
                    ),
        #TAB2
        elif active_tab == "tab-2":
            return  dbc.Row(
                        [   #GLOBALER FILTER
                            dbc.Col(html.Div(children=[
                                html.H2("Filter options"),
                                html.Br(),
                                #Kontinente
                                html.H3("Select continent:"),     
                                     dcc.Dropdown(id='continent-dropdown',
                                     options = [{'label': x, 'value': x} for x in continent_list
                                                ],
                                     value = ["Europe"],
                                     multi = True,
                                     searchable=True,
                                     clearable=False,
                                     placeholder="Select continent",
                                     persistence=True,
                                     persistence_type="memory",
                                     style = {"width": "100%"},
                                     className="dropdown"),
                                html.Br(),
                                     
                                #Date-Picker
                                html.H3("Select time period:"),
                                     dcc.DatePickerRange(id='my-date-picker-range',
                                     #Erlaubte Auswahl
                                     min_date_allowed=oldest_date,
                                     max_date_allowed=newest_date,
                                     #Standard-Auswahl
                                     start_date=startdatum,
                                     end_date=enddatum,
                                     persistence=True,
                                     persistence_type="memory"                                     ),
                                ]), className="global_filter", lg=2, md=12),
                            
                            #DIAGRAMM3
                            dbc.Col(html.Div(children=[
                                #DROPDOWN3
                                html.H2("Diagram 3"),
                                dcc.Dropdown(id='diagramm3_auswahl',
                                            options = [
                                                 {"label": "line diagram", "value": '1'},
                                                 {"label": "bar chart", "value": '2'},
                                                 {"label": "scatter plot", "value": '3'},
                                                 {"label": "treemap", "value": '4'},
                                                 {"label": "choropleth", "value": '5'},
                                                 ],
                                            value = '4',
                                            multi = False,
                                            persistence=True,
                                            persistence_type="memory",
                                            style = {"width": "100%"}), 
                                #GRAPH3
                                dcc.Graph(id='diagramm3_graph'),
                                #FILTER3
                                    #Attribut Filter unter Diagramm 3
                                    #Filter X-Attribut von Diagramm 3
                                    html.Div(id="diagramm3_x_attribute_filter", 
                                        children = [
                                            #Radio Filter X Attribut Diagramm 3 
                                            dcc.RadioItems(id='diagramm3_x_radio_filter',
                                                options=[
                                                    {'label': ' Values per day', 'value': 'on'},
                                                    {'label': ' Average value over the selected time period', 'value': 'off'}
                                                    ],
                                                value='on',
                                                persistence=True,
                                                persistence_type="memory",
                                                labelStyle={'display': 'block'}),   
                                        
                                        html.Br(),
                                        #Dropdown X Attribut von Diagramm 3
                                        html.H3("Select X-Axis:"),
                                        dcc.Dropdown(id='diagramm3_dropdown_x_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                value = 'new_deaths_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #X Variable Description für Diagamm 3
                                                html.Div(id='diagramm3_description_x_attribut', className="variableDescription")               
                                                ], style= {'display': 'block'}),
                                       
                                    #Filter Y-Attribut von Diagramm 3
                                    html.Div(id="diagramm3_y_attribute_filter", 
                                        children = [
 
                                        #Dropdown Y Attribut von Diagramm 3 
                                        html.H3("Select Y-Axis:"),
                                        dcc.Dropdown(id='diagramm3_dropdown_y_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                value = 'new_cases_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #Y Variable Description für Diagamm 3
                                                html.Div(id='diagramm3_description_y_attribut', className="variableDescription"),
                                         html.Br(),                                        
                                         #Radio Filter Y Attribut Diagramm 3                                   
                                         dcc.RadioItems(id='diagramm3_y_radio_filter',
                                                options=[
                                                    {'label': ' Values per country (per continent)', 'value': 'on'},
                                                    {'label': ' Average over countries (per continent)', 'value': 'off'}
                                                    ],
                                                value='off',
                                                persistence=True,
                                                persistence_type="memory",
                                                labelStyle={'display': 'block'}),                                         
                                                                   
                                        ], style= {'display': 'block'}),                                            

                                    #Filter links für Sonstige Attribute
                                    html.Div(id="diagramm3_sonstige_attribute_filter", 
                                        children = [
                                        #Dropdown Sonstige Attribut von Diagramm 3
                                        html.H3("Select:"),
                                        dcc.Dropdown(id='diagramm3_dropdown_sonstige_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                value = 'new_cases_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #Sonstige Variable Description für Diagamm 3
                                                html.Div(id='diagramm3_description_sonstige_attribut', className="variableDescription")               
                                                ], style= {'display': 'block'}),  
                                        
                                ]), className="diagramm", lg=5, md=12),


                            #DIAGRAMM4
                            dbc.Col(html.Div(children=[
                                #DROPDOWN4
                                html.H2("Diagram 4"),
                                dcc.Dropdown(id='diagramm4_auswahl',
                                            options = [
                                                 {"label": "line diagram", "value": '1'},
                                                 {"label": "bar chart", "value": '2'},
                                                 {"label": "scatter plot", "value": '3'},
                                                 {"label": "treemap", "value": '4'},
                                                 {"label": "choropleth", "value": '5'},
                                                 ],
                                            value = '5',
                                            multi = False,
                                            persistence=True,
                                            persistence_type="memory",
                                            style = {"width": "100%"}), 
                                #GRAPH4
                                dcc.Graph(id='diagramm4_graph'),
                                #FILTER4
                                    #Filter unter Diagramm 4
                                    #Filter  X Attribut Diagramm 4
                                    html.Div(id="diagramm4_x_attribute_filter", 
                                        children = [
                                            #Radio Filter X Attribut Diagramm 4
                                            dcc.RadioItems(id='diagramm4_x_radio_filter',
                                                options=[
                                                    {'label': ' Values per day', 'value': 'on'},
                                                    {'label': ' Average value over the selected time period', 'value': 'off'}
                                                    ],
                                                value='on',
                                                persistence=True,
                                                persistence_type="memory",
                                                labelStyle={'display': 'block'}),   
                                        
                                        html.Br(),
                                        #Dropdown X Attribut von Diagramm 4 
                                        html.H3("Select X-Axis:"),
                                        dcc.Dropdown(id='diagramm4_dropdown_x_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                value = 'new_deaths_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #X Variable Description für Diagamm 4
                                                html.Div(id='diagramm4_description_x_attribut', className="variableDescription")               
                                                ], style= {'display': 'block'}),
                                       
                                    #Filter links für Y Attribut
                                    html.Div(id="diagramm4_y_attribute_filter", 
                                        children = [
                                          
                                       #Dropdown Y Attribut von Diagramm 4 
                                        html.H3("Select Y-Axis:"),
                                        dcc.Dropdown(id='diagramm4_dropdown_y_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                #Standard Wert
                                                value = 'new_cases_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #Y Variable Description für Diagamm 4
                                                html.Div(id='diagramm4_description_y_attribut', className="variableDescription"),
                                        html.Br(),                                        
                                        #Radio Filter Y Attribut Diagramm 4 
                                         dcc.RadioItems(id='diagramm4_y_radio_filter',
                                                options=[
                                                    {'label': ' Values per country (per continent)', 'value': 'on'},
                                                    {'label': ' Average over countries (per continent)', 'value': 'off'}
                                                    ],
                                                value='off',
                                                persistence=True,
                                                persistence_type="memory",
                                                labelStyle={'display': 'block'}),                                         
                                                                   
                                        ], style= {'display': 'block'}),                                            

                                    #Filter links für Sonstige Attribute
                                    html.Div(id="diagramm4_sonstige_attribute_filter", 
                                        children = [
                                        #Dropdown Sonstige Attribut von Diagramm 4
                                        html.H3("Select:"),
                                        dcc.Dropdown(id='diagramm4_dropdown_sonstige_attribute',
                                                options = [{'label': x.replace("_", " "), 'value': x} for x in attribute_list
                                                           ],
                                                value = 'new_cases_per_million',
                                                persistence=True,
                                                persistence_type="memory"),
                                                #Sonstige Variable Description für Diagamm 4
                                                html.Div(id='diagramm4_description_sonstige_attribut', className="variableDescription")               
                                                ], style= {'display': 'block'}),  
                                        
                                ]), className="diagramm", lg=5, md=12),
                        ]
                    ),
        #TAB3
        elif active_tab == "tab-3":
            return dbc.Row(dbc.Col(html.Div(children=[
                html.H2('About'),
                html.P('This project originates from an assignment I worked on during my studies in "Information Science" at the Fachhochschule Graubünden. In a team of four students, we designed and implemented a Dynamic User Interface that provides a wide variety of visualizations and plots about COVID-19 -Data.'),
                html.P('The raw data is sourced from ourworldindata.org. We decided to write the code in Python because of the useful libraries available. We utilized Pandas to process the data. The user interface was created using Plotly and Dash.'),
                html.P('In the beginning we were inexperienced with some of the used technologies and our time for the assignment was limited hence the final product had its flaws.'),
                html.P('Nonetheless the assignment sparked my interest and I decided to redesign the UI and improve the code by myself. Using dash-bootstrap-components I gave the UI its new look and made it responsive. This personal project allowed me to further improve my coding skills and I deepened my knowledge about the mentioned libraries.')
                ]), className="about", width=12)),
                       
    return "No tab selected"


#----------------
# Diagramm 1
#----------------
@app.callback(Output('diagramm1_graph', 'figure'),
    [Input('location-dropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('diagramm1_auswahl', 'value'),
     Input('diagramm1_dropdown_y_attribute', 'value'),
     Input('diagramm1_dropdown_x_attribute', 'value'),
     Input('diagramm1_x_radio_filter', 'value')
     ]
)
def update_diagramm1_graph(land_auswahl, start_date, end_date, diagramm_auswahl, y_attribut, x_attribut, x_radio):
    
    #Daten nach gewähltem Datum filtern (Date-Picker)
    df_timeperiod=df[(df["date"]>= start_date) & (df["date"]<= end_date)]

    #Daten nach gewählten Ländern filtern (Dropdown)
    df_timeperiod_location = df_timeperiod[df_timeperiod['location'].isin(land_auswahl)] 
    
    #DATENSETS
    # Tagesdurchschnitt pro Land berechnen
    df_location_per_day=df_timeperiod_location.groupby(["location", "date"], as_index=False).mean()
    # Durchschnittswerte über ausgewählten Zeitpunkt
    df_location_per_timeperiod=df_timeperiod_location.groupby(["location"], as_index=False).mean()

    #Plotly Diagramme
    if diagramm_auswahl == "1":
    #Liniendiagramm (y-Achse: Attribut von Filter 1)
        fig = px.line(df_location_per_day, x="date", y=y_attribut, color='location', symbol="location")
    elif diagramm_auswahl == "2":
    #Balkendiagramm  (y-Achse: Attribut von Filter 1, x-Achse: Attribut von Filter 2)
        fig = px.bar( df_location_per_timeperiod, x="location", y=y_attribut, color='location')
    elif diagramm_auswahl == "3":
    #Streudiagramm  (y-Achse: Attribut von Filter 1, x-Achse: Attribut von Filter 2)
        if x_radio =="on":
            fig = px.scatter(df_location_per_day, x=x_attribut, y=y_attribut, color='location', symbol="location", hover_data=["date"])
        else:
            fig = px.scatter(df_location_per_timeperiod, x=x_attribut, y=y_attribut, color='location', symbol="location")
    return fig


#Diagramm1: Filter für X-Attribut ein/ausblenden
@app.callback(
    Output('diagramm1_x_attribute_filter', 'style'),
    Input('diagramm1_auswahl', 'value')
)
def show_diagramm1_X_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'} 
    
#Diagramm1: Beschreibung X-Variable
@app.callback(
    Output('diagramm1_description_x_attribut', 'children'),
    [Input('diagramm1_dropdown_x_attribute', 'value')]
)
def update_diagramm1_beschreibung_x_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#Diagramm1: Filter für Y-Attribut ein/ausblenden
@app.callback(
    Output('diagramm1_y_attribute_filter', 'style'),
    Input('diagramm1_auswahl', 'value')
)
def show_diagramm1_Y_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '1' or diagramm_auswahl == '2' or diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

#Diagramm1: Beschreibung Y-Variable
@app.callback(
    Output('diagramm1_description_y_attribut', 'children'),
    [Input('diagramm1_dropdown_y_attribute', 'value')]
)
def update_diagramm1_beschreibung_y_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#----------------
# Diagramm 2
#----------------
@app.callback(Output('diagramm2_graph', 'figure'),
    [Input('location-dropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('diagramm2_auswahl', 'value'),
     Input('diagramm2_dropdown_y_attribute', 'value'),
     Input('diagramm2_dropdown_x_attribute', 'value'),
     Input('diagramm2_x_radio_filter', 'value')
     ]
)
def update_diagramm2_graph(land_auswahl, start_date, end_date, diagramm_auswahl, y_attribut, x_attribut, x_radio):
    
    #Daten nach gewähltem Datum filtern (Date-Picker)
    df_timeperiod=df[(df["date"]>= start_date) & (df["date"]<= end_date)]

    #Daten nach gewählten Ländern filtern (Dropdown)
    df_timeperiod_location = df_timeperiod[df_timeperiod['location'].isin(land_auswahl)] 
    
    #DATENSETS
    # Tagesdurchschnitt pro Land berechnen
    df_location_per_day=df_timeperiod_location.groupby(["location", "date"], as_index=False).mean()
    # Durchschnittswerte über ausgewählten Zeitpunkt
    df_location_per_timeperiod=df_timeperiod_location.groupby(["location"], as_index=False).mean()

    #Plotly Diagramme
    if diagramm_auswahl == "1":
    #Liniendiagramm (y-Achse: Attribut von Filter 1)
        fig = px.line(df_location_per_day, x="date", y=y_attribut, color='location', symbol="location")
    elif diagramm_auswahl == "2":
    #Balkendiagramm  (y-Achse: Attribut von Filter 1, x-Achse: Attribut von Filter 2)
        fig = px.bar( df_location_per_timeperiod, x="location", y=y_attribut, color='location')
    elif diagramm_auswahl == "3":
    #Streudiagramm  (y-Achse: Attribut von Filter 1, x-Achse: Attribut von Filter 2)
        if x_radio =="on":
            fig = px.scatter(df_location_per_day, x=x_attribut, y=y_attribut, color='location', symbol="location", hover_data=["date"])
        else:
            fig = px.scatter( df_location_per_timeperiod, x=x_attribut, y=y_attribut, color='location', symbol="location")
    return fig


#Diagramm2: Filter für X-Attribut ein/ausblenden
@app.callback(
    Output('diagramm2_x_attribute_filter', 'style'),
    Input('diagramm2_auswahl', 'value')
)
def show_diagramm2_X_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'}  
 
#Diagramm2: Beschreibung X-Variable
@app.callback(
    Output('diagramm2_description_x_attribut', 'children'),
    [Input('diagramm2_dropdown_x_attribute', 'value')]
)
def update_diagramm2_beschreibung_x_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)     
 
#Diagramm2: Filter für Y-Attribut ein/ausblenden
@app.callback(
    Output('diagramm2_y_attribute_filter', 'style'),
    Input('diagramm2_auswahl', 'value')
)
def show_diagramm2_Y_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '1' or diagramm_auswahl == '2' or diagramm_auswahl == '3':
        return {'display': 'block'}    
    else:
        return {'display': 'none'}

#Diagramm2: Beschreibung Y-Variable
@app.callback(
    Output('diagramm2_description_y_attribut', 'children'),
    [Input('diagramm2_dropdown_y_attribute', 'value')]
)
def update_diagramm2_beschreibung_y_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#----------------
# Diagramm 3
#----------------
@app.callback(Output('diagramm3_graph', 'figure'),
    [Input('continent-dropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('diagramm3_auswahl', 'value'),
     Input('diagramm3_dropdown_y_attribute', 'value'),
     Input('diagramm3_dropdown_x_attribute', 'value'),
     Input('diagramm3_dropdown_sonstige_attribute', 'value'),
     Input('diagramm3_x_radio_filter', 'value'),
     Input('diagramm3_y_radio_filter', 'value')
     ]
)
def update_diagramm3_graph(kontinent_auswahl, start_date, end_date, diagramm_auswahl, y_attribut, x_attribut, sonstige_attribut, x_radio, y_radio):
    #Daten nach gewähltem Datum filtern (Date-Picker)
    df_timeperiod=df[(df["date"]>= start_date) & (df["date"]<= end_date)]
    
    #Daten nach gewählten Kontinent filtern (Dropdown)     
    df_timeperiod_continent = df_timeperiod[df_timeperiod['continent'].isin(kontinent_auswahl)] 
    
    #DATENSETS
    #Tagesdurchschnitt der Länder des gewählten Kontinents berechnen
    df_location_per_day=df_timeperiod_continent.groupby(["location", "date", "continent"], as_index=False).mean()
    #Tagesdurchschnitt pro Kontinent berechnen    
    df_continent_per_day=df_timeperiod_continent.groupby(["continent", "date"], as_index=False).mean()
    # Durchschnittswert der Länder des gewählten Kontinents über den ausgewählten Zeitpunkt
    df_location_per_timeperiod=df_timeperiod_continent.groupby(["continent", "location"], as_index=False).mean()
    # Durchschnittswerte des Kontinents über ausgewählten Zeitpunkt und all seine Länder
    df_continent_per_timeperiod=df_timeperiod_continent.groupby(["continent"], as_index=False).mean()
    
    #Werteverteilung
    df_verteilung=df_timeperiod_continent.groupby(["continent", "location"], as_index=False).mean()
  
    #Map
    df_map=df_timeperiod_continent.groupby(["iso_code", "location", "continent"], as_index=False).mean()  

    #Plotly Diagramme
    #Liniendiagramm     
    if diagramm_auswahl == "1":
        if y_radio =="on":
            fig = px.line(df_location_per_day, x="date", y=y_attribut, color='location', symbol='location', hover_name='location')
        else:
            fig = px.line(df_continent_per_day, x="date", y=y_attribut, color='continent', symbol="continent")
    #Balkendiagramm     
    elif diagramm_auswahl == "2":
        if y_radio =="on":
            fig = px.bar(df_location_per_timeperiod, x="continent", y=y_attribut, color='continent', hover_name='location')
        else:
            fig = px.bar(df_continent_per_timeperiod, x="continent", y=y_attribut, color='continent')
    #Streudiagramm    
    elif diagramm_auswahl == "3":
        if x_radio =="on":
           if y_radio =="on":         
               fig = px.scatter(df_location_per_day, x=x_attribut, y=y_attribut, color='continent', symbol="continent",  hover_name='location', hover_data=["date"])
           else:
               fig = px.scatter(df_continent_per_day, x=x_attribut, y=y_attribut, color='continent', symbol="continent", hover_data=["date"])
        elif x_radio =="off":    
            if y_radio =="on":         
                fig = px.scatter(df_location_per_timeperiod, x=x_attribut, y=y_attribut, color='continent', symbol="continent", hover_name='location')
            else:
                fig = px.scatter(df_continent_per_timeperiod, x=x_attribut, y=y_attribut, color='continent', symbol="continent")
    #Treemap   
    elif diagramm_auswahl == "4":
        fig = px.treemap(df_verteilung, path=[px.Constant("Total"), 'continent', 'location'], values=sonstige_attribut, color_discrete_sequence=["#b4dee3", "#8cc9d5", "#5da3c6", "#4071b4", "#3b4286", "#1d1d3b"])
        fig.update_traces(root_color="#e5ecf6")
        fig.update_layout(margin = dict(t=20, l=0, r=0, b=0))
        
    # Choropleth   
    elif diagramm_auswahl == "5":
        fig = px.choropleth(df_map, locations="iso_code", color=sonstige_attribut, color_continuous_scale="ice", hover_name="location")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

#Diagramm3: Filter für X-Attribut ein/ausblenden
@app.callback(
    Output('diagramm3_x_attribute_filter', 'style'),
    Input('diagramm3_auswahl', 'value')
)
def show_diagramm3_X_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'} 

#Diagramm3: Beschreibung X-Variable
@app.callback(
    Output('diagramm3_description_x_attribut', 'children'),
    [Input('diagramm3_dropdown_x_attribute', 'value')]
)
def update_diagramm3_beschreibung_x_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)  

#Diagramm3: Filter für Y-Attribut ein/ausblenden
@app.callback(
    Output('diagramm3_y_attribute_filter', 'style'),
    Input('diagramm3_auswahl', 'value')
)
def show_diagramm3_Y_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '1' or diagramm_auswahl == '2' or diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

#Diagramm3: Beschreibung Y-Variable
@app.callback(
    Output('diagramm3_description_y_attribut', 'children'),
    [Input('diagramm3_dropdown_y_attribute', 'value')]
)
def update_diagramm3_beschreibung_y_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#Diagramm3: Filter für Sonstig Attribut ein/ausblenden
@app.callback(
    Output('diagramm3_sonstige_attribute_filter', 'style'),
    Input('diagramm3_auswahl', 'value')
)
def show_diagramm3_sonstige_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '4' or diagramm_auswahl == '5':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

#Diagramm3: Beschreibung Sonstige-Variable
@app.callback(
    Output('diagramm3_description_sonstige_attribut', 'children'),
    [Input('diagramm3_dropdown_sonstige_attribute', 'value')]
)
def update_diagramm3_beschreibung_sonstige_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#----------------
# Diagramm 4
#----------------
@app.callback(Output('diagramm4_graph', 'figure'),
    [Input('continent-dropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('diagramm4_auswahl', 'value'),
     Input('diagramm4_dropdown_y_attribute', 'value'),
     Input('diagramm4_dropdown_x_attribute', 'value'),
     Input('diagramm4_dropdown_sonstige_attribute', 'value'),
     Input('diagramm4_x_radio_filter', 'value'),
     Input('diagramm4_y_radio_filter', 'value')
     ]
)
def update_diagramm4_graph(kontinent_auswahl, start_date, end_date, diagramm_auswahl, y_attribut, x_attribut, sonstige_attribut, x_radio, y_radio):
    #Daten nach gewähltem Datum filtern (Date-Picker)
    df_timeperiod=df[(df["date"]>= start_date) & (df["date"]<= end_date)]
    
    #Daten nach gewählten Kontinent filtern (Dropdown)     
    df_timeperiod_continent = df_timeperiod[df_timeperiod['continent'].isin(kontinent_auswahl)] 
    
    #DATENSETS
    #Tagesdurchschnitt der Länder des gewählten Kontinents berechnen
    df_location_per_day=df_timeperiod_continent.groupby(["location", "date", "continent"], as_index=False).mean()
    #Tagesdurchschnitt pro Kontinent berechnen    
    df_continent_per_day=df_timeperiod_continent.groupby(["continent", "date"], as_index=False).mean()
    # Durchschnittswert der Länder des gewählten Kontinents über den ausgewählten Zeitpunkt
    df_location_per_timeperiod=df_timeperiod_continent.groupby(["continent", "location"], as_index=False).mean()
    # Durchschnittswerte des Kontinents über ausgewählten Zeitpunkt und all seine Länder
    df_continent_per_timeperiod=df_timeperiod_continent.groupby(["continent"], as_index=False).mean()
    
    #Werteverteilung
    df_verteilung=df_timeperiod_continent.groupby(["continent", "location"], as_index=False).mean()
  
    #Map
    df_map=df_timeperiod_continent.groupby(["iso_code", "location", "continent"], as_index=False).mean()  

    #Plotly Diagramme
    #Liniendiagramm     
    if diagramm_auswahl == "1":
        if y_radio =="on":
            fig = px.line(df_location_per_day, x="date", y=y_attribut, color='location', symbol='location', hover_name='location')
        else:
            fig = px.line(df_continent_per_day, x="date", y=y_attribut, color='continent', symbol="continent")
    #Balkendiagramm     
    elif diagramm_auswahl == "2":
        if y_radio =="on":
            fig = px.bar(df_location_per_timeperiod, x="continent", y=y_attribut, color='continent', hover_name='location')
        else:
            fig = px.bar(df_continent_per_timeperiod, x="continent", y=y_attribut, color='continent')
    #Streudiagramm    
    elif diagramm_auswahl == "3":
        if x_radio =="on":
           if y_radio =="on":         
               fig = px.scatter(df_location_per_day, x=x_attribut, y=y_attribut, color='continent', symbol="continent",  hover_name='location', hover_data=["date"])
           else:
               fig = px.scatter(df_continent_per_day,x=x_attribut, y=y_attribut, color='continent', symbol="continent", hover_data=["date"])
        elif x_radio =="off":    
            if y_radio =="on":         
                fig = px.scatter(df_location_per_timeperiod, x=x_attribut, y=y_attribut, color='continent', symbol="continent", hover_name='location')
            else:
                fig = px.scatter(df_continent_per_timeperiod,x=x_attribut, y=y_attribut, color='continent', symbol="continent")
    #Treemap   
    elif diagramm_auswahl == "4":
        fig = px.treemap(df_verteilung, path=[px.Constant("Total"), 'continent', 'location'], values=sonstige_attribut, color_discrete_sequence=["#b4dee3", "#8cc9d5", "#5da3c6", "#4071b4", "#3b4286", "#1d1d3b"])
        fig.update_traces(root_color="#e5ecf6")
        fig.update_layout(margin = dict(t=20, l=0, r=0, b=0))
        
    # Choropleth   
    elif diagramm_auswahl == "5":
        fig = px.choropleth(df_map, locations="iso_code", color=sonstige_attribut, color_continuous_scale="ice", hover_name="location")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

#Diagramm4: Filter für X-Attribut ein/ausblenden
@app.callback(
    Output('diagramm4_x_attribute_filter', 'style'),
    Input('diagramm4_auswahl', 'value')
)
def show_diagramm4_X_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'} 

#Diagramm4: Beschreibung X-Variable
@app.callback(
    Output('diagramm4_description_x_attribut', 'children'),
    [Input('diagramm4_dropdown_x_attribute', 'value')]
)
def update_diagramm4_beschreibung_x_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung) 

#Diagramm4: Filter für Y-Attribut ein/ausblenden
@app.callback(
    Output('diagramm4_y_attribute_filter', 'style'),
    Input('diagramm4_auswahl', 'value')
)
def show_diagramm4_Y_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '1' or diagramm_auswahl == '2' or diagramm_auswahl == '3':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

#Diagramm4: Beschreibung Y-Variable
@app.callback(
    Output('diagramm4_description_y_attribut', 'children'),
    [Input('diagramm4_dropdown_y_attribute', 'value')]
)
def update_diagramm4_beschreibung_y_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#Diagramm4: Filter für Sonstig Attribut ein/ausblenden
@app.callback(
    Output('diagramm4_sonstige_attribute_filter', 'style'),
    Input('diagramm4_auswahl', 'value')
)
def show_diagramm4_sonstige_attribut(diagramm_auswahl):
    #Nummer der Diagramme, bei denen Filter angezeigt werden soll
    if diagramm_auswahl == '4' or diagramm_auswahl == '5':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

#Diagramm4: Beschreibung Sonstige-Variable
@app.callback(
    Output('diagramm4_description_sonstige_attribut', 'children'),
    [Input('diagramm4_dropdown_sonstige_attribute', 'value')]
)
def update_diagramm4_beschreibung_sonstige_variable(attribut):
    index = df_attribute_codebook.index(attribut)
    beschreibung = df_codebook.iloc[index]['description']
    return html.P(beschreibung)

#---------------------------------------

if __name__ == "__main__":
    print("RUN")
    app.run_server()