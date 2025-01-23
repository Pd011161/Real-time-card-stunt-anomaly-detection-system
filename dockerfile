# ใช้ base image Python 3.9 (ขนาดเล็กสำหรับ production)
FROM python:3.10-slim

# ตั้งค่า working directory ใน container
WORKDIR /app

# Copy ไฟล์ requirements.txt (ใส่ dependency ของ Python ไว้ที่นี่)
COPY requirements.txt .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ไฟล์ทั้งหมดในโฟลเดอร์ปัจจุบันเข้าไปใน container
COPY . .

# เปิด port ที่ Flask ใช้งาน (5003)
EXPOSE 5003

# คำสั่งรันแอป (ปรับตาม app.py ของคุณ)
CMD ["python", "app.py"]
