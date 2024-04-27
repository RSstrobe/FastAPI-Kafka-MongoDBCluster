FROM python:3.9
LABEL authors="MosyaginGrigorii"

WORKDIR /opt/etl

ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt requirements.txt
COPY app.py app.py

RUN mkdir -p /opt/etl/logs/ \
    && pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "app.py"]
