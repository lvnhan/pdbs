# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 14:45:58 2024

@author: Dell
"""
from dash import Dash, page_registry, page_container
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
import os
# select the Bootstrap stylesheets and figure templates for the theme toggle here:

url_theme1 = dbc.themes.SIMPLEX
url_theme2 = dbc.themes.DARKLY

# This stylesheet defines the "dbc" class.  Use it to style dash-core-components
# and the dash DataTable with the bootstrap theme.
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# Tạo đối tượng app

app = Dash(__name__, use_pages=True, external_stylesheets=[url_theme1, dbc_css], suppress_callback_exceptions=True)
server = app.server

theme_toggle = ThemeSwitchAIO(
    aio_id="theme",
    themes=[url_theme1, url_theme2],
    icons={"left": "fa fa-sun", "right": "fa fa-moon"},
)

navbar = dbc.NavbarSimple(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(page["name"], href=page["path"])
                for page in page_registry.values()
                if page["module"] != "pages.not_found_404"
                # module là tên module python được Dash sử dụng khi người dùng truy cập một URL không hợp lệ
                # Chỉ những trang không phải là 404 mới được hiển thị trong DropdownMenu
            ],
            nav=True,
            label="More Pages",
        ),
    ],
    brand="Healhcare App Demo",
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [
          navbar, 
          # theme_toggle, 
          dbc.Row(
              [ 
                  dbc.Col(
                    theme_toggle, 
                    width=12,
                    style={"min-height": "50px", "margin-bottom": "10px"}
                    )
                  ]
              ), 
          page_container
      ], fluid=True, className="dbc"
)

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
    # port = int(os.environ.get("PORT", 8050))  # Lấy cổng từ biến môi trường PORT hoặc dùng 8050 nếu PORT không được đặt
    # app.run_server(host="0.0.0.0", port=port, debug=False, use_reloader=False)

