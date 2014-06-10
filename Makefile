HOST=titan
HOSTCMD=ssh ${HOST}
XMPPHOME=/usr/local/home/xmpp-server-list/
GITDIR=django-xmpp-server-list/

MAXMIND=http://geolite.maxmind.com/download/geoip/database

deploy:
	git push origin master
	${HOSTCMD} "cd ${XMPPHOME}${GITDIR} && sudo git pull origin master"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/pip install -r ${GITDIR}requirements.txt"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py syncdb --noinput"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py migrate --no-initial-data"
	${HOSTCMD} "cd ${XMPPHOME} && sudo bin/python ${GITDIR}manage.py collectstatic --noinput"
	${HOSTCMD} "cd ${XMPPHOME} && make -C ${GITDIR} refresh-geoip"
	${HOSTCMD} sudo /etc/init.d/apache2 restart

refresh-geoip:
	mkdir -p geoip
	curl ${MAXMIND}/GeoLiteCity.dat.gz -o geoip/GeoLiteCity.dat.gz
	gunzip -f geoip/GeoLiteCity.dat.gz
