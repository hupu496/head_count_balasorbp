# Generated by Django 4.2.9 on 2025-05-22 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_monitordata_trid'),
    ]

    operations = [
        migrations.CreateModel(
            name='GatePass',
            fields=[
                ('allowing_entry', models.CharField(choices=[('Yes', 'Hazardous Area'), ('No', 'Non Hazardous Area')], max_length=10)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('cardNo', models.CharField(max_length=250)),
                ('date', models.DateField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('company', models.CharField(blank=True, max_length=250, null=True)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('mobile', models.CharField(blank=True, max_length=250, null=True)),
                ('vehicleNo', models.CharField(blank=True, max_length=250, null=True)),
                ('purpose', models.TextField()),
                ('noOfPerson', models.CharField(blank=True, max_length=250, null=True)),
                ('idNo', models.CharField(blank=True, max_length=250, null=True)),
                ('typeOf', models.CharField(blank=True, max_length=250, null=True)),
                ('govt_id', models.CharField(blank=True, max_length=250, null=True)),
                ('govtno', models.CharField(blank=True, max_length=250, null=True)),
                ('personToMeet', models.CharField(blank=True, max_length=250, null=True)),
                ('inTime', models.CharField(blank=True, max_length=250, null=True)),
                ('outTime', models.CharField(blank=True, max_length=250, null=True)),
                ('permittedBy', models.CharField(blank=True, max_length=250, null=True)),
                ('carringGadget', models.CharField(blank=True, max_length=250, null=True)),
                ('passNo', models.CharField(blank=True, max_length=250, null=True)),
                ('image', models.ImageField(default='default.jpg', upload_to='gatepass_images/')),
                ('remarks', models.TextField(blank=True, null=True)),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('renew_remarks', models.TextField(blank=True, max_length=250, null=True)),
                ('createdAt', models.DateField(blank=True, null=True)),
                ('updatedAt', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='true', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='ReportLog',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('addedon', models.DateTimeField(auto_now_add=True, null=True)),
                ('Status', models.IntegerField(default=1)),
            ],
        ),
    ]
