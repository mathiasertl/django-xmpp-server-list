from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0010_auto_20150311_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
