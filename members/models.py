from django.db import models
from django.utils import timezone
import uuid
from accounts.models import CustomUser


class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    CLIENT_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('organization', 'Organization'),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('unemployed', 'Unemployed'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    member_national_id = models.CharField(max_length=20, unique=True)
    registration_date = models.DateField(default=timezone.now)
    phone_number = models.CharField(max_length=15)
    secondary_phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES)
    client_photo = models.ImageField(upload_to='client_photos/', null=True, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    address = models.CharField(max_length=255)
    town = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES)
    employment_income = models.DecimalField(max_digits=10, decimal_places=2)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    spouse_name = models.CharField(max_length=100, null=True, blank=True)
    spouse_address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
     return f"{self.first_name} {self.last_name} Account"
     #return f'{self.member.first_name} {self.member.last_name} Account'

class MemberAccount(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    share_capital = models.DecimalField(max_digits=10, decimal_places=2)
    savings = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    reg_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    mobile_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
     return f'{self.member.first_name} {self.member.last_name} Account'

class NextOfKin(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    kin_national_id = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f'Next of kin for {self.member}'



class Transaction(models.Model):
    TRANSACTION_MODES = [
        (1, 'Mpesa'),
        (2, 'Cash'),
        (3, 'Bank Transfer')
    ]

    
    sacco_ref_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    member_id = models.ForeignKey('Member', on_delete=models.CASCADE)
    tr_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tr_type =  models.CharField(max_length=100)
    tr_account = models.CharField(max_length=20)  # e.g., 'savings', 'share_capital', 'withdraw', 'transfer', 'loan_repayment'
    account_id = models.IntegerField()  # savings, share_capital, loans
    tr_mode_id = models.IntegerField(choices=TRANSACTION_MODES)
    tr_origin = models.CharField(max_length=100)
    tr_destn = models.CharField(max_length=100)  # e.g., 'member account', 'beneficiary id'
    external_ref_code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    updated_by = models.CharField(max_length=100, default='system')
    updated_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.sacco_ref_code:
            self.sacco_ref_code = uuid.uuid4().hex[:10]
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.sacco_ref_code} - {self.member_id}"
        
class MemberAccountsLedger(models.Model):
    TRANSACTION_MODES = [
        (1, 'Mpesa'),
        (2, 'Cash'),
        (3, 'Bank Transfer')
    ]

    
    sacco_ref_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    member_id = models.ForeignKey('Member', on_delete=models.CASCADE)
    tr_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tr_type =  models.CharField(max_length=100)
    tr_account = models.CharField(max_length=20)  # e.g., 'savings', 'share_capital', 'withdraw', 'transfer', 'loan_repayment'
    account_id = models.IntegerField()  # savings, share_capital, loans
    tr_mode_id = models.IntegerField(choices=TRANSACTION_MODES)
    tr_origin = models.CharField(max_length=100)
    tr_destn = models.CharField(max_length=100)  # e.g., 'member account', 'beneficiary id'
    external_ref_code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    updated_by = models.CharField(max_length=100, default='system')
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.sacco_ref_code:
            self.sacco_ref_code = uuid.uuid4().hex[:10]
        super(MemberAccountsLedger, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.sacco_ref_code} - {self.member_id}"


