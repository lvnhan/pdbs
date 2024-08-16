# Chọn hình ảnh cơ sở từ Docker Hub
FROM python:3.10

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép các file yêu cầu vào container
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Cài đặt các thư viện Python yêu cầu
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn ứng dụng vào container
COPY . .

# Xác định lệnh chạy ứng dụng
CMD ["python", "app.py"]
