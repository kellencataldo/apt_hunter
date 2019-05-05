FROM python:3-alpine

RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add postgresql-dev

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /apt_hunter/logs/
RUN mkdir -p /apt_hunter/data/
RUN mkdir -p /apt_hunter/apt_hunter/

COPY ./apt_hunter /apt_hunter/apt_hunter/
COPY ./data/configuration.json /apt_hunter/data/configuration.json
ENV DATA_PATH /apt_hunter/data/configuration.json

CMD ["python", "apt_hunter/apt_hunter/apt_hunter.py"]


# COPY entrypoint.sh /entrypoint.sh
# RUN chmod 755 /entrypoint.sh
# ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]



