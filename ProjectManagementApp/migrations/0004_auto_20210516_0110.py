# Generated by Django 3.1.5 on 2021-05-15 23:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManagementApp', '0003_auto_20210508_0206'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='address',
            field=models.CharField(blank=True, max_length=100, verbose_name='Address'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='company_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Company Name'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='email',
            field=models.CharField(default='', max_length=100, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='name_surname',
            field=models.CharField(default='', max_length=100, verbose_name='Name and Surname'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='phone',
            field=models.CharField(blank=True, max_length=100, verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='projectinvites',
            name='expire_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 26, 1, 9, 58, 932327), verbose_name='Created At'),
        ),
    ]
