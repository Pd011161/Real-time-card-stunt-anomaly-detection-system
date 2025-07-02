FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --prefer-binary -r requirements.txt

COPY . .
# EXPOSE 5003

CMD ["python", "app.py"]
