# Generated by Django 3.2.3 on 2021-09-24 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tkt_qtr', '0002_auto_20210924_0952'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ld_phe_duyet',
            old_name='ld_cuc',
            new_name='ld_ten',
        ),
        migrations.RemoveField(
            model_name='ld_phe_duyet',
            name='ld_phong',
        ),
        migrations.AddField(
            model_name='ld_phe_duyet',
            name='ld_cv',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='ld_phe_duyet',
            name='ld_gioi_tinh',
            field=models.CharField(default='', max_length=3),
        ),
    ]
