# Generated by Django 5.2 on 2025-05-08 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libmanage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(blank=True, max_length=17, verbose_name='ISBN'),
        ),
    ]
