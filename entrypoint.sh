#!/bin/sh


connect() {
    PGPASSWORD=${POSTGRES_PASSWORD} psql ${POSTGRES_DB} -h ${POSTGRES_ADDRESS} \
        -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -c '\q';
}

MAX_ATTEMPTS=3
INDEX=0

until connect; do
    if [ $INDEX -eq $MAX_ATTEMPTS ]; then
        >&2 echo "POSTGRES SERVICE CANNOT BE REACHED AFTER ${MAX_ATTEMPTS} ATTEMPTS: EXITING."
        exit 1
    fi
    INDEX=$((INDEX + 1))
    >&2 echo "POSTGRES SERVICE CANNOT BE REACHED: SLEEPING"
    sleep 1
done
    
#if [ "$bool" = true ]; then
#    exec "$@"

