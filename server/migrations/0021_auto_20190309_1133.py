# Generated by Django 2.1.5 on 2019-03-09 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0020_remove_server_city'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificate',
            name='server',
        ),
        migrations.AddField(
            model_name='certificateauthority',
            name='serial',
            field=models.CharField(default='', help_text='The serial of the certificate.', max_length=64),
            preserve_default=False,
        ),
    ]
