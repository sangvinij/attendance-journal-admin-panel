#!/bin/bash

cleanup() {
    echo 'Cleaning up...'
    python project/manage.py shell -c "from accounts.models import User; u = User.objects.filter(username='test_username2'); u.delete()"
}

echo 'Run unit-tests...'
python project/manage.py test accounts
$ echo $?

echo 'Run test to DB, create test user'
pytest . -s
$ echo $?

echo 'Succesful!!!'
trap cleanup EXIT
