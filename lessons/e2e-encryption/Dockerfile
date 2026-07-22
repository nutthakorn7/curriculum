FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common.py server.py alice.py bob.py ./

ENTRYPOINT ["python", "-u"]
