#!/usr/bin/bash

cd "${0%/*}"
cd ..

echo "Running Mumimo..."
./mumimo.py -vv --env-file='.env'
