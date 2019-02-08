from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0009_auto_20150311_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='policy_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='registration_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
