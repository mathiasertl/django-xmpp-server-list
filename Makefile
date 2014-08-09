HOST=hyperion
HOSTCMD=ssh ${HOST}
XMPPHOME=/usr/local/home/xmpp-server-list/
GITDIR=django-xmpp-server-list/

MAXMIND=http://geolite.maxmind.com/download/geoip/database

deploy:
	git push origin master
	${HOSTCMD} "cd ${XMPPHOME}${GITDIR} && sudo git fetch"
	${HOSTCMD} "cd ${XMPPHOME}${GITDIR} && sudo git pull origin master"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/pip install -r ${GITDIR}requirements.txt"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py syncdb --noinput"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py migrate --no-initial-data"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py collectstatic --noinput"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py geoip"
	${HOSTCMD} sudo /etc/init.d/apache2 restart

refresh-geoip:
	python manage.py geoip
