# Generated by Django 4.2.9 on 2024-09-26 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_monitordata_trid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monitordata',
            name='TRID',
        ),
    ]
