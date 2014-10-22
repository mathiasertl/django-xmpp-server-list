# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_remove_server_ssl_port'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='c2s_ssl_verified',
        ),
    ]
