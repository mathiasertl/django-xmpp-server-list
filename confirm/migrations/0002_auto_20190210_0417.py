# Generated by Django 2.1.5 on 2019-02-10 04:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('confirm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpasswordresetkey',
            name='subject',
        ),
        migrations.DeleteModel(
            name='UserPasswordResetKey',
        ),
    ]
