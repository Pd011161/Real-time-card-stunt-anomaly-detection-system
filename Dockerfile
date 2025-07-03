# base image -> python
FROM python:3.10-slim

# working directory
WORKDIR /app

# copy requirements.txt 
COPY requirements.txt .

# install uv 
RUN pip install uv

# install dependencies 
RUN uv pip install --system -r requirements.txt

# copy code to container
COPY . .

# open port 
EXPOSE 8080

# run app
CMD ["python", "app.py"]
