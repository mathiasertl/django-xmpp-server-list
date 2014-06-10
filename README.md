This is a small [Django](https://www.djangoproject.com/) project to create the
list of servers at https://list.jabber.at.

It requires Python 2.7, Django and a WSGI server to run. As a normal Django
project, it can use MySQL, PostgreSQL and others as a database backend and runs
with any WSGI compatible webserver (apache, nginx, lighttpd, uWSGI, ...).

Installation
============

Simply clone the repository, create a virtualenv and install the dependencies:

```
git clone https://github.com/mathiasertl/django-xmpp-server-list.git
cd django-xmpp-server-list
virtualenv .
source bin/activate
pip install -r requirements.txt
```

You also need to refresh the GeoIP database:

```
make refresh-geoip
```

Deployment
==========

This software is a normal Django app. Please refer to Django's documentation on
deployment options.

License
=======

This project is licensed as [GPLv3 or
later](http://www.gnu.org/copyleft/gpl.html).
