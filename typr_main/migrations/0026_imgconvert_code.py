# Generated by Django 3.0.8 on 2021-05-27 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('typr_main', '0025_auto_20210527_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='imgconvert',
            name='code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
