# Generated by Django 4.2.9 on 2024-06-14 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_alter_empmast_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='machinemast',
            name='devicemodel',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='machinemast',
            name='machineno',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
