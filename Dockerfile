FROM python:alpine3.9

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /bankAPI
WORKDIR /bankAPI

RUN python3 bankAPI/model/database.py

RUN python3 bankAPI/load_data.py

ENV FLASK_APP=bankAPI

CMD ["flask", "run"]