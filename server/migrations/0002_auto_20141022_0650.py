# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificateauthority',
            name='display_name',
            field=models.CharField(max_length=30, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='certificateauthority',
            name='name',
            field=models.CharField(unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='server',
            name='ca',
            field=models.ForeignKey(related_name=b'servers', blank=True, to='server.CertificateAuthority', help_text=b'The Certificate Authority of the certificate used in SSL/TLS connections.', null=True, verbose_name=b'CA'),
        ),
    ]
