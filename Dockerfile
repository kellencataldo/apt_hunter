FROM python:3-alpine

RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add postgresql-dev

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY apt_hunter /apt_hunter/

ENTRYPOINT ["python", "apt_hunter/apt_hunter.py"]
# persist log directory!!!!!


# COPY entrypoint.sh /entrypoint.sh
# RUN chmod 755 /entrypoint.sh
# ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]



