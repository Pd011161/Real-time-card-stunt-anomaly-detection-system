# ใช้ base image เป็น python (เช่น python:3.10-slim)
FROM python:3.10-slim

# ตั้ง working directory
WORKDIR /app

# copy ไฟล์ requirements.txt เพื่อ install dependencies ก่อน (ช่วยให้ build เร็วขึ้นถ้า requirements ไม่เปลี่ยน)
COPY requirements.txt .

RUN pip install uv

# ติดตั้ง dependencies
RUN uv pip install --system -r requirements.txt

# copy โค้ดทั้งหมดเข้าไปใน container
COPY . .

# เปิด port (เช่น 8080 สำหรับ Flask, 8000 ถ้าเป็น FastAPI)
EXPOSE 8080

# คำสั่งรันแอป (สมมติใช้ app.py)
CMD ["python", "app.py"]
