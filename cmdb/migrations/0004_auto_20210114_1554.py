# Generated by Django 3.1.5 on 2021-01-14 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0003_auto_20210114_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostusername',
            name='password',
            field=models.CharField(max_length=32, verbose_name='密码'),
        ),
    ]
