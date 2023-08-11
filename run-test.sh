#!/bin/bash
set -e

echo 'Wait...'
sleep 25s

echo 'Run Pytest'
chmod a+w /project/.pytest_cache
pytest . -s

echo 'Succesful!!!'
