# Generated by Django 3.2.25 on 2024-10-09 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0025_alter_monitordata_errorstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitordata',
            name='Errorstatus',
            field=models.IntegerField(default=0),
        ),
    ]
