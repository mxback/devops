# Generated by Django 3.1.5 on 2021-01-14 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='sex',
            field=models.IntegerField(blank=True, choices=[(0, '男'), (1, '女')], null=True, verbose_name='性别'),
        ),
    ]
