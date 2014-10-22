# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_auto_20141022_0705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificateauthority',
            name='website',
            field=models.URLField(null=True, blank=True),
        ),
    ]
