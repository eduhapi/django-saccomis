# Generated by Django 5.0.3 on 2024-07-12 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_alter_mpesareconciliationledger_reconciled_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpesareconciliationledger',
            name='completion_date',
            field=models.CharField(max_length=50),
        ),
    ]
