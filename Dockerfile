FROM python:3-alpine

RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add postgresql-dev
RUN apk add postgresql-client

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /apt_hunter/
WORKDIR /apt_hunter/

RUN mkdir logs/
RUN mkdir data/
RUN mkdir apt_hunter/

COPY ./apt_hunter apt_hunter/
COPY ./data/configuration.json data/configuration.json
ENV DATA_PATH data/configuration.json

COPY entrypoint.sh entrypoint.sh
RUN chmod 755 entrypoint.sh
CMD ["/bin/sh", "entrypoint.sh"]



