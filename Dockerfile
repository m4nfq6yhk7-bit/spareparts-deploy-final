# ใช้ Python 3.11 slim
FROM python:3.11-slim

# ตั้ง working directory
WORKDIR /app

# คัดลอก requirements
COPY requirements.txt .

# อัปเดต pip และติดตั้ง dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY . .

# ตั้งค่า Gunicorn ให้รัน app.py
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "1"]
