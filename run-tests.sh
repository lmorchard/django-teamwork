#!/bin/sh
clear
pep8 -r teamwork/*py teamwork/tests/*py
coverage run ./teamwork_example/manage.py test -v1 teamwork
coverage html -i
coverage report
