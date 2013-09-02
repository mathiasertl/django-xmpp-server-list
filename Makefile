HOSTCMD=ssh eris
XMPPHOME=/usr/local/home/xmpplist/
GITDIR=${XMPPHOME}/xmpplist

MAXMIND=http://geolite.maxmind.com/download/geoip/database

deploy:
	git push origin master
	${HOSTCMD} "cd ${GITDIR} && sudo git pull origin master"
	${HOSTCMD} "cd ${GITDIR} && sudo bin/pip install -U -r requirements.txt"
	${HOSTCMD} "cd ${GITDIR} && sudo bin/python manage.py syncdb --noinput"
	${HOSTCMD} "cd ${GITDIR} && sudo bin/python manage.py migrate"
	${HOSTCMD} "cd ${GITDIR} && sudo bin/python manage.py collectstatic --noinput"
	${HOSTCMD} sudo /etc/init.d/apache2 restart

refresh-geoip:
	curl ${MAXMIND}/GeoLiteCountry/GeoIP.dat.gz -o static/geoip/GeoIP.dat.gz
	curl ${MAXMIND}/GeoIPv6.dat.gz -o static/geoip/GeoIPv6.dat.gz
	curl ${MAXMIND}/GeoLiteCity.dat.gz -o static/geoip/GeoLiteCity.dat.gz
	curl ${MAXMIND}/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz -o static/geoip/GeoLiteCityv6.dat.gz

	gunzip static/geoip/GeoIP.dat.gz
	gunzip static/geoip/GeoIPv6.dat.gz
	gunzip static/geoip/GeoLiteCity.dat.gz
	gunzip static/geoip/GeoLiteCityv6.dat.gz
