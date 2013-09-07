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
	mkdir -p geoip

	curl ${MAXMIND}/GeoLiteCountry/GeoIP.dat.gz -o geoip/GeoIP.dat.gz
	curl ${MAXMIND}/GeoIPv6.dat.gz -o geoip/GeoIPv6.dat.gz
	curl ${MAXMIND}/GeoLiteCity.dat.gz -o geoip/GeoLiteCity.dat.gz
	curl ${MAXMIND}/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz -o geoip/GeoLiteCityv6.dat.gz

	gunzip geoip/GeoIP.dat.gz
	gunzip geoip/GeoIPv6.dat.gz
	gunzip geoip/GeoLiteCity.dat.gz
	gunzip geoip/GeoLiteCityv6.dat.gz
