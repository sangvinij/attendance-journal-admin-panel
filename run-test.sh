#!/bin/bash
set -e

echo 'Wait...'
sleep 25s

echo 'Run Pytest'
pytest . -s

echo 'Succesful!!!'
