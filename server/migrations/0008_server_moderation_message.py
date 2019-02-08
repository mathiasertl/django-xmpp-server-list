from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0007_server_moderators_notified'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='moderation_message',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
