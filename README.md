[![Flattr this git
repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=mathiasertl&url=https://jabber.at)

This is a small [Django](https://www.djangoproject.com/) project to create the
list of servers at https://list.jabber.at. Since this project is free software,
you are welcome to host your own list, if you like.

It requires Python 2.7, Django and a WSGI server to run. As a normal Django
project, it can use MySQL, PostgreSQL and others as a database backend and runs
with any WSGI compatible webserver (apache, nginx, lighttpd, uWSGI, ...).

Features
========

Primary feature is that server admins can submit their data mostly
autonomously, formal aspects (e.g. SRV records, TLS, ...) are checked
automatically. Admin users only have to verify contact details.

On the todo list is a possibility to display XMPP features and limit the list
to servers with particular features.

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
