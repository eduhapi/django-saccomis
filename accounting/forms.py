# forms.py
from django import forms
from .models import SaccoAccountsLedger, SaccoAccount
from .models import SaccoCharge

class ExpenditureForm(forms.ModelForm):
    account = forms.ModelChoiceField(queryset=SaccoAccount.objects.all(), empty_label="Select Account")

    class Meta:
        model = SaccoAccountsLedger
        fields = ['account', 'description', 'amount']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

class AssetForm(forms.ModelForm):
    account = forms.ModelChoiceField(queryset=SaccoAccount.objects.all(), empty_label="Select Account")

    class Meta:
        model = SaccoAccountsLedger
        fields = ['account', 'description', 'amount']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

class SaccoAccountForm(forms.ModelForm):
    class Meta:
        model = SaccoAccount
        fields = ['account_code', 'account_name', 'account_type']

class ReportFilterForm(forms.Form):
    account = forms.ModelChoiceField(queryset=SaccoAccount.objects.all(), required=False)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)

class SaccoChargeForm(forms.ModelForm):
    class Meta:
        model = SaccoCharge
        fields = ['charge_name', 'charge_type', 'charge_value']
