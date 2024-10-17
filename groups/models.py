# groups/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import models, connection, transaction
import uuid

class Entity(models.Model):
    ENTITY_TYPES = [
        ('public_company', 'Public Company'),
        ('private_company', 'Private Company'),
        ('chama', 'Chama'),
        ('church', 'Church'),
        # Add other types as needed
    ]
    PREFIX = 'E'  # Define a prefix for Entity IDs

    id = models.CharField(max_length=15, primary_key=True, editable=False)
    entity_name = models.CharField(max_length=255)
    reg_cert_number = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    head_office_address = models.CharField(max_length=100)
    office_phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reg_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_id()
        super().save(*args, **kwargs)
    
    def generate_id(self):
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute("SELECT nextval('global_id_sequence')")
            next_id = cursor.fetchone()[0]
        return f'{self.PREFIX}{next_id}'

# Model for entity account
class EntityAccount(models.Model):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name='account')
    reg_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    savings = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    share_capital = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    mobile_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

# Model for entity officials
class EntityOfficial(models.Model):
    DESIGNATIONS = [
        ('treasurer', 'Treasurer'),
        ('chairman', 'Chairman'),
        ('secretary', 'Secretary'),
        # Add other designations as needed
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=50, choices=DESIGNATIONS)
    national_id = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    signature = models.ImageField(upload_to='signatures/')
    photo = models.ImageField(upload_to='photos/')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(default=timezone.now)

class EntityAccountsLedger(models.Model):
    TRANSACTION_MODES = [
        (1, 'Mpesa'),
        (2, 'Cash'),
        (3, 'Bank Transfer')
    ]
    TRANSACTION_TYPES = [
        (1, 'Debit'),
        (2, 'Credit'),
    ]

    sacco_ref_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    tr_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tr_type = models.CharField(choices=TRANSACTION_TYPES, max_length=6)
    tr_account = models.CharField(max_length=50)  # savings, share_capital, loan
    tr_mode_id = models.IntegerField(choices=TRANSACTION_MODES)
    tr_origin = models.CharField(max_length=100)
    tr_destn = models.CharField(max_length=100)  # e.g., 'entity_account', 'beneficiary_id'
    external_ref_code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(default=timezone.now)
    

    def save(self, *args, **kwargs):
        if not self.sacco_ref_code:
            self.sacco_ref_code = uuid.uuid4().hex[:10]
        super(EntityAccountsLedger, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.sacco_ref_code} - {self.entity}"
