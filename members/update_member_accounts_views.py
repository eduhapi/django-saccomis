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
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from loans.models import IssuedLoan
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

@login_required
def deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    account = get_object_or_404(MemberAccount, member=member)

    # Get the ContentType for Member
    member_content_type = ContentType.objects.get_for_model(Member)

    # Get the first active loan where the member is a guarantor or has provided collateral
    active_loan_guarantors = Guarantor.objects.filter(guarantor=member, loan_status='active')
    active_loan_collaterals = Collateral.objects.filter(loan_status='active', loan__object_id=member.id, loan__content_type=member_content_type)
    active_loan = None

    if active_loan_guarantors.exists():
        active_loan = active_loan_guarantors.first().loan
    elif active_loan_collaterals.exists():
        active_loan = active_loan_collaterals.first().loan

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account_type = form.cleaned_data['account_type']
            external_code = form.cleaned_data['external_ref_code']

            # Update the appropriate account balance based on the account type
            if account_type == 'savings':
                account.savings += amount
            elif account_type == 'share_capital':
                account.share_capital += amount
            elif account_type == 'loan':
                # Update the loan balance with the deposit amount
                loan_account = IssuedLoan.objects.filter(object_id=member_id, content_type=member_content_type).first()
                if loan_account:
                    if loan_account.loan_balance + amount == 0:
                        # Loan fully repaid
                        loan_account.loan_balance = Decimal('0.00')
                    elif loan_account.loan_balance + amount > 0:
                        # Loan overpaid, set account balance to remaining amount after deductions
                        loan_account.loan_balance += amount
                    else:
                        loan_account.loan_balance += amount

                    if loan_account.loan_balance <= 0 and active_loan:
                        active_loan_guarantors.update(loan_status='settled')
                        active_loan_collaterals.update(loan_status='settled')

                    loan_account.save()

            # Record the transaction
            Transaction.objects.create(
                member_id=member,
                tr_amount=amount,
                external_ref_code=external_code,
                tr_type='credit',
                tr_account=account_type,
                account_id=1,  # Replace with actual account id
                tr_mode_id=1,  # Default to Mpesa for now
                tr_origin='member deposit',
                tr_destn='member account',
                updated_by=request.user.username,
                updated_date=timezone.now()
            )

            account.save()

            # Send SMS notification
            phone_number = member.phone_number
            message = f"Dear {member.first_name}, a deposit of Ksh {amount} has been made to your {account_type} account. Your new balance is Ksh {getattr(account, account_type)}."
            send_notification(phone_number, message)

            messages.success(request, f'Deposit of Ksh {amount} successfully credited to {member.first_name} {member.last_name}.')
            return redirect('members:member_details', member_id=member_id)
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
            print("Submitted data:", request.POST) 
            amount = form.cleaned_data['amount']
            account = get_object_or_404(MemberAccount, member=member)
            if account.savings >= amount:
                account.savings -= amount
                
                # Record the transaction
                Transaction.objects.create(
                    member_id=member,
                    tr_amount=amount,
                    tr_type = 'debit',
                    tr_account='savings',
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_destn='member account',
                    updated_by=request.user.username,
                    updated_date=timezone.now()
                )
                account.save()
                
                # Send SMS notification
                phone_number = member.phone_number
                message = f"Dear {member.first_name}, a withdrawal of Ksh {amount} has been made from your savings account. Your new balance is Ksh {account.savings}."
                send_notification(phone_number, message)
                
                messages.success(request, f'Withdrawal of ${amount} successfully debited from {member.first_name} {member.last_name}.')
                return redirect('members:member_details', member_id=member_id)
            else:
                messages.error(request, 'Insufficient funds.')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = WithdrawalForm()
    return render(request, 'members/withdraw.html', {'form': form, 'member': member})



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
                Transaction.objects.create(
                    member_id=member,
                    tr_amount=amount,
                    tr_type = 'debit',
                    tr_account=transfer_from_account_type,
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin = f'{member.first_name} {member.last_name} ({transfer_from_account_type})',
                    tr_destn=f'{recipient.first_name} {recipient.last_name} ({transfer_to_account_type})',
                    updated_by=request.user.username,
                    updated_date=timezone.now()
                )
                
                # Record the transaction for the recipient
                Transaction.objects.create(
                    member_id=recipient,
                    tr_amount=amount,
                    tr_type = 'credit',
                    tr_account=transfer_to_account_type,
                    account_id=1,  # Replace with actual account id
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin = f'{member.first_name} {member.last_name} ({transfer_from_account_type})',
                    tr_destn=f'{recipient.first_name} {recipient.last_name} ({transfer_to_account_type})',
                    updated_by=request.user.username,
                    updated_date=timezone.now()
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
