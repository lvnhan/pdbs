"""
HealthCare Dasboard Template with the ThemeSwitchAIO component
Note - this requires dash-bootstrap-components>=1.0.0 and dash>=2.0 dash-bootstrap-templates>=1.0.4.
NhanLe

"""
import pandas as pd
from dash import dcc, html, Input, Output, register_page, callback#, Dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
#..
import dash_daq as daq
from datetime import timedelta, date
from dateutil import parser #use to parse date string to date object
import numpy as np

# include common function from helpers
from helpers.math_helpers import divide


register_page(
    __name__,
    path='/hc_owid',
    name='World',
    title='Plotly.Dash Coronavirus Pandemic by OWID',
    description='Coronavirus Pandemic in the World'
    )
# select the Bootstrap stylesheets and figure templates for the theme toggle here:
template_theme1 = "simplex" 
template_theme2 = "darkly"

# dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
# app = Dash(__name__, external_stylesheets=[url_theme1, dbc_css], suppress_callback_exceptions=True)
# app.title = "Plotly.Dash Coronavirus Pandemic"

#local style HTML
colors = {
    'pl.bkground': 'rgba(0, 0, 0, 0)',
    'pg.bkground': 'rgba(0, 0, 0, 0)',
    'drop.bkg': '#1E1E1E',
    'text.light': '#B6B6B6',
    'text.note': '#989898'
}
fontnames = {
    'u': 'Segoe UI',
    'l': 'Segoe UI Light',
    's': 'Segoe UI Semibold',
    'b': 'Segoe UI Black'
    }

fontsz = {
    'f40': '2.5em'  ,
    'f30': '1.875em',
    'f14': '0.875em',
    'f16': '1em',
    'f12': '0.75em' ,
    'f10': '0.625em' 
    }
# pass variables
title = ['Bảng đồ cấp độ dịch trong cộng đồng', 'STATISTIC DATA']
stitle= ['Dữ liệu ghi nhận từ OWID','Visualising data with Plotly - Dash']
LTitleChart = 'Biểu đồ thống kê dịch bệnh theo ngày'
STitleChart = 'Biểu đồ thống kê số ca nhiễm tích lũy & tử vong'

fnote = ['7-day rolling average. Due to limited testing, the number of confirmed cases is lower than the true number of infections.',
         '(Dữ liệu về các ca nhiễm được cập nhật thường xuyên từ OWID)',
         'Dữ liệu sẽ hiển thị giá trị 0 khi số liệu chưa được cập nhật.']

cardtitle =['Ca nhiễm tích lũy', 'Ca nhiễm theo ngày', 'Người tiêm vaccine/ngày', 'Ca tử vong tích lũy']
cardcontent =['Mức tăng giảm: ', 'Tỷ lệ/1M dân: ', 'Số người tiêm đủ liều: ', 'Tỷ lệ/1M dân: ']
cardclass ={
    'h':'bg-primary bg-gradient fw-light text-white', 
    'b':'card-title fw-bold',
    's':'card-text',
    'g':'text-center shadow-sm rounded'
    }
defCountries = ['France','Vietnam','Germany','United Kingdom','Italy','Japan','Canada','United States']
metrics = {
    'new_cases_smoothed':'Confirmed cases', 
    'new_deaths_smoothed':'Confirmed deaths', 
    'people_vaccinated': 'People vaccinated', 
    'people_fully_vaccinated': 'People fully vaccinated' 
    #số người tiêm đủ liều theo phác đồ tiêm chủng ban đầu
    }
sd = [0] * 4

# Load data
df = pd.read_csv('./data/owid-covid-data.csv')
# filter
df.dropna(subset = ['continent'], inplace = True) 
# Replace NaN Values with Zeros in Pandas DataFrame
df = df.replace(np.nan, 0)
# Extract and add more the year from date column
df['year'] = pd.DatetimeIndex(df['date']).year

dfc = df.copy(deep=True)
df.index = pd.to_datetime(df['date'])
dmax = date.today() + timedelta(days=-1)
diff = date.fromisoformat(dmax.strftime('%Y-%m-%d')) - date.fromisoformat('2020-01-22')

#############################################
# preprocess data for scatter fig
# Remove all NULL value from continent
# get date max from dataframe
#############################################
dfc.index = pd.to_datetime(dfc['date'])

date_req = dfc.index.max() + timedelta(days=-1)
filterMask = dfc['date'] >= date_req.strftime('%Y-%m-%d') #<= apply for animation
# filterMask = dfc['date'] <= date_req.strftime('%Y-%m-%d') #<= apply for animation
dfmc = dfc[filterMask]

#############################################
# Data statistic
#############################################
befDate = dmax + timedelta(days=-1)
#############################################
# Calculate total cumulative confirmed cases
#############################################
tcases_p  = 0
tcases_c = 0
deviant = 0
tcases_percent = 0.0
def update_cardsinfo(adf, max_dt, bef_dt):
    befDate = bef_dt
    dmax = max_dt
    #############################################
    # Creates a list containing 4 lists, each of 2 items, all set to empty
    # each card includes: 0- body | 1-sup info
    #############################################
    w, h = 2, 4
    card_rstl = [['' for x in range(w)] for y in range(h)]
    
    #############################################
    # Calculate total cumulative confirmed cases
    #############################################    
    tcases_p = adf[adf['date'] == befDate.strftime('%Y-%m-%d')].sum(numeric_only = True)['total_cases']
    tcases_c = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['total_cases']  
    sd[0] = tcases_c
    deviant = tcases_c - tcases_p
    #tcases_percent = deviant/tcases_p #use % formatting, so without *100
    tcases_percent = divide(deviant, tcases_p)

    card_rstl[0][0] = "{:,.0f}".format(sd[0])
    card_rstl[0][1]  = [cardcontent[0],
                         (lambda x: html.Label('\u25B2 ', style={'color': '#FF0000'}) if x>0 else html.Label("\u25BC ", style={'color': '#228B22'}))(deviant),
                         ("{:,.0f}".format(deviant)+" ({:.2%})").format(tcases_percent)
                         ]
    #############################################
    # Total new cases per 1,000,000 people
    #############################################
    #ncases_p = adf[adf['date'] == befDate.strftime('%Y-%m-%d')].sum(numeric_only = True)['new_cases']
    ncases_c = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['new_cases']
    sd[1] = ncases_c
    
    ncases_pm = adf[adf['date'] == befDate.strftime('%Y-%m-%d')].sum(numeric_only = True)['new_cases_per_million']
    ncases_cm = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['new_cases_per_million']
    
    deviantn = ncases_cm - ncases_pm
    #ncases_percent = deviantn/ncases_pm
    ncases_percent = divide(deviantn, ncases_pm)
    
    card_rstl[1][0] = "{:,.0f}".format(sd[1])
    card_rstl[1][1] = [cardcontent[1],
                       "{:,.0f}".format(ncases_cm) + " (",
                       (lambda x: html.Label('\u25B2 ', style={'color': '#FF0000'}) if x>0 else html.Label("\u25BC ", style={'color': '#7CFC00'}))(deviantn),
                       #forestgreen	#228B22 | lawngreen 	#7CFC00
                       "{:,.2%}".format(ncases_percent) + ")"
        ]
    
    #############################################
    # Total number of people who received at least one vaccine dose
    #############################################
    pvacc_c = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['people_vaccinated']
    pfvacc_c = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['people_fully_vaccinated']
    
    sd[2] = pvacc_c                            
    card_rstl[2][0] = "{:,.0f}".format(sd[2])
    card_rstl[2][1] = [cardcontent[2] + "{:,.0f}".format(pfvacc_c)]
    
    #############################################
    # Total deaths
    #############################################
    tdeaths_c = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['total_deaths']
    tdeaths_percent = adf[adf['date'] == dmax.strftime('%Y-%m-%d')].sum(numeric_only = True)['total_deaths_per_million']

    sd[3] = tdeaths_c
    card_rstl[3][0] = "{:,.0f}".format(sd[3])
    card_rstl[3][1] = [cardcontent[3] + "{:,.0f}".format(tdeaths_percent)]
 
    return card_rstl

#############################################
header = html.Div(children=[
    dbc.Row([
        dbc.Col([
            html.H2(title[0], className="text-white",
                    style={'font-family': fontnames['l']})
            ], xs=12, sm=12, md=12)
        ]),
    dbc.Row([
        dbc.Col([html.Sup(stitle[0], style={'color':'#E6E6E6'})], xs=12, sm=12, md=12)
        ])
    ], className="bg-primary bg-gradient p-3 mb-2")


SubHeader = html.Div(children=[
            html.H5("Biểu đồ", style={'font-family': fontnames['l']})
            ])
#############################################
# Define top four cards
#############################################
card = {
        '0':
            dbc.Card([ #{:.9f}
                dbc.CardHeader(id="c0", children=[cardtitle[0]], className=cardclass['h']),
                dbc.CardBody([html.H3(className=cardclass['b'], style={'color':'#FF0000'}, id="c0b"),
                              html.Sup(id="c0s", children=[], className=cardclass['s'])
                              ])
                ],className=cardclass['g'], style={"height": 150}
                ),      
        '1':
            dbc.Card([
                dbc.CardHeader(id="c1", children=[cardtitle[1]], className=cardclass['h']),
                dbc.CardBody([html.H3(className=cardclass['b'], style={'color':'#FF8C00'}, id="c1b"), #orangered:#FF4500 darkorange: #FF8C00
                              html.Sup(id="c1s", children=[], className=cardclass['s'])
                              ])
                ],className=cardclass['g'], style={"height": 150}
                ),
        '2':
            dbc.Card([
                dbc.CardHeader(id="c2", children=[cardtitle[2]], className=cardclass['h']),
                dbc.CardBody([html.H3(className=cardclass['b'], style={'color':'#409602'}, id="c2b"),
                              html.Sup(id="c2s", children =[], className=cardclass['s'])
                              ])
                ],className=cardclass['g'], style={"height": 150}
                ),
        '3':
            dbc.Card([
                dbc.CardHeader(id="c3", children=[cardtitle[3]], className=cardclass['h']),
                dbc.CardBody([html.H3(className=cardclass['b'], id="c3b"),
                              html.Sup(id="c3s", children=[], className=cardclass['s'])
                              ])
                ],className=cardclass['g'], style={"height": 150}
                ),
        }
cards = html.Div([
        dbc.Row(
            [
                dbc.Col(dbc.Card(card['0']), xs=12, sm=12, md=3),
                dbc.Col(dbc.Card(card['1']), xs=12, sm=12, md=3),
                dbc.Col(dbc.Card(card['2']), xs=12, sm=12, md=3),
                dbc.Col(dbc.Card(card['3']), xs=12, sm=12, md=3),
            ],
            className="mb-0",
        )])
#############################################
# Define switching btn for dark-light screen
#############################################
switch = html.Div([
    dbc.Row([
        dbc.Col(
            children=[
                html.Sup("Coronavirus Pandemic (COVID-19).", style={'font-weight': 'bold'}),
                html.Sup(" Dữ liệu đã được cập nhật đến ngày " + dmax.strftime('%d-%m-%Y') + " (UTC) | "),
                html.Sup("Đợt bùng phát từ ngày 22-01-2020 đến nay: {}".format(diff.days) + " ngày.")
            ],
            xs=12, sm=12, md=12
        ),
        # dbc.Col(
        #     html.Div([
        #         html.Div(id="switch-result", children=["Light screen"], style={'display': 'inline-block', 'font-size': '12', 'margin-right': '10px'}),
        #         html.Div(ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2], icons={"left": "{%}", "right": "{%}"}), style={'display': 'inline-block'})
        #     ], style={'textAlign': 'right'}),
        #     xs=12, sm=12, md=3
        # )
    ])
])

#############################################
# Define pg footer 
#############################################
bottom = html.P("© 2022 LAC VIET Computing Corp.")
#############################################
# Define criterias
#############################################
yrslider = dcc.RangeSlider(
    min = df['year'].min(),
    max = df['year'].max(),
    step = 1,
    value = [df['year'].min(), df['year'].max()],
    marks={str(year): str(year) for year in df['year'].unique()},
    id='year-slider'
    )

# Creating a Dropdown Menu
# Creates a list of dictionaries, which have the keys 'label' and 'value'.

def get_options(locations):
    dict_list = [{'label': 'Select all', 'value': 'all_values'}]
    for i in locations:
        dict_list.append({'label': i, 'value': i})
    return dict_list

def get_days(days):
    dict_list = []
    for i in days:
        dict_list.append({'label': i, 'value': i})
    return dict_list

crictrl = html.Div(className='div-user-controls',
                     children=[
                         html.H6('Plotly.Dash',style={'color': colors['text.light'], 'font-family': fontnames['l']}, className="mt-5"),
                         html.H5(title[1]),
                         html.Div(children=[html.Sup('Statistic data by year(s)'), yrslider], className="mt-3"),
                         html.Div(className='div-for-dropdown mt-3',
                                  children=[
                                      html.Sup('Select date'),
                                      dcc.Dropdown(id='dateselector', multi=False,
                                                   value=df['date'].unique().max(),
                                                   style={'backgroundColor': colors['drop.bkg'],
                                                   'font-family': fontnames['u'],
                                                   'font-size': fontsz['f16']},
                                                   className='dateselector'
                                      )
                                      ]
                                  ),                         
                         html.Div(className='div-for-dropdown mt-3',
                                  children=[
                                      html.Sup('Select location'),
                                      dcc.Dropdown(id='locselector',
                                                   options=get_options(df['location'].unique()), multi=True,
                                                   value=defCountries,
                                                   style={'backgroundColor': colors['drop.bkg'],
                                                   'font-family': fontnames['u'],
                                                   'font-size': fontsz['f16']},
                                                   className='locselector'
                                      )
                                      ]
                                  ),
                         html.Div(className='div-for-dropdown mt-3',
                                  children=[
                                      html.Sup('Chỉ số theo dõi'),
                                      dcc.Dropdown(id='crossfilter_metricselector',
                                                   options=metrics, multi=False,
                                                   value='new_cases_smoothed',
                                                   style={'backgroundColor': colors['drop.bkg'],
                                                   'font-family': fontnames['u'],
                                                   'font-size': fontsz['f16']},
                                                   className='locselector'
                                      )
                                      ]
                                  ),
                         html.Div(className='div-for-dropdown mt-3',
                                  children=[html.Div(children=[fnote[2],html.Br(),'Chọn đồ thị'], 
                                                     className='mt-5 mx-1'),
                                            html.Div(children=[
                                                daq.ToggleSwitch(id='ChartTypeToggle-switch', size=25,
                                                                 color='grey',label=['Dạng line', 'Dạng log'],
                                                                 value=False)], className='mb-3' #'m-4 ms-5'
                                                     ) 
                                            ], style={'font-size': fontsz['f12'],})
                         ], style={'font-family': fontnames['u']}
    )

#############################################
ggraph = html.Div(dcc.Graph(id="ggraph"), className="m-4")
cgraph = {
    'line':html.Div(dcc.Graph(id="cgraph_line"), className="m-4"),
    'scatter':html.Div(dcc.Graph(id="cgraph_scatter"), className="m-4"),
    }

layout = dbc.Container(children=[
    dbc.Row(
        [
            #dbc.Col(xs=0, sm=0, md=1),
            dbc.Col(
                [
                    header,
                    switch,
                ], xs=12, sm=12, md=12
            ),
            #dbc.Col(xs=0, sm=0, md=1)
        ]
    ),
    dbc.Row(
        [
        #dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(cards, xs=12, sm=12, md=12),
        #dbc.Col(xs=0, sm=0, md=1)
        ]
        ),
    dbc.Row(
        [
        #dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(crictrl, xs=12, sm=12, md=3 ),#, className="shadow-sm rounded m-1"
        dbc.Col(cgraph['line'], xs=12, sm=12, md=9, className="shadow-sm rounded m-0"), 
        #dbc.Col(xs=0, sm=0, md=1)
        ],#className="m-1"
        ),
    dbc.Row(
        [
        #dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(xs=12, sm=12, md=3),
        dbc.Col(cgraph['scatter'], xs=12, sm=12, md=9, className="shadow-sm rounded m-0"), #, className="shadow-sm rounded m-1"
        #dbc.Col(xs=0, sm=0, md=1)
        ]
        ),
    dbc.Row(
        [
        #dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(xs=12, sm=12, md=3),
        dbc.Col(ggraph, xs=12, sm=12, md=9, className="shadow-sm rounded m-0"),
        #dbc.Col(xs=0, sm=0, md=1)
        ]
        ),
    dbc.Row(
        [
        #dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(bottom, xs=12, sm=12, md=12),
        #dbc.Col(xs=0, sm=0, md=1)
        ]
        ),
    ],
    className="m-1 dbc", #m-4
    fluid=True,
)

@callback(
    Output('c0b', 'children', allow_duplicate=True),
    Output('c0s', 'children', allow_duplicate=True),
    Output('c1b', 'children', allow_duplicate=True),
    Output('c1s', 'children', allow_duplicate=True),
    Output('c2b', 'children', allow_duplicate=True),
    Output('c2s', 'children', allow_duplicate=True),
    Output('c3b', 'children', allow_duplicate=True),
    Output('c3s', 'children', allow_duplicate=True),
    Input('dateselector', 'value'),
    Input('locselector', 'value'),
    prevent_initial_call='initial_duplicate'
    )
def update_cards(selected_date, selected_loc):
    dmax = parser.parse(selected_date)
    befDate = dmax + timedelta(days=-1)
    if selected_loc==['all_values']:
        dff = df
    else:
        dff = df[df['location'].isin(selected_loc)]

    #############################################
    # Calculate total cumulative confirmed cases
    #############################################
    cardinfo = update_cardsinfo(dff, dmax, befDate)

    return  cardinfo[0][0], cardinfo[0][1], cardinfo[1][0], cardinfo[1][1], cardinfo[2][0], cardinfo[2][1], cardinfo[3][0], cardinfo[3][1]

@callback(  
    Output('dateselector', 'options', allow_duplicate=True),
    Output('dateselector', 'value', allow_duplicate=True),
    Input('year-slider', 'value'),
    prevent_initial_call='initial_duplicate'
    )

def set_date_range(selected_year):
    yrmin = int(selected_year[0])
    yrmax = int(selected_year[1])
    dff = df[(df.year >= yrmin) & (df.year <= yrmax)]
    dmax = dff['date'].unique().max()
    return get_days(dff['date'].unique()), dmax

@callback(
    #Output("switch-result", 'children'),
    Output("cgraph_line", "figure", allow_duplicate=True),
    Output("cgraph_scatter", "figure", allow_duplicate=True),
    Output("ggraph", "figure", allow_duplicate=True),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input('year-slider', 'value'),
    Input('dateselector', 'value'),
    Input('locselector', 'value'),
    Input('crossfilter_metricselector','value'),
    Input('ChartTypeToggle-switch', 'value'),
    prevent_initial_call='initial_duplicate'   
)
def update_theme(toggle, selected_year, selected_date, selected_loc, xaxis_name, selected_chart_type):
    yrmin = int(selected_year[0])
    yrmax = int(selected_year[1])
  
    # template = template_theme1 if toggle else template_theme2
    s='Màn hình sáng' if toggle else 'Màn hình tối'
    template = template_theme1 if toggle else template_theme2
    
    if selected_loc==['all_values']:
        dff = df[(df.year >= yrmin) & (df.year <= yrmax)]
        dffmc = dfmc[(dfmc.year >= yrmin) & (dfmc.year <= yrmax)]
    else:
        dff = df[(df.year >= yrmin) & (df.year <= yrmax)]
        dffmc = dfmc[(dfmc.year >= yrmin) & (dfmc.year <= yrmax)]
        
        dff = dff[dff['location'].isin(selected_loc)]
        dffmc = dffmc[dffmc['location'].isin(selected_loc)]
    

    # Charting in Dash – Displaying a Plotly-Figure
    ##############################
    # reload dataframe by criteria
    ##############################
    dmax = parser.parse(selected_date)
    
    cfigline = px.line(dff, x='date', y=dff[xaxis_name], color='location',  markers=False, height=500, #width=700,
                  labels={
                  "date": "Ngày ghi nhận",
                  "new_cases_smoothed": "Số ca nhiễm bình quân trong tuần",
                  "new_deaths_smoothed": "Số tử vong bình quân trong tuần",
                  "people_vaccinated":"Số người đã tiêm ít nhất một liều vaccine",
                  "people_fully_vaccinated":"Số người tiêm đủ liều",
                  "location": "Quốc gia"
                  }, 
                  template=template,
                  #animation_frame="date", animation_group="location",
                  title= LTitleChart + "<br><sup>Cập nhật đến ngày: " + dmax.strftime('%d-%m-%Y') +"</sup>"
                  )
    #show and hide legend on chart
    cfigline.update_layout(showlegend=False)
    
    #switching chart type by toggle button
    if(selected_chart_type==False):
        cfigline.update_yaxes(type="linear")
    else:
        cfigline.update_yaxes(type="log")

    cfigline.update_traces(hovertemplate="%{y} ca") 
    cfigline.update_xaxes(spikecolor="grey", spikedash="dot" ) 

    # styling hover
    if toggle:
        cfigline.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)'),
                               showlegend=False)
    else:
        cfigline.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(0,0,0,0.5)'),
                               showlegend=False) 
    
    #Scatter with play x-axis
    cfigscatter = px.scatter(dffmc, x="total_cases", y="total_deaths",
                              size="population",
                              color="continent", hover_name="location",
                              size_max=60, opacity=0.7,
                              range_x=[100,10000000], range_y=[25,140000],
                              labels={
                                  "total_cases": "Tổng ca nhiễm tích lũy",
                                  "total_deaths":"Tổng ca tử vong",
                                  "total_cases_per_million": "Tỷ lệ nhiễm/1000000 dân",
                                  "location": "Quốc gia",
                                  "continent": "Châu lục"},
                              template=template,
                              title= STitleChart + "<br><sup>Cập nhật đến ngày: " + date_req.strftime('%d-%m-%Y') +"</sup>"
                              )
    cfigscatter.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))

    gfig = px.scatter(
        df[df['date'] == dmax.strftime('%Y-%m-%d')],
        x="gdp_per_capita", #Gross domestic product at purchasing power parity (constant 2011 international dollars), most recent year available
        y="life_expectancy", # Life expectancy at birth in 2019
        size="population",
        color="continent",
        log_x=True,
        size_max=60,
        template=template,
        labels={
            "gdp_per_capita": "Tổng sản phẩm Quốc nội GDP",
            "life_expectancy":"Tuổi thọ bình quân",
            "population": "Dân số",
            "location": "Quốc gia",
            "continent": "Châu lục"
                         },
        title="Gapminder" + 
        "<br><sup>Số liệu thống kê theo các thông tin khác về tuổi thọ bình quân và tổng sản phẩm Quốc nội.</sup>"
    )
    gfig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    
    ####################################################
    return cfigline, cfigscatter, gfig
