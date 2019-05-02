FROM python
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

RUN ./entrypoint.sh

