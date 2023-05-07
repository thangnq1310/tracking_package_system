FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN apt-get -y install supervisor

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD [ "python", "main.py" ]