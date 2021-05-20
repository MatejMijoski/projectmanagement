# Generated by Django 3.1.5 on 2021-05-16 20:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManagementApp', '0004_auto_20210516_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='address',
            field=models.CharField(blank=True, max_length=200, verbose_name='Client Address'),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(default='email@email.com', max_length=254, verbose_name='Client Email'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projectinvites',
            name='expire_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 26, 22, 48, 32, 788009), verbose_name='Created At'),
        ),
        migrations.DeleteModel(
            name='ClientAddress',
        ),
    ]
