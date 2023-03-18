#!/usr/bin/bash

cd "${0%/*}"

echo "Running black[0]: src/"
black ../src/
echo "Running black[1]: tests/"
black ../tests/

echo "Running flake8[0]: src/"
flake8 ../src/
echo "Running flake8[1]: tests/"
flake8 ../tests/

echo "Running isort: ."
isort ../
