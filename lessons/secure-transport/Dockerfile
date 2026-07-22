FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gen_certs.py bob.py mitm.py alice.py alice_student.py ./

ENTRYPOINT ["python", "-u"]
