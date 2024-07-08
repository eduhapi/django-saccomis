# groups/forms.py

from django import forms
from .models import Entity, EntityAccount, EntityOfficial
from django import forms
from .models import EntityAccountsLedger


class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = ['entity_name', 'reg_cert_number', 'entity_type', 'annual_income',
                  'head_office_address', 'office_phone_number', 'email']

class EntityAccountForm(forms.ModelForm):
    class Meta:
        model = EntityAccount
        fields = ['reg_fee','savings', 'share_capital', 'loan']

class EntityOfficialForm(forms.ModelForm):
    class Meta:
        model = EntityOfficial
        fields = ['name', 'designation', 'national_id', 'phone_number', 'signature', 'photo']
        widgets = {
            'signature': forms.ClearableFileInput(attrs={'required': False}),
            'photo': forms.ClearableFileInput(attrs={'required': False}),
        }

# forms.py

from django import forms

class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)
    account_type = forms.ChoiceField(label='Account Type', choices=[('savings', 'Savings'), ('share_capital', 'Share Capital'), ('loan', 'Loan')])
    external_ref_code = forms.CharField(label='External Reference Code', required=False)

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)
    account_type = forms.ChoiceField(label='Account Type', choices=[('savings', 'Savings'), ('share_capital', 'Share Capital')])

class TransferForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)
    recipient_id = forms.CharField(label='Recipient Entity ID')
    transfer_from_account_type = forms.ChoiceField(label='Transfer From Account Type', choices=[('savings', 'Savings'), ('share_capital', 'Share Capital'), ('loan', 'Loan')])
    transfer_to_account_type = forms.ChoiceField(label='Transfer To Account Type', choices=[('savings', 'Savings'), ('share_capital', 'Share Capital'), ('loan', 'Loan')])

class EntityStatementFilterForm(forms.Form):
    entity_id = forms.CharField(required=False, label='Entity ID')
    account_type = forms.ChoiceField(choices=[('', 'All'),('savings', 'Savings'), ('share_capital', 'Share Capital'), ('loan', 'Loan')], required=False)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
