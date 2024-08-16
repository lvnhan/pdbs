# Chọn hình ảnh cơ sở từ Docker Hub
FROM python:3.10

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép các file yêu cầu vào container
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install pandas first
#RUN pip install numpy==1.22.4
#RUN pip install pandas==1.4.2
#RUN pip install matplotlib==3.5.1
#RUN pip install plotly==5.6.0
#RUN pip install chart-studio==1.1.0

# Cài đặt các thư viện Python yêu cầu
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install plotly --upgrade

# Cài đặt psycopg2-binary
#RUN pip install psycopg2-binary

# Sao chép mã nguồn ứng dụng vào container
COPY . .

# Thực hiện kiểm tra kết nối sau khi build
#RUN python test_connection_sqlalchemy.py

# Xác định lệnh chạy ứng dụng
CMD ["python", "app.py"]

# Cung cấp cổng mà ứng dụng sẽ lắng nghe
# EXPOSE 8050