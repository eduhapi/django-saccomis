from django import forms

class MemberStatementFilterForm(forms.Form):
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    account_type = forms.ChoiceField(label='Account Type', choices=[('', 'All'), ('savings', 'Savings'), ('share_capital', 'Share Capital'), ('loan', 'Loan')], required=False)
    member_id = forms.IntegerField(label='Member ID', required=False)
