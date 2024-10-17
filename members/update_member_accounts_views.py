from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, MemberAccount, Transaction
from loans.models import Guarantor,Collateral
from .forms import DepositForm, WithdrawalForm, TransferForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from sms.utils import send_notification  # Import the send_notification function
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Member
from .utils import generate_unique_sacco_ref_id
from django.contrib.contenttypes.models import ContentType

@login_required
def search_member(request):
    members = []
    error_message = None
    
    if request.method == 'POST':
        search_term = request.POST.get('search_term')
        
        if search_term:
            # Search by ID
            try:
                member_id = int(search_term)
                member = Member.objects.filter(id=member_id).first()
                if member:
                    members.append(member)
            except ValueError:
                pass
            
            # Search by various fields and limit to three results
            query = Member.objects.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(middle_name__icontains=search_term) |
                Q(member_national_id__icontains=search_term)
            )[:3]
            
            members += list(query)

            if not members:
                error_message = "No members found matching your search criteria."

    return render(request, 'members/search_member.html', {'members': members, 'error_message': error_message})




@login_required
def select_action(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    return render(request, 'members/select_action.html', {'member': member})

@login_required
def update_member_accounts(request, member_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        member = get_object_or_404(Member, id=member_id)

        if action == 'deposit':
            return redirect('members:deposit', member_id=member_id)
        elif action == 'withdraw':
            return redirect('members:withdraw', member_id=member_id)
        elif action == 'transfer':
            return redirect('members:transfer', member_id=member_id)
        elif action == 'loan_repayment':
            return redirect('members:loan_repayment', member_id=member_id)
        else:
            messages.error(request, 'Invalid action selected.')
            return render(request, 'members/search_member.html')
    else:
        return render(request, 'members/search_member.html')

@login_required
def member_details(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    account = get_object_or_404(MemberAccount, member=member)
    return render(request, 'members/member_details.html', {'member': member, 'account': account})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Member, MemberAccount, MemberAccountsLedger
from loans.models import  IssuedLoan,Collateral, Guarantor
from .forms import LoanRepaymentForm
from sms.utils import send_notification

@login_required
def loan_repayment(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member_account = get_object_or_404(MemberAccount, member=member)

    # Get the ContentType for Member
    member_content_type = ContentType.objects.get_for_model(Member)

    # Get the active loan
    active_loan = IssuedLoan.objects.filter(object_id=member_id, content_type=member_content_type, loan_status='active').first()

    if request.method == 'POST':
        form = LoanRepaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            external_ref_code = form.cleaned_data['external_ref_code']

            try:
                if active_loan:
                    if active_loan.loan_balance <= 0:
                        messages.error(request, 'Loan is already fully repaid or overpaid. No further payments allowed.')
                        raise ValueError('Loan is already fully repaid or overpaid.')

                    new_balance = active_loan.loan_balance - amount
                    overpayment_amount = 0

                    if new_balance < 0:
                        overpayment_amount = abs(new_balance)
                        active_loan.loan_balance = 0
                        active_loan.loan_status = 'settled'
                        messages.success(request, f'Loan fully repaid. Overpayment of Ksh {overpayment_amount} credited to savings.')
                        Collateral.objects.filter(loan=active_loan).update(loan_status='settled')
                        Guarantor.objects.filter(loan=active_loan).update(loan_status='settled')
                        member_account.savings += overpayment_amount
                    else:
                        active_loan.loan_balance = new_balance

                    active_loan.save()
                else:
                    messages.error(request, f'No active loan found for {member.first_name} {member.last_name}.')
                    raise ValueError('No active loan found.')

                member_account.save()

                # Record the transaction
                MemberAccountsLedger.objects.create(
                    member_id=member,
                    tr_amount=amount,
                    external_ref_code=external_ref_code,
                    tr_type='credit',
                    tr_account='loan',
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin='loan_repayment',
                    tr_destn='loan_account',
                    updated_by=request.user.username,
                    updated_at=timezone.now()
                )

                # Send SMS notification
                phone_number = member.phone_number
                message = f"Dear {member.first_name}, a repayment of Ksh {amount} has been made to your loan account. Your new loan balance is Ksh {active_loan.loan_balance if active_loan else 0}."
                send_notification(phone_number, message)

                messages.success(request, f'Repayment of Ksh {amount} successfully applied to the loan account of {member.first_name} {member.last_name}.')
                return redirect('members:member_details', member_id=member_id)
            except Exception as e:
                messages.error(request, f'Error processing repayment: {str(e)}')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LoanRepaymentForm()

    return render(request, 'members/loan_repayment.html', {'form': form, 'member': member})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Member, MemberAccount, MemberAccountsLedger
from .forms import DepositForm

@login_required
def deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    account = get_object_or_404(MemberAccount, member=member)

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account_type = form.cleaned_data['account_type']
            external_ref_code = form.cleaned_data['external_ref_code']

            try:
                if account_type == 'savings':
                    account.savings += amount
                elif account_type == 'share_capital':
                    account.share_capital += amount

                account.save()

                # Record the transaction
                MemberAccountsLedger.objects.create(
                    member_id=member,
                    tr_amount=amount,
                    tr_type='credit',
                    tr_account=account_type,
                    account_id=1,  # You may want to replace this with the actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin='member deposit',
                    tr_destn='member account',
                    external_ref_code=external_ref_code,
                    updated_by=request.user.username,
                    updated_at=timezone.now()
                )

                # Send SMS notification
                phone_number = member.phone_number
                message = f"Dear {member.first_name}, a deposit of Ksh {amount} has been made to your {account_type} account. Your new balance is Ksh {getattr(account, account_type)}."
                send_notification(phone_number, message)

                messages.success(request, f'Deposit of Ksh {amount} successfully credited to {member.first_name} {member.last_name}.')
                return redirect('members:member_details', member_id=member_id)
            except Exception as e:
                messages.error(request, f'Error processing deposit: {str(e)}')
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = DepositForm()

    return render(request, 'deposit.html', {'form': form, 'member': member})

@login_required
def withdrawal(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account = get_object_or_404(MemberAccount, member=member)
            if account.savings >= amount:
                account.savings -= amount
                
                # Record the transaction
                MemberAccountsLedger.objects.create(
                    member_id=member,
                    tr_amount=amount,
                    tr_type='debit',
                    tr_account='savings',
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin=f'{member.first_name} {member.last_name} (savings)',
                    tr_destn='member account',
                    updated_by=request.user.username,
                    updated_at=timezone.now()
                )
                account.save()
                
                # Send SMS notification
                phone_number = member.phone_number
                message = f"Dear {member.first_name}, a withdrawal of Ksh {amount} has been made from your savings account. Your new balance is Ksh {account.savings}."
                send_notification(phone_number, message)
                
                messages.success(request, f'Withdrawal of Ksh {amount} successfully debited from {member.first_name} {member.last_name}.')
                return redirect('members:member_details', member_id=member_id)
            else:
                messages.error(request, 'Insufficient funds.')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = WithdrawalForm()
    return render(request, 'members/withdraw.html', {'form': form, 'member': member})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Member, MemberAccount, MemberAccountsLedger
from .forms import TransferForm

@login_required
def transfer(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            recipient_id = form.cleaned_data['recipient_id']
            transfer_from_account_type = form.cleaned_data['transfer_from_account_type']
            transfer_to_account_type = form.cleaned_data['transfer_to_account_type']
            
            recipient = get_object_or_404(Member, id=recipient_id)
            account = get_object_or_404(MemberAccount, member=member)
            recipient_account = get_object_or_404(MemberAccount, member=recipient)
            
            # Check if the member has sufficient funds in the specified account type
            if getattr(account, transfer_from_account_type) >= amount:
                # Deduct from the sender's account
                setattr(account, transfer_from_account_type, getattr(account, transfer_from_account_type) - amount)
                account.save()
                
                # Add to the recipient's account
                setattr(recipient_account, transfer_to_account_type, getattr(recipient_account, transfer_to_account_type) + amount)
                recipient_account.save()
                
                # Record the transaction for the sender
                MemberAccountsLedger.objects.create(
                    member_id=member,
                    tr_amount=amount,
                    tr_type='debit',
                    tr_account=transfer_from_account_type,
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin=f'{member.first_name} {member.last_name} ({transfer_from_account_type})',
                    tr_destn=f'{recipient.first_name} {recipient.last_name} ({transfer_to_account_type})',
                    external_ref_code=generate_unique_sacco_ref_id(),  # Add external reference code if applicable
                    updated_by=request.user.username,
                    updated_at=timezone.now()
                )
                
                # Record the transaction for the recipient
                MemberAccountsLedger.objects.create(
                    member_id=recipient,
                    tr_amount=amount,
                    tr_type='credit',
                    tr_account=transfer_to_account_type,
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin=f'{member.first_name} {member.last_name} ({transfer_from_account_type})',
                    tr_destn=f'{recipient.first_name} {recipient.last_name} ({transfer_to_account_type})',
                    external_ref_code=generate_unique_sacco_ref_id(),  # Add external reference code if applicable
                    updated_by=request.user.username,
                    updated_at=timezone.now()
                )
                
                # Send SMS notification to the sender
                phone_number = member.phone_number
                message = f"Dear {member.first_name}, a transfer of Ksh {amount} has been made from your {transfer_from_account_type} account to {recipient.first_name} {recipient.last_name}'s {transfer_to_account_type} account."
                send_notification(phone_number, message)
                
                # Send SMS notification to the recipient
                recipient_phone_number = recipient.phone_number
                recipient_message = f"Dear {recipient.first_name}, you have received a transfer of Ksh {amount} to your {transfer_to_account_type} account from {member.first_name} {member.last_name}'s {transfer_from_account_type} account. Your new balance is Ksh {getattr(recipient_account, transfer_to_account_type)}."
                send_notification(recipient_phone_number, recipient_message)
                
                messages.success(request, f'Transfer of Ksh {amount} from {member.first_name} {member.last_name} to {recipient.first_name} {recipient.last_name} successful.')
                return redirect('members:member_details', member_id=member_id)
            else:
                messages.error(request, 'Insufficient funds in the specified account.')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = TransferForm()
    return render(request, 'transfer.html', {'form': form, 'member': member})
