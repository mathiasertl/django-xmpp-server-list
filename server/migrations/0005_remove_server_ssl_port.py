# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_auto_20141022_0709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='ssl_port',
        ),
    ]
