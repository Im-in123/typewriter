# Generated by Django 3.0.8 on 2021-05-27 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('typr_main', '0018_i_imgconvert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imgconvert',
            name='name',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
