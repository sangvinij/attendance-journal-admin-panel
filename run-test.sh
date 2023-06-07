#!/bin/bash

echo 'Wait...'
sleep 25s

echo 'Run Pytest'
pytest . -s
if [[ $? == 1 ]]; then exit 1; fi

echo 'Succesful!!!'
