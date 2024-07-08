from django import forms
from .models import Member, MemberAccount, NextOfKin

class DepositForm(forms.Form):
    account_type = forms.ChoiceField(choices=[
        ('savings', 'Savings'),
        ('share_capital', 'Share Capital'),
        ('loan', 'Loan Repayment'),
     ])
    external_ref_code = forms.CharField(label='External Reference Code', max_length=100, required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
 

def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    

class TransferForm(forms.Form):
    transfer_from_account_type = forms.ChoiceField(choices=[
        ('savings', 'Savings'),
        ('share_capital', 'Share Capital'),
        ('loan', 'Loan Repayment'),
     ])
    transfer_to_account_type = forms.ChoiceField(choices=[
        ('savings', 'Savings'),
        ('share_capital', 'Share Capital'),
        ('loan', 'Loan Repayment'),
     ])
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    recipient_id = forms.IntegerField()

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'first_name', 'middle_name', 'last_name','member_national_id', 'registration_date', 'phone_number',
            'secondary_phone_number', 'email', 'date_of_birth', 'gender', 'client_type', 
            'client_photo', 'marital_status', 'address', 'town', 'profession', 
            'employment_status', 'employment_income', 'signature', 'spouse_name', 
            'spouse_address'
        ]


class MemberAccountForm(forms.ModelForm):
    external_ref_code = forms.CharField(label='External Reference Code', max_length=100, required=True)

    class Meta:
        model = MemberAccount
        fields = ['share_capital', 'savings', 'reg_fee', 'external_ref_code']


        

class NextOfKinForm(forms.ModelForm):
    class Meta:
        model = NextOfKin
        fields = ['full_name', 'relationship', 'kin_national_id', 'address', 'email', 'phone_number']


class MiniStatementForm(forms.Form):
    member_id = forms.CharField(label='Member ID', max_length=100)
    account_type = forms.ChoiceField(choices=[('savings', 'Savings'), ('share_capital', 'Share Capital'), ('loan', 'Loan Account')], label='Account Type')
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label="Start Date")
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label="End Date")

