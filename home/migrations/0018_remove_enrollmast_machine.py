# Generated by Django 4.2.9 on 2024-06-20 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_alter_monitordata_srno'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollmast',
            name='machine',
        ),
    ]
