# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_auto_20141022_0650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificateauthority',
            name='certificate',
        ),
        migrations.AlterField(
            model_name='certificateauthority',
            name='website',
            field=models.URLField(),
        ),
    ]
