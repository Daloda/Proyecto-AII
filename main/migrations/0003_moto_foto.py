# Generated by Django 2.0.8 on 2019-01-20 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20190120_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='moto',
            name='foto',
            field=models.CharField(max_length=30, null=True, verbose_name='Photo'),
        ),
    ]
