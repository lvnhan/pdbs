# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:12:39 2024
@author: NhanLe - Dell
"""

# helpers/plot_helpers.py
import plotly.graph_objects as go

def create_scatter_plot(x, y, title):
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers'))
    fig.update_layout(title=title)
    return fig