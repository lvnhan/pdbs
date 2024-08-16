# -*- coding: utf-8 -*-
"""
Created on Fri May 27 16:54:00 2022

@author: lvietnhan
"""
import pandas as pd
import geopandas as gpd
from dash import dcc, html, Input, Output, register_page, callback #Dash
import dash
import plotly.express as px

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dependencies import State

# hide warining in future
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

register_page(
    __name__,
    path='/hc_govn',
    name='Vietnam',
    title='Plotly.Dash Coronavirus Pandemic (VN)',
    description='Coronavirus Pandemic in Vietnam'
    )
#from hc_govn_layout import govn_layout
###############################################################################
#Preparing for page template
template_theme1 = "simplex"
template_theme2 = "darkly"

url_theme1 = dbc.themes.SIMPLEX
url_theme2 = dbc.themes.DARKLY
# dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
# app = Dash(__name__, external_stylesheets=[url_theme1, dbc_css], suppress_callback_exceptions=True)
# app.title = "Plotly.Dash Coronavirus Pandemic (VN)"
###############################################################################
#UDF Discrete Colors Range - using for discrete color bar
#categorizing the number of cases and assign each category to each row
def CurConfDiscreteColors(val):
    if val <= 100:
        return "0-100" #FEF5F9
    elif val <= 500:
        return "101-500" #F2E4EC
    elif val <= 1000:
        return  "501-1,000" #E4D1DE
    elif val <= 5000:
        return "1,001-5,000" #D0BAC2
    elif val <= 10000:
        return "5,001-10,000" #BE9293
    elif val <= 50000:
        return "10,001-50,000" #AA4E51
    elif val <= 100000:
        return "50,001-100,000" #A2171C
    elif val <= 500000:
        return "100,001-500,000" #921316
    elif val <= 500000:
        return "500,001-1,000,000" #921316    
    else:#>1,000,000
        return "Trên 1,000,000" #430000   
RedColor_discrete_map={'0-100':'#FEF5F9', '101-500':'#F2E4EC','501-1,000':'#E4D1DE',
                       '1,001-5,000':'#D0BAC2','5,001-10,000':'#BE9293',
                       '10,001-50,000':'#AA4E51','50,001-100,000':'#A2171C',
                       '100,001-500,000':'#921316', '500,001-1,000,000':'#921316', 'Trên 1,000,000':'#430000'}
BlueColor_discrete_map={'0-100':'#FFF7FB', '101-500':'#ECE7F2','501-1,000':'#D0D1E6',
                       '1,001-5,000':'#A6BDDB','5,001-10,000':'#74A9CF',
                       '10,001-50,000':'#3690C0','50,001-100,000':'#0570B0',
                       '100,001-500,000':'#045A8D', '500,001-1,000,000':'#023858', 'Trên 1,000,000':'#012337'}

ConfDColorsOrder={"ConfDColors": [
    '0-100',
    '101-500',
    '501-1,000',
    '1,001-5,000',
    '5,001-10,000',
    '10,001-50,000',
    '50,001-100,000',
    '100,001-500,000',
    '500,001-1,000,000',
    'Trên 1,000,000'
    ]}
def ConfDiscreteColors(val):
    if val <= 10:
        return "0-10" #fff7ec
    elif val <= 100:
        return "11-100" #fc8d59
    elif val <= 500:
        return  "101-500" #ef6548
    elif val <= 1000:
        return "501-1,000" #d7301f
    elif val <= 2000:
        return "1,001-2,000" #b30000
    elif val <= 5000:
        return "2,001-5,000" #990000
    else:#>5000
        return "trên 5,000" #7f0000    
#color_discrete_map={'0-10':'#fff7ec', '11-100':'#fc8d59','101-500':'#ef6548','501-1,000':'#d7301f','1,001-2,000':'#b30000','2,001-5,000':'#990000','trên 5,000':'#7f0000'}
###############################################################################
color_scale = {
    'Confirmed': [(0, "#fff7ec"), (0.1,"#ef6548"), (0.2,"#d7301f"), (0.4, "#b30000"),  (1, "#7f0000")],#'redor', 
    'Deaths':'greys', 
    'Dan_So': [(0, "#c3daee"), (0.5, "#0570b0"), (1, "#093c57")] , #'blues', 
    'Recovered': [(0, "#d8f0d3"), (0.5, "#36a157"), (1, "#013716")] #'greens' 
    }
###############################################################################
#UDF will be call from dropdown | CheckBox | radioItems
def get_dfopts(slabel, svalue, sall):
    lst = data_slave[[slabel, svalue]]
    lst.set_index(svalue)
    lst = lst.drop_duplicates()
    dict_list = [{'label': sall, 'value': 'all'}]
    lst.sort_values([svalue], ascending=[True], inplace=True)
    
    options_dict = dict(zip(lst[slabel], lst[svalue]))
    for word, tag in options_dict.items():
        dict_list.append({'label':word,'value':tag}) #, 'disabled': False
    return dict_list
###############################################################################
def get_dfopts_cb(slabel, svalue, sall, sfw, sw):
    #sfw: field for criteria with sw. For example: 
    #get_dfopts_cb('Location', 'ISOCode', 'Tất cả Tỉnh/TP', 'VNAreaID', '1')
    
    lst = data_slave[[slabel, svalue, sfw]]
    lst.set_index(sfw)
    lst = lst.drop_duplicates()
    dict_list = [{'label': sall, 'value': 'all'}]
    for index, row in lst.iterrows():
        if row[sfw]==sw:#sw
            dict_list.append({'label':row[slabel],'value':row[svalue]}) 
        else:
            dict_list.append({'label':row[slabel],'value':row[svalue],'disabled': True}) 
    return dict_list
###############################################################################
#Prepare geodataframe
url_json = "./shp/diaphanhuyen.shp" # shape file for VN map
#['OBJECTID', 'f_code', 'Ten_Tinh', 'Ten_Huyen', 'Dan_So', 'Nam_TK','Code_vung', 'geometry']
geojson = gpd.read_file(url_json, encoding="utf-8") #Read with UTF-8 and load to geodataframe
geojson['ProvCode'] = geojson['Code_vung'].str.slice(0,2)
geojson.set_index('Code_vung')

###############################################################################
#Prepare dataframe with data visualation
url_data ="./data/Covid-VN-ByProvince-AdmCode.csv"
#ISOCode,Location,Location-en,RecDtm,Confirmed,Recovered,Deaths,WaveID,ProvCode,HASC,Latitude,Longtitude,VNAreaID,Domain,Domain-en,RegionID,RegionCode,Region,Region-en
#cols_to_read = ['ISOCode', 'Location', 'RecDtm', 'Confirmed', 'WaveID', 'ProvCode', 'HASC', 'HASC', 'Latitude', 'Longtitude', 'VNAreaID', 'Domain', 'RegionID', 'RegionCode', 'Region','ConfDColors']

data_slave = pd.read_csv(url_data, parse_dates=True, dtype={'ProvCode':'string'})
data_slave.index = pd.to_datetime(data_slave['RecDtm'])
###############################################################################
# Merge beween geojson & master to get ISOCode column
full_dataset = geojson.merge(data_slave, #map_df merge to df
                             left_on=['ProvCode'],
                             right_on=['ProvCode'])
full_dataset.set_index("ISOCode")
dfw = full_dataset[['WaveID']].drop_duplicates().reset_index(drop=True)
#Prepare dataset for plots
ds = full_dataset[['ISOCode', 'Location', 'Dan_So', 'Confirmed', 'Recovered', 'Deaths', 'WaveID', 'ProvCode', 'VNAreaID', 'Domain', 'RegionID', 'RegionCode', 'Region','ConfDColors']]

###############################################################################
sdefLocs = 'all' #default value for Single choice
mdefLocs = ['all'] #default value for multi-choice ['VN-SG']
###############################################################################
#local style HTML
colors = {
    'pl.bkground': 'rgba(0, 0, 0, 0)',
    'pg.bkground': 'rgba(0, 0, 0, 0)',
    'drop.bkg': '#1E1E1E',
    'text.light': '#B6B6B6',
    'text.note': '#989898',
    'text.dark': '#000000'
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
###############################################################################
# pass variables
title = ['Bảng đồ cấp độ dịch tại Việt Nam', 'STATISTIC DATA']
stitle= ['Dữ liệu chỉ mang tính chất minh họa','Visualising data with Plotly - Dash']
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
bottom = html.P("© 2022 LAC VIET Computing Corp.")
###############################################################################
switch = html.Div([
    dbc.Row([
        dbc.Col(
            children=[
                html.Sup("Coronavirus Pandemic (COVID-19).", style={'font-weight': 'bold'}),
                html.Sup(" Dữ liệu minh họa trong các đợt dịch bùng phát tại các Tỉnh-Thành phố.")
            ],
            xs=12, sm=12, md=12
        ),
        # dbc.Col(
        #     html.Div([
        #         html.Div(id="switch-result", children=["Màn hình sáng"], style={'display': 'inline-block', 'font-size': '12', 'margin-right': '10px'}),
        #         html.Div(ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2], icons={"left": "{%}", "right": "{%}"}), style={'display': 'inline-block'})
        #     ], style={'textAlign': 'right'}),
        #     xs=12, sm=12, md=3
        # )
    ])
])
###############################################################################
# Define criterias
# Wave slider
waveSlider = dcc.Slider(
    dfw['WaveID'].min(),
    dfw['WaveID'].max(),
    step=None,
    value=dfw['WaveID'].min(),#polar_ds['WaveID'].min(),
    marks={str(wid): str(wid) for wid in dfw['WaveID'].unique()},
    id='wave-slider'
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

crictrl = html.Div([dbc.Row([
    dbc.Col(html.Div(children=[html.Sup('Các đợt dịch bùng phát'), waveSlider], className="mt-0"),  xs=12, sm=12, md=3),
    dbc.Col(html.Div(children=[
        dcc.Dropdown(
            options=get_dfopts('Region', 'RegionID', 'Tất cả vùng'),
            multi=False,
            value=sdefLocs,#defLocs,
            placeholder="Chọn vùng",
            id="area",
            style={#'backgroundColor': colors['drop.bkg'],
                   'font-family': fontnames['u'],
                   'font-size': fontsz['f14']
                   },
            )
        ], className="mt-1"),  xs=12, sm=12, md=3),
    dbc.Col(html.Div(children=[
        dcc.Dropdown(
            options=get_dfopts('Domain', 'VNAreaID', 'Tất cả tiểu vùng'),
            multi=False,
            value=sdefLocs,
            placeholder="Chọn tiểu vùng",
            id="sub-area",
            style={#'backgroundColor': colors['drop.bkg'],
                   'font-family': fontnames['u'],
                   'font-size': fontsz['f14']
                   },
            )
        ], className="mt-1"),  xs=12, sm=12, md=3),
    dbc.Col(html.Div(children=[
        dcc.Dropdown(
            options=get_dfopts('Location', 'ISOCode', 'Tất cả Tỉnh Thành'),
            multi=True,
            value=mdefLocs,
            placeholder="Chọn Tỉnh/Thành phố",
            id='locselector',
            style={#'backgroundColor': colors['drop.bkg'],
                   'font-family': fontnames['u'],
                   'font-size': fontsz['f14']
                   },
            className='locselector')
        ], className="mt-1"),  xs=12, sm=12, md=3), # xs: rất nhỏ | sm: nhỏ | md: màn hình trung bình
    dbc.Col(xs=0, sm=0, md=1),
    ])],style={'font-family': fontnames['u']})
###############################################################################

cgraph = {
    'map':html.Div(dcc.Graph(id="graph", style={'height': '100%', 'width': '100%'}), className="m-1", style={'height': '100%', 'width': '100%', 'position': 'relative'}),#, 'border': '2px solid red'
    }

###############################################################################

layout = dbc.Container(children=[
    dbc.Row(
        [
            dbc.Col(xs=0, sm=0, md=1),
            dbc.Col(
                [
                    header,
                    switch,
                ], xs=12, sm=12, md=10
            ),
            dbc.Col(xs=0, sm=0, md=1)
        ], 
        ),
    dbc.Row(
        [
            dbc.Col(xs=0, sm=0, md=1),
            dbc.Col(crictrl, xs=12, sm=12, md=10),
            dbc.Col(xs=0, sm=0, md=1)
        ], 
        ),#row_content_plot
    dbc.Row(
        [
        dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(html.Div(cgraph['map'], 
                         # style={'height': 'calc(100vh - 60px)', 'width': '100%'},
                         style={'height': '100%', 'width': '100%'},
                         # style={'height': '600px'},
                         #className='bg-info'
                         ), xs=12, sm=12, md=10, 
                # style={'height': 'calc(100vh - 60px)', 'border': '2px solid green'}
                style={'height': '100%'}
                ), 
        dbc.Col(xs=0, sm=0, md=1),
        ], style={'height': 'calc(100vh - 60px)'}, 
        ),
    dbc.Row(
        [
        dbc.Col(xs=0, sm=0, md=1),
        dbc.Col(bottom, xs=12, sm=12, md=10),
        dbc.Col(xs=0, sm=0, md=1)
        ], 
        ),
    ],
    className="mt-1 dbc", #m-4
    fluid=True, # tương thích với các màn hình khác nhau
    )
@callback(
    Output('sub-area', 'value', allow_duplicate=True),
    [Input('sub-area', 'value')],
    [State('area', 'options')],
    [Input('area', 'value')],
    [State('area', 'options')],
    prevent_initial_call='initial_duplicate'
    )
def lstcallback_sarea(selected_subarea, opts1, selected_area,  opts2):
    lst = data_slave[['Domain', 'VNAreaID', 'RegionID']].drop_duplicates()
    if selected_subarea == sdefLocs:
        return selected_subarea
    
    # Lọc các hàng có RegionID phù hợp
    filtered_lst = lst[lst['RegionID'] == selected_area]
    
    if not filtered_lst.empty:
        # Kiểm tra nếu selected_subarea là hợp lệ
        if selected_subarea not in filtered_lst['VNAreaID'].values:
            return filtered_lst.iloc[0]['VNAreaID']  # Trả về giá trị hợp lệ đầu tiên
    return selected_subarea

@callback(
    Output('sub-area', 'options', allow_duplicate=True),
    Output('locselector', 'options', allow_duplicate=True),
    Input('area', 'value'),
    Input('sub-area', 'value'),
    prevent_initial_call='initial_duplicate'
    )
def set_subareas_options(selected_area, selected_subarea):
    if selected_area == sdefLocs:  # Nếu vùng là "Tất cả vùng"
        subarea_opts = get_dfopts('Domain', 'VNAreaID', 'Tất cả tiểu vùng')
    else:  # Nếu vùng cụ thể được chọn
        subarea_opts = get_dfopts_cb('Domain', 'VNAreaID', 'Tất cả tiểu vùng', 'RegionID', selected_area)
    
    # Xác định tùy chọn địa điểm dựa trên điều kiện của tiểu vùng
    if selected_subarea == sdefLocs:
        if selected_area == sdefLocs:
            loc_opts = get_dfopts('Location', 'ISOCode', 'Tất cả Tỉnh Thành')
        else:
            loc_opts = get_dfopts_cb('Location', 'ISOCode', 'Tất cả Tỉnh Thành', 'RegionID', selected_area)
    else:
        loc_opts = get_dfopts_cb('Location', 'ISOCode', 'Tất cả Tỉnh Thành', 'VNAreaID', selected_subarea)
    
    return subarea_opts, loc_opts

#Check and remove 'all' element from selected items of dropdown list
@callback(
    Output('locselector', 'value', allow_duplicate=True),
    [Input('locselector', 'value')],
    [State('locselector', 'options')],
    prevent_initial_call='initial_duplicate'
    )
def lstcallback(selected_loc, opts):
    if 'all' in selected_loc:
        if len(selected_loc) > 1:  # Nếu 'all' được chọn cùng với các lựa chọn khác
            selected_loc = [loc for loc in selected_loc if loc != 'all']
    return selected_loc

#Check data validation from options list components
@callback(
    #Output("switch-result", 'children'),
    Output("graph", "figure", allow_duplicate=True), 
    Input('wave-slider', 'value'),
    Input('area', 'value'),
    Input('sub-area', 'value'),
    Input('locselector', 'value'),
    Input('graph','clickData'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    prevent_initial_call='initial_duplicate'
    )
def display_graphs(selected_wave, selected_area, selected_subarea, selected_loc, click_data, toggle):

    global ds
    ctx =dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    template = template_theme1 if toggle else template_theme2
    s='Màn hình sáng' if toggle else 'Màn hình tốt'
    
    if trigger_id in ['wave-slider', 'area', 'sub-area', 'locselector'] or trigger_id is None:
        ds = full_dataset[full_dataset['WaveID'] == selected_wave]
        
        # Áp dụng bộ lọc cho 'RegionID' nếu selected_area khác sdefLocs
        if selected_area != sdefLocs:
            ds = ds[ds['RegionID'] == selected_area]
        
        # Áp dụng bộ lọc cho 'VNAreaID' nếu selected_subarea khác sdefLocs
        if selected_subarea != sdefLocs:
            ds = ds[ds['VNAreaID'] == selected_subarea]
        
        # Áp dụng bộ lọc cho 'ISOCode' nếu selected_loc khác mdefLocs
        if selected_loc != mdefLocs:
            ds = ds[ds['ISOCode'].isin(selected_loc)]
            
    # Tạo fig choropleth
    fig = px.choropleth(
        ds, geojson=ds.geometry,
        hover_name="Location", 
        color="ConfDColors",
        locations=ds.index,
        custom_data=["ISOCode", "Location", "Ten_Huyen", 
                     "Confirmed", "Recovered", "Deaths", "Dan_So"],
        color_discrete_map=RedColor_discrete_map,
        category_orders=ConfDColorsOrder,
        labels={
            'ISOCode': 'iso',
            'location': 'Tỉnh/TP',
            'Ten_Huyen': 'Quận/Huyện/Thị xã',
            'Confirmed': 'Ca nhiễm',
            'Recovered': 'Phục hồi',
            'Deaths': 'Ca tử vong',
            'Dan_So': 'Dân số',
            'ConfDColors': 'Ca nhiễm tích lũy'
        },
    )
    
    # Tạo hovertemplate
    hovertemp = (
        "<b>%{customdata[0]}: %{customdata[1]}-%{customdata[2]}</b><br>"
        "Dân số: %{customdata[6]:,.0f}<br>"
        "Ca nhiễm tích lũy: %{customdata[3]:,.0f}<br>"
        "Ca phục hồi: %{customdata[4]:,.0f}<br>"
        "Ca tử vong tích lũy: %{customdata[5]:,.0f}"
    )
    fig.update_traces(
        hovertemplate=hovertemp,
        marker_line=dict(width=0.5, color="#d6d6d6"),  # Cập nhật độ rộng và màu của đường viền
        #hoverlabel=dict(bgcolor='rgba(125, 125,125, 0.6)')  # Cập nhật nền của hover với độ trong suốt
    )
    
    # Cập nhật layout của map
    fig.update_layout(
        showlegend=True,
        legend_title_text='<b>Số ca nhiễm/1 triệu dân</b>',
        font={"size": 11, "color": "#808080", "family": "Segoe UI"},
        legend=dict(
            orientation='v',
            yanchor="top", y=0.9, 
            xanchor="left", x=0.01,
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", 
            borderwidth=0, itemclick="toggleothers",
        ),
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#e0fffe'),
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0, pad=0, autoexpand=True),
        height=600,
    )
    
    # Zoom map vào khu vực cần thiết
    fig.update_geos(fitbounds="locations", resolution=110, visible=False)
    
    fig.update_layout(template=template)
    
    return fig#, location 

# layout = app.layout  # Export layout for the main app
# # app.layout = govn_layout
# if __name__ == "__main__":
#     # app.run_server(port=8052, debug=True, use_reloader=False)    
#     app.run_server(debug=True, use_reloader=False)
