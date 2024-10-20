# Generated by Django 5.0.3 on 2024-06-19 03:43

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collateral',
            name='guarantee_amount',
        ),
        migrations.RemoveField(
            model_name='collateral',
            name='guarantor',
        ),
        migrations.AlterField(
            model_name='collateral',
            name='collateral_type',
            field=models.CharField(choices=[('log_book', 'Log Book'), ('land_title_deed', 'Land Title Deed'), ('official_letter', 'Official Letter')], max_length=20),
        ),
        migrations.CreateModel(
            name='Guarantor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guarantee_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_by', models.CharField(default='system', max_length=100)),
                ('loan_status', models.CharField(choices=[('active', 'Active'), ('settled', 'Settled'), ('overdue', 'Overdue')], default='active', max_length=10)),
                ('guarantor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guaranteed_loans', to=settings.AUTH_USER_MODEL)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loans.issuedloan')),
            ],
        ),
    ]
