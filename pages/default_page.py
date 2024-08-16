import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__, 
    path='/',
    name='Landing page',
    title='Coronavirus Pandemi',
    )
# path='/': URL gốc của ứng dụng
# path='/404': trang lỗi hoặc trang không tìm thấy

# Layout của trang
layout = html.Div(
    style={
        "background-color": "rgba(0, 0, 0, 0)",
        "background-image": "url('/assets/covid19.png')",  # Đường dẫn tới hình ảnh trong thư mục assets
        "background-size": "33%",  # Giữ nguyên kích thước gốc của hình ảnh: "auto"
        "background-position": "left bottom",  # Đặt hình ảnh ở góc dưới bên trái
        "background-repeat": "no-repeat",  # Không lặp lại hình ảnh
        "display": "flex",
        "flex-direction": "column",
        "justify-content": "center",
        "align-items": "center",
        "height": "80vh",
        "font-family": "Segoe UI"
    },
    children=[
        html.H1(
            "THEO DÕI TÌNH HÌNH DỊCH BỆNH",
            style={
                "text-align": "center",
                "margin-bottom": "30px",
                "font-weight": "semibold",
                "letter-spacing": "-1px"
            }
        ),
        html.Div(
            style={"margin-bottom": "20px", "text-align": "center"},
            children=[
                html.H2(
                    "Coronavirus Pandemic in the World",
                    style={"font-weight": "light", "letter-spacing": "-1px"}
                ),
                html.P(
                    "Tình hình dịch bệnh trên thế giới. Dữ liệu minh họa được lấy từ OWID",
                    style={"margin-bottom": "3px"}
                ),
                dbc.Button(
                    "Xem thêm",
                    href="/your-first-page-url",  # Thay bằng URL tương ứng cho trang thứ nhất
                    color="primary",
                    className="mt-3 mb-5"
                )
            ]
        ),
        html.Div(
            style={"text-align": "center"},
            children=[
                html.H2(
                    "Coronavirus Pandemic in Viet Nam",
                    style={"font-weight": "light", "letter-spacing": "-1px"}
                ),
                html.P([
                    "Tình hình dịch bệnh tại các tỉnh thành phố của Việt Nam.",
                    html.Br(),
                    "Dữ liệu chỉ mang tính chất minh họa, không phải là dữ liệu thật."
                    ],
                    style={"margin-bottom": "3px"}
                ),
                dbc.Button(
                    "Xem thêm",
                    href="/your-second-page-url",  # Thay bằng URL tương ứng cho trang thứ hai
                    color="primary",
                    className="mt-3 mb-5"
                )
            ]
        ),
    ]
)
