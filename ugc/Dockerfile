FROM python:3.11.7

WORKDIR /opt/ugc

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev gcc python3-dev musl-dev netcat-traditional\
    && pip install --upgrade pip  \
    && pip install -r requirements.txt --no-cache-dir \
    && apt-get clean

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh", "/opt/ugc/entrypoint.sh"]
# ENTRYPOINT ["/opt/ugc/entrypoint.sh"]
