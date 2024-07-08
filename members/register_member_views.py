from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView
from .forms import MemberForm, MemberAccountForm, NextOfKinForm
from .models import Member, MemberAccount, NextOfKin, Transaction
from accounting.models import SaccoAccount, SaccoAccountsLedger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime
from .utils import generate_unique_sacco_ref_id
from sms.utils import send_notification  # Import the send_notification function

# Define a file storage for uploaded files
file_storage = FileSystemStorage(location='/tmp/')

FORMS = [
    ("member", MemberForm),
    ("account", MemberAccountForm),
    ("next_of_kin", NextOfKinForm),
]

TEMPLATES = {
    "member": "register_member/step_member.html",
    "account": "register_member/step_account.html",
    "next_of_kin": "register_member/step_next_of_kin.html"
}

@method_decorator(login_required, name='dispatch')
class MemberRegistrationWizard(SessionWizardView):
    form_list = FORMS
    file_storage = file_storage  # Specify the file storage

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        member_form = form_list[0]
        account_form = form_list[1]
        next_of_kin_form = form_list[2]

        # Save the member, account, and next of kin details
        member = member_form.save()
        account = account_form.save(commit=False)
        account.member = member
        account.save()

        next_of_kin = next_of_kin_form.save(commit=False)
        next_of_kin.member = member
        next_of_kin.save()

        # Get initial amounts and external reference code from the account form
        initial_savings = account_form.cleaned_data['savings']
        initial_share_capital = account_form.cleaned_data['share_capital']
        external_ref_code = account_form.cleaned_data['external_ref_code']
        registration_fee = account_form.cleaned_data['reg_fee']

        # Create initial transaction entries for the new member's account
        self.create_initial_transactions(member, initial_savings, initial_share_capital, external_ref_code)

        # Post the registration fee to the Sacco account with account code "2001"
        self.post_registration_fee(registration_fee, external_ref_code)

        # Send SMS notification
        phone_number = member.phone_number  # Ensure this field exists and is properly populated
        message = (
            f"Welcome to Django Sacco System v.1.0.0, {member.first_name}!\n"
            f"Membership Number: {member.id}\n"
            f"Share Capital: Ksh {initial_share_capital}\n"
            f"Savings: Ksh {initial_savings}\n"
            f"Welcome aboard, together we succeed!"
        )
        send_notification(phone_number, message)

        return render(self.request, 'register_member/done.html', {
            'member': member,
            'account': account,
            'next_of_kin': next_of_kin
        })

    def create_initial_transactions(self, member, savings, share_capital, external_ref_code):
        initial_transactions = [
            {'tr_account': 'savings', 'tr_amount': savings},
            {'tr_account': 'share_capital', 'tr_amount': share_capital},
        ]

        for index, transaction in enumerate(initial_transactions, start=1):
            Transaction.objects.create(
                sacco_ref_code=generate_unique_sacco_ref_id(),
                tr_amount=transaction['tr_amount'],
                tr_account=transaction['tr_account'],
                account_id=member.id,
                tr_mode_id=1,
                tr_origin='initial',
                tr_type='credit',
                tr_destn='self',
                external_ref_code=f"{external_ref_code}_{index}",
                updated_by=self.request.user.username,
                updated_date=datetime.now(),
                member_id_id=member.id,
            )

    def post_registration_fee(self, amount, external_ref_code):
        sacco_account = SaccoAccount.objects.get(account_code='2001')

        # Update the sacco account balance
        sacco_account.account_balance += amount
        sacco_account.save()

        # Create a ledger entry
        SaccoAccountsLedger.objects.create(
            account_id=sacco_account.id,
            description="Registration Fee",
            amount=amount,
            transaction_type='Cr',  # Credit the Sacco account
            updated_by=self.request.user
        )
