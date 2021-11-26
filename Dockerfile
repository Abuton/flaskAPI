FROM python:alpine3.7

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /bankAppServer
WORKDIR /bankAppServer

ENV FLASK_APP=bankAppServer

ENTRYPOINT ["./gunicorn_starter.sh"]