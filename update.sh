#!/bin/bash

set -e
set -x

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Error: Please activate the virtualenv."
    exit 1
fi

if [[ -e update.rc ]]; then
    . update.rc
fi

pip install -U -r requirements.txt ${EXTRA_PIP_REQUIREMENTS}
python manage.py migrate
python manage.py collectstatic --noinput

if [[ -n ${UWSGI_EMPEROR} && -e /etc/uwsgi-emperor/vassals/${UWSGI_EMPEROR} ]]; then
    touch /etc/uwsgi-emperor/vassals/${UWSGI_EMPEROR}
fi
