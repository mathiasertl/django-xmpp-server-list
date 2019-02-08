from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0008_server_moderation_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='website',
            field=models.URLField(help_text=b'A homepage where one can find information on your server. If left empty, the default is https://<domain>.', blank=True),
            preserve_default=True,
        ),
    ]
