HOST=hyperion
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
	${HOSTCMD} "cd ${XMPPHOME} && sudo make -C ${GITDIR} refresh-geoip"
	${HOSTCMD} sudo /etc/init.d/apache2 restart

refresh-geoip:
	mkdir -p geoip
	wget ${MAXMIND}/GeoLiteCity.dat.gz -O geoip/GeoLiteCity.dat.gz
	gunzip -f geoip/GeoLiteCity.dat.gz
	wget ${MAXMIND}/GeoIPv6.dat.gz -O geoip/GeoLiteCityv6.dat.gz
	gunzip -f geoip/GeoLiteCityv6.dat.gz
