# Generated by Django 3.0.8 on 2021-05-26 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('typr_main', '0013_images_imageby4'),
    ]

    operations = [
        migrations.RenameField(
            model_name='images',
            old_name='imageby4',
            new_name='imageby',
        ),
        migrations.RemoveField(
            model_name='images',
            name='imageby1',
        ),
        migrations.RemoveField(
            model_name='images',
            name='imageby2',
        ),
        migrations.RemoveField(
            model_name='images',
            name='imageby3',
        ),
    ]
