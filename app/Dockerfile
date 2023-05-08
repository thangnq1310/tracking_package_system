FROM python:3.10.5-slim-buster

WORKDIR /app

RUN apt-get -y update && apt-get -y install supervisor

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY supervisor/ /etc/supervisor/supervisor.d/

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
