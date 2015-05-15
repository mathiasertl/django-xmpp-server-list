# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list).
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import logging
logging.basicConfig(level=logging.DEBUG)

from fabric.api import local
from fabric.tasks import Task


class DeployTask(Task):
    def run(self, host='hyperion', dir='/usr/local/home/xmpp-server-list/django-xmpp-server-list/',
            group='xmpp-server-list'):
        local('git push origin master')
        ssh = lambda cmd: local('ssh %s sudo sg %s -c \'"cd %s && %s"\'' % (host, group, dir, cmd))
        manage = lambda cmd: ssh('../bin/python manage.py %s' % cmd)
        local('ssh %s sudo chgrp -R %s %s' % (host, group, dir))
        ssh("git fetch")
        ssh("git pull origin master")
        ssh("../bin/pip install -r requirements.txt")
        manage('migrate')
        manage('collectstatic --noinput')
        manage('geoip')
        ssh("touch /etc/uwsgi-emperor/vassals/xmpp-server-list.ini")


deploy = DeployTask()
