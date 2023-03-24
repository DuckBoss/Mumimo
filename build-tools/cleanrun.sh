#!/usr/bin/bash

cd "${0%/*}"
cd ..

DB_FILE="mumimo.db"

echo "Removing old databases..."
if [ -f "$DB_FILE" ] ; then
    rm "$DB_FILE"
    echo "Removed '$DB_FILE'"
fi

# Thanks to V.Gamula/Gulzar on stackoverflow for this convenient command:
# https://stackoverflow.com/questions/28991015/python3-project-remove-pycache-folders-and-pyc-files
echo "Removing pycache files..."
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

echo "Running Mumimo..."
./mumimo.py -vv --env-file='.env' --config-file='.config/config.toml' --log-config-file='.config/logging.toml'
