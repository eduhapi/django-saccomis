# Generated by Django 5.0.3 on 2024-06-29 05:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('loans', '0006_issuedloan_loan_balance_issuedloan_loan_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issuedloan',
            name='member',
        ),
        migrations.AddField(
            model_name='issuedloan',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issuedloan',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
