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
	curl ${MAXMIND}/GeoLiteCity.dat.gz -o geoip/GeoLiteCity.dat.gz
	gunzip -f geoip/GeoLiteCity.dat.gz
