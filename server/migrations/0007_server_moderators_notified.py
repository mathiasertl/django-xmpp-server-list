from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0006_remove_server_c2s_ssl_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='moderators_notified',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
