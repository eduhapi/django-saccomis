
# models.py
from django.db import models
from django.conf import settings



class SaccoAccount(models.Model):
    ACCOUNT_TYPES = [
        ('income', 'Income Account'),
        ('expenditure', 'Expenditure Account'),
        ('fixed_asset', 'Fixed Asset Account'),
        ('current_asset', 'Current Asset Account'),
        ('current_liability', 'Current Liability Account'),
        ('long_term_liability', 'Long-Term Liability Account'),
    ]

    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)  # Added account type
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'accounting_saccoaccount'

    def __str__(self):
        return f"{self.account_code} - {self.account_name}"


class SaccoAccountsLedger(models.Model):
    account_id = models.IntegerField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=2, choices=[('Dr', 'Debit'), ('Cr', 'Credit')])
    transaction_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f"{self.account_id} - {self.transaction_type} - {self.amount}"


class SaccoCharge(models.Model):
    CHARGE_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('amount', 'Amount'),
    ]

    charge_name = models.CharField(max_length=255)
    charge_type = models.CharField(max_length=10, choices=CHARGE_TYPE_CHOICES)
    charge_value = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.charge_name
# accounting/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class MpesaReconciliationLedger(models.Model):
    RECEIPT_CHOICES = (
        ('savings_first', _('Savings First')),
        ('loan_repayment_first', _('Loan Repayment First')),
    )

    receipt_no = models.CharField(_('Receipt Number'), max_length=100, unique=True)
    completion_date = models.CharField(max_length=50)
    paid_in = models.DecimalField(_('Paid In Amount'), max_digits=10, decimal_places=2)
    account_no = models.CharField(_('Account Reference'), max_length=50)
    priority = models.CharField(_('Priority'), max_length=20, choices=RECEIPT_CHOICES)
    reconciled = models.BooleanField(_('Reconciled'), default=False)
    reconciled_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.receipt_no} - {self.account_no}"

    class Meta:
        verbose_name = _('M-Pesa Reconciliation Entry')
        verbose_name_plural = _('M-Pesa Reconciliation Entries')


