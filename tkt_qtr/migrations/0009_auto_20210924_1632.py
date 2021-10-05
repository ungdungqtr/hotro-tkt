# Generated by Django 3.2.3 on 2021-09-24 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tkt_qtr', '0008_rename_qd_cancuqd'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanCu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('so_qd', models.CharField(default='', max_length=25)),
                ('ten_qd', models.CharField(default='', max_length=255)),
                ('ngay_qd', models.DateField()),
            ],
        ),
        migrations.DeleteModel(
            name='CanCuQD',
        ),
    ]
