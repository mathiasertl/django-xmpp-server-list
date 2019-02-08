# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import confirm.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerConfirmationKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=1, choices=[('J', 'JID'), ('E', 'e-mail')])),
                ('subject', models.ForeignKey(related_name='confirmations', to='server.Server', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserConfirmationKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=1, choices=[('J', 'JID'), ('E', 'e-mail')])),
                ('subject', models.ForeignKey(related_name='confirmations', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, confirm.models.UserConfirmationMixin),
        ),
        migrations.CreateModel(
            name='UserPasswordResetKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=1, choices=[('J', 'JID'), ('E', 'e-mail')])),
                ('subject', models.ForeignKey(related_name='password_resets', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, confirm.models.UserConfirmationMixin),
        ),
    ]
