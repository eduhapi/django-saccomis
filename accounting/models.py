
# models.py
from django.db import models
from django.conf import settings



class SaccoAccount(models.Model):
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50)
    account_balance= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


    class Meta:
        db_table = 'accounting_saccoaccount'  # Explicitly specify the table name

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

