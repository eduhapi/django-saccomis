# loans/models.py
from django.db import models
from django.conf import settings
from members.models import Member, MemberAccount
from django.utils import timezone
from django.conf import settings  # for getting the user model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from members.models import Member  # Adjust the import as necessary
from groups.models import Entity




class LoanProduct(models.Model):
    name = models.CharField(max_length=100)
    savings_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    max_repayment_period = models.IntegerField(default=36)
    min_membership_age = models.DurationField(default="00:10:00")  # For testing, 10 minutes
    processing_fee_less_100k = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    processing_fee_100k_to_1M = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    processing_fee_above_1M = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)


class IssuedLoan(models.Model):
    LOAN_STATUSES = [
        ('active', 'Active'),
        ('settled', 'Settled'),
        ('overdue', 'Overdue')
    ]
    loan_ref_id = models.CharField(max_length=20, unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=15)  # Updated to CharField to handle both types of IDs
    content_object = GenericForeignKey('content_type', 'object_id')
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    repayment_period = models.IntegerField()
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_purpose = models.CharField(max_length=255)
    grace_period = models.IntegerField(default=0)
    repayments_start_date = models.DateField()
    installment_every = models.CharField(max_length=20, default='1 month')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(default=timezone.now)
    loan_status = models.CharField(max_length=10, choices=LOAN_STATUSES, default='active')
    updated_at = models.DateField(default=timezone.now)


class Collateral(models.Model):
    COLLATERAL_TYPES = [
        ('log_book', 'Log Book'),
        ('land_title_deed', 'Land Title Deed'),
        ('official_letter', 'Official Letter'),
    ]
    COLLATERAL_STATUSES = [
        ('active', 'Active'),
        ('settled', 'Settled'),
        ('overdue', 'Overdue')
    ]
    loan = models.ForeignKey('IssuedLoan', on_delete=models.CASCADE)
    collateral_type = models.CharField(max_length=20, choices=COLLATERAL_TYPES)
    document_ref_no = models.CharField(max_length=100, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loan_status = models.CharField(max_length=10, choices=COLLATERAL_STATUSES, default='active')

class Guarantor(models.Model):
    GUARANTOR_STATUSES = [
        ('active', 'Active'),
        ('settled', 'Settled'),
        ('overdue', 'Overdue')
    ]
    loan = models.ForeignKey('IssuedLoan', on_delete=models.CASCADE)
    guarantor = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='guaranteed_loans')
    guarantee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=100, default='system')
    loan_status = models.CharField(max_length=10, choices=GUARANTOR_STATUSES, default='active')
    
    def __str__(self):
        return f"{self.guarantor} - {self.loan}"