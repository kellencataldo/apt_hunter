FROM python:3-alpine

RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add postgresql-dev
RUN apk add postgresql-client

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# yes I know about WORKDIR, no I won't use it.
RUN mkdir -p /apt_hunter/logs/
RUN mkdir -p /apt_hunter/data/
RUN mkdir -p /apt_hunter/apt_hunter/

COPY ./apt_hunter /apt_hunter/apt_hunter/
COPY ./data/configuration.json /apt_hunter/data/configuration.json
ENV DATA_PATH /apt_hunter/data/configuration.json

COPY entrypoint.sh /apt_hunter/entrypoint.sh
RUN chmod 755 /apt_hunter/entrypoint.sh
CMD ["/bin/sh", "/apt_hunter/entrypoint.sh", "python", "/apt_hunter/apt_hunter/apt_hunter.py"]
