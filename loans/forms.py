# loans/forms.py
from django import forms
from .models import LoanProduct, IssuedLoan
from django import forms
from .models import Collateral, Guarantor
from members.models import Member


class LoanProductForm(forms.ModelForm):
    class Meta:
        model = LoanProduct
        fields = '__all__'


class LoanEligibilityForm(forms.Form):
    loan_product = forms.ModelChoiceField(queryset=LoanProduct.objects.all(), label='Loan Product')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_product'].label_from_instance = lambda obj: obj.name


class IssueLoanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_product'].label_from_instance = lambda obj: obj.name

    class Meta:
        model = IssuedLoan
        fields = ['loan_product', 'loan_amount', 'repayment_period', 'loan_purpose', 'grace_period', 'repayments_start_date']


class CollateralForm(forms.ModelForm):
    class Meta:
        model = Collateral
        fields = ['collateral_type', 'document_ref_no', 'value']
    

class GuarantorForm(forms.ModelForm):
    guarantor_id = forms.IntegerField(label="Guarantor ID")

    class Meta:
        model = Guarantor
        fields = ['guarantor_id', 'guarantee_amount', 'loan_status']

class LoanApprovalForm(forms.ModelForm):
    class Meta:
        model = IssuedLoan
        fields = ['loan_status', 'comments']
        widgets = {
            'status': forms.Select(choices=IssuedLoan.LOAN_STATUSES),
            'comments': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

        
class MemberSearchForm(forms.Form):
    member_id = forms.CharField(max_length=20)

