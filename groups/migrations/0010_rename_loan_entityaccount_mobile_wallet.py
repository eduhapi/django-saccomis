# Generated by Django 5.0.3 on 2024-07-18 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0009_alter_entityaccount_entity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entityaccount',
            old_name='loan',
            new_name='mobile_wallet',
        ),
    ]
