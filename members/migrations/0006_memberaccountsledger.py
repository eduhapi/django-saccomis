# Generated by Django 5.0.3 on 2024-07-10 14:05

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_delete_memberaccountsledger'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberAccountsLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sacco_ref_code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('tr_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tr_type', models.CharField(max_length=100)),
                ('tr_account', models.CharField(max_length=20)),
                ('account_id', models.IntegerField()),
                ('tr_mode_id', models.IntegerField(choices=[(1, 'Mpesa'), (2, 'Cash'), (3, 'Bank Transfer')])),
                ('tr_origin', models.CharField(max_length=100)),
                ('tr_destn', models.CharField(max_length=100)),
                ('external_ref_code', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('updated_by', models.CharField(default='system', max_length=100)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member')),
            ],
        ),
    ]
