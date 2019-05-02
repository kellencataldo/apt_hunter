FROM python

COPY bootstrap.sh /bootstrap.sh
RUN chmod 755 /entrypoint.sh
RUN ./entrypoint.sh

