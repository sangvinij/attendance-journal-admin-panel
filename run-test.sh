#!/bin/bash
set -e

echo 'Run Black'
black . --check

echo 'Wait...'
sleep 25s

echo 'Run Pytest'
pytest . -s

echo 'Succesful!!!'
