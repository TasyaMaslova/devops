FROM mysql:8.0

COPY films2_dump.sql /docker-entrypoint-initdb.d/

