# Generated by Django 5.0.3 on 2024-06-20 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0004_issuedloan_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='collateral',
            name='loan_status',
            field=models.CharField(choices=[('active', 'Active'), ('settled', 'Settled'), ('overdue', 'Overdue')], default='active', max_length=10),
        ),
    ]
