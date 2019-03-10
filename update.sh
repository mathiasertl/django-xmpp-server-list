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

# Don't install necessary dependencies, seems unsafe for the general usecase
APT_DEPENDENCIES=zlib1g-dev

if [[ "${INSTALL_APT_DEPENDENCIES}" == "y" ]]; then
    apt-get update
    apt-get install -y ${APT_DEPENDENCIES}

    if [[ -z "${EXTRA_APT_DEPENDENCIES}" ]]; then
        apt-get install -y ${EXTRA_APT_DEPENDENCIES}
    fi
fi

pip install -U -r requirements.txt ${EXTRA_PIP_REQUIREMENTS}
python manage.py migrate
python manage.py collectstatic --noinput

if [[ -n ${UWSGI_EMPEROR} && -e /etc/uwsgi-emperor/vassals/${UWSGI_EMPEROR} ]]; then
    touch /etc/uwsgi-emperor/vassals/${UWSGI_EMPEROR}
fi
