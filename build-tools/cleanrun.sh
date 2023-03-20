#!/usr/bin/bash

cd "${0%/*}"
cd ..

DB_FILE="mumimo.db"

echo "Removing old databases..."
if [ -f "$DB_FILE" ] ; then
    rm "$DB_FILE"
    echo "Removed '$DB_FILE'"
fi

echo "Running Mumimo..."
./mumimo.py -vv --env-file='.env'
