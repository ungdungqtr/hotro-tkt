# Generated by Django 3.2.3 on 2022-03-14 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tkt_qtr', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='canbo',
            options={'permissions': (('canbo_view', 'CanBo View'), ('canbo_add', 'CanBo Add'), ('canbo_edit', 'CanBo Edit'), ('canbo_delete', 'CanBo Delete'))},
        ),
    ]