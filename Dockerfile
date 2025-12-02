FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install PyGithub

COPY . .

ENTRYPOINT ["python", "/app/main.py"]
