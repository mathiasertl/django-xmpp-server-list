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

CELERY_CONF_NAME=xmpp-server-list-celery.conf
CELERY_CONF_DEST=/etc/conf.d/${CELERY_CONF_NAME}
CELERY_SERVICE_NAME=xmpp-server-list-celery.service
CELERY_SERVICE_DEST=/etc/systemd/system/${CELERY_SERVICE_NAME}
TMPFILE_NAME=xmpp-server-list.conf
TMPFILE_DEST=/etc/tmpfiles.d/xmpp-server-list.tmpfiles.conf
UWSGI_NAME=xmpp-server-list.ini
UWSGI_DEST=/etc/uwsgi-emperor/vassals/${UWSGI_NAME}

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

# create/chown log dir
mkdir -p /var/log/xmpp-server-list
chown xmpp-server-list:xmpp-server-list /var/log/xmpp-server-list

# install tmpfiles
if [[ ! -e ${TMPFILE_DEST} ]]; then
    ln -s `pwd`/files/tmpfiles/${TMPFILE_NAME} ${TMPFILE_DEST}
fi

# install celery service
if [[ ! -e ${CELERY_SERVICE_DEST} ]]; then
    ln -s `pwd`/files/celery/${CELERY_SERVICE_NAME} ${CELERY_SERVICE_DEST}
fi
if [[ ! -e ${CELERY_CONF_DEST} ]]; then
    ln -s `pwd`/files/celery/${CELERY_CONF_NAME} ${CELERY_CONF_DEST}
fi

systemctl daemon-reload
systemd-tmpfiles --create
systemctl enable ${CELERY_SERVICE_NAME}
systemctl restart ${CELERY_SERVICE_NAME}

# copy uwsgi file - automatically restarts because of emperor
cp files/uwsgi/${UWSGI_NAME} ${UWSGI_DEST}
