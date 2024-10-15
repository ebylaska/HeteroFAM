#!/bin/bash

if [ ! -f /docker-entrypoint-initdb.d/backup/eric9.sql ]; then
    gunzip /docker-entrypoint-initdb.d/backup/eric9.sql.gz
fi

DB_EXISTS=$(mariadb -uhetero -psolid -e "SHOW DATABASES LIKE 'HeteroFAM_Project';" | grep "HeteroFAM_Project" > /dev/null; echo "$?")

if [ "$DB_EXISTS" -eq 1 ]; then
    mariadb -uhetero -psolid HeteroFAM_Project < /docker-entrypoint-initdb.d/backup/eric9.sql
fi

