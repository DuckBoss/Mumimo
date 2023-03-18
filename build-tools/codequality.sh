#!/usr/bin/bash

cd "${0%/*}"
cd ..

echo "Running black[0]: src/"
black src/
echo "Running black[1]: tests/"
black tests/

echo "Running flake8[0]: src/"
echo Errors: $(flake8 src/)
echo "Running flake8[1]: tests/"
echo Errors: $(flake8 tests/)

echo "Running isort: ."
isort .
