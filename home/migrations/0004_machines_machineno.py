# Generated by Django 4.2.9 on 2024-05-21 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_companymast_departmast_desmast_empmast'),
    ]

    operations = [
        migrations.AddField(
            model_name='machines',
            name='MachineNo',
            field=models.IntegerField(null=True),
        ),
    ]
