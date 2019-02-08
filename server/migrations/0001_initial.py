from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateAuthority',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('website', models.URLField(unique=True)),
                ('certificate', models.FilePathField(path=b'core/static/certs', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Certificate authorities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Features',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_muc', models.BooleanField(default=False)),
                ('has_irc', models.BooleanField(default=False)),
                ('has_vcard', models.BooleanField(default=False)),
                ('has_pep', models.BooleanField(default=False)),
                ('has_proxy', models.BooleanField(default=False)),
                ('has_webpresence', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Features',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.PositiveSmallIntegerField(choices=[(50, b'CRITICAL'), (40, b'ERROR'), (30, b'WARNING'), (20, b'INFO'), (10, b'DEBUG')])),
                ('message', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('launched', models.DateField(help_text=b'When the server was launched.')),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('last_checked', models.DateTimeField(null=True, blank=True)),
                ('city', models.CharField(default=b'', max_length=100, null=True, help_text=b'City the server is located in.', blank=True)),
                ('country', models.CharField(default=b'', max_length=100, null=True, help_text=b'Country the server is located in.', blank=True)),
                ('domain', models.CharField(help_text=b'The primary domain of your server.', unique=True, max_length=60)),
                ('website', models.URLField(help_text=b'A homepage where one can find information on your server. If left empty, the default is http://<domain>.', blank=True)),
                ('ssl_port', models.PositiveIntegerField(default=5223, help_text=b'The Port where your server allows SSL connections. Leave empty if your server does not allow SSL connections.', null=True, verbose_name=b'SSL port', blank=True)),
                ('moderated', models.NullBooleanField(default=None)),
                ('software_version', models.CharField(max_length=30, blank=True)),
                ('c2s_srv_records', models.BooleanField(default=False)),
                ('s2s_srv_records', models.BooleanField(default=False)),
                ('ipv6', models.BooleanField(default=False)),
                ('c2s_tls_verified', models.BooleanField(default=False)),
                ('c2s_ssl_verified', models.BooleanField(default=False)),
                ('s2s_tls_verified', models.BooleanField(default=False)),
                ('c2s_auth', models.BooleanField(default=False)),
                ('c2s_caps', models.BooleanField(default=False)),
                ('c2s_compression', models.BooleanField(default=False)),
                ('c2s_register', models.BooleanField(default=False)),
                ('c2s_rosterver', models.BooleanField(default=False)),
                ('c2s_sasl_auth', models.BooleanField(default=False)),
                ('c2s_starttls', models.BooleanField(default=False)),
                ('c2s_starttls_required', models.BooleanField(default=False)),
                ('s2s_starttls', models.BooleanField(default=False)),
                ('s2s_starttls_required', models.BooleanField(default=False)),
                ('s2s_caps', models.BooleanField(default=False)),
                ('s2s_dialback', models.BooleanField(default=False)),
                ('contact', models.CharField(help_text=b'The address where the server-admins can be reached.', max_length=60)),
                ('contact_type', models.CharField(default=b'J', help_text=b'What type your contact details are. This setting will affect how the contact details are rendered on the front page. If you choose a JID or an e-mail address, you will receive an automated confirmation message.', max_length=1, choices=[('M', 'MUC'), ('J', 'JID'), ('E', 'e-mail'), ('W', 'website')])),
                ('contact_name', models.CharField(help_text=b'If you want to display a custom link-text for your contact details, give it here.', max_length=60, blank=True)),
                ('contact_verified', models.BooleanField(default=False)),
                ('ca', models.ForeignKey(related_name='servers', verbose_name=b'CA', to='server.CertificateAuthority', help_text=b'The Certificate Authority of the certificate used in SSL/TLS connections.', on_delete=models.PROTECT)),
                ('features', models.OneToOneField(related_name='server', to='server.Features', on_delete=models.CASCADE)),
            ],
            options={
                'permissions': (('moderate', 'can moderate servers'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerSoftware',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16)),
                ('website', models.URLField()),
                ('newest_version', models.CharField(max_length=8)),
            ],
            options={
                'verbose_name_plural': 'Server software',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='server',
            name='software',
            field=models.ForeignKey(related_name='servers', blank=True, to='server.ServerSoftware', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='user',
            field=models.ForeignKey(related_name='servers', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logentry',
            name='server',
            field=models.ForeignKey(related_name='logs', to='server.Server', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
