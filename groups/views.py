from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import EntityForm, EntityAccountForm, EntityOfficialForm, DepositForm, WithdrawForm, TransferForm, EntityStatementFilterForm,LoanRepaymentForm
from .models import Entity, EntityAccount, EntityOfficial, EntityAccountsLedger
from accounting.models import SaccoAccount, SaccoAccountsLedger
from loans.models import IssuedLoan, Collateral, Guarantor
from datetime import timedelta
from sms.utils import send_notification
from .utils import generate_pdf_report, generate_excel_report
from django.utils import timezone



@login_required
def register_entity_step_1(request):
    if request.method == 'POST':
        form = EntityForm(request.POST)
        if form.is_valid():
            entity = form.save()
            form = EntityForm()
            return redirect('groups:register_entity_step_2', entity_id=entity.id)
    else:
        form = EntityForm()
    return render(request, 'groups/register_entity_step_1.html', {'form': form})
@login_required
def register_entity_step_2(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    if request.method == 'POST':
        form = EntityAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.entity = entity
            account.save()

            # Record registration fee in EntityAccountsLedger
            reg_fee = account.reg_fee
            # Add registration fee to sacco account with code 2001
            sacco_account = SaccoAccount.objects.get(account_code='2001')
            sacco_account.account_balance += reg_fee
            sacco_account.save()

            # Record transaction in SaccoAccountsLedger
            sacco_ledger_entry = SaccoAccountsLedger(
                account_id=sacco_account.id,
                transaction_type='Cr',  # Assuming 2 represents a credit
                amount=reg_fee,
                description=f'Registration fee from {entity.entity_name}',
                updated_by=request.user
            )
            sacco_ledger_entry.save()
            form = EntityAccountForm()
            return redirect('groups:register_entity_step_3', entity_id=entity.id)
    else:
        form = EntityAccountForm()
    return render(request, 'groups/register_entity_step_2.html', {'form': form, 'entity': entity})

@login_required
def register_entity_step_3(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    if request.method == 'POST':
        if 'add_official' in request.POST:
            form = EntityOfficialForm(request.POST, request.FILES)
            if form.is_valid():
                official = form.save(commit=False)
                official.entity = entity
                official.save()
                messages.success(request, 'Official added successfully.')
                return redirect('groups:register_entity_step_3', entity_id=entity.id)
        elif 'next' in request.POST:
            form = EntityOfficialForm()
            return redirect('register_entity_done', entity_id=entity.id)
    else:
        form = EntityOfficialForm()

    officials = EntityOfficial.objects.filter(entity=entity)
    return render(request, 'groups/register_entity_step_3.html', {
        'form': form,
        'entity': entity,
        'officials': officials
    })

@login_required
def delete_official(request, entity_id, official_id):
    official = get_object_or_404(EntityOfficial, id=official_id)
    official.delete()
    messages.success(request, 'Official deleted successfully.')
    return redirect('groups:register_entity_step_3', entity_id=entity_id)

@login_required
def register_entity_done(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    account = EntityAccount.objects.get(entity=entity)
    officials = EntityOfficial.objects.filter(entity=entity)

    # Send SMS notification
    phone_number = entity.office_phone_number  # Ensure this field exists and is properly populated
    message = (
        f"Welcome to Django Sacco System v.1.0.0, {entity.entity_name}!\n"
        f"Registration Number: {entity.reg_cert_number}\n"
        f"Share Capital: Ksh {account.share_capital}\n"
        f"Savings: Ksh {account.savings}\n"
        f"Loan Balance: Ksh {account.loan}\n"
        f"Welcome aboard, together we succeed!"
    )
    send_notification(phone_number, message)

    return render(request, 'groups/register_entity_done.html', {
        'entity': entity,
        'account': account,
        'officials': officials
    })

@login_required
def updated_entity_details(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    account = get_object_or_404(EntityAccount, entity=entity)
    return render(request, 'groups/updated_entity_details.html', {'entity': entity, 'account': account})
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

@login_required
def view_groups(request):
    groups = Entity.objects.all().select_related('account')
    
    active_loans = IssuedLoan.objects.filter(
        loan_status='active',
        content_type=ContentType.objects.get_for_model(Entity)
    )
    
    # Annotate each group with their active loan amount
    group_loan_data = {
        loan.object_id: loan.loan_balance
        for loan in active_loans
    }
    
    context = {
        'groups': groups,
        'group_loan_data': group_loan_data
    }
    return render(request, 'groups/view_groups.html', context)


from django.contrib import messages
from django.shortcuts import render
from .models import Entity

@login_required
def search_entity(request):
    if request.method == 'POST':
        search_term = request.POST.get('search_term')
        entities = Entity.objects.filter(id=search_term) | Entity.objects.filter(entity_name__icontains=search_term)

        if entities.exists():
            return render(request, 'groups/search_entity.html', {'entities': entities})
        else:
            messages.warning(request, f"No entities found matching '{search_term}'.")
    else:
        messages.error(request, "Invalid request method.")

    return render(request, 'groups/search_entity.html')


@login_required
def select_action(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    return render(request, 'groups/select_action.html', {'entity': entity})

@login_required
def update_entity_accounts(request, entity_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'deposit':
            return redirect('groups:deposit', entity_id=entity_id)
        elif action == 'withdraw':
            return redirect('groups:withdraw', entity_id=entity_id)
        elif action == 'transfer':
            return redirect('groups:transfer', entity_id=entity_id)
        elif action == 'loan_repayment':
            return redirect('groups:loan_repayment', entity_id=entity_id)
        else:
            messages.error(request, 'Invalid action selected.')
            return redirect('groups:search_entity')
    return redirect('groups:search_entity')
@login_required
def loan_repayment(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    account = get_object_or_404(EntityAccount, entity=entity)
    issued_loan = IssuedLoan.objects.filter(object_id=entity_id, loan_status='active').first()

    if request.method == 'POST':
        form = LoanRepaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            external_ref_code = form.cleaned_data['external_ref_code']

            try:
                if issued_loan:
                    overpayment = amount - issued_loan.loan_balance
                    if overpayment >= 0:
                        # Fully repay the loan and add overpayment to savings
                        issued_loan.loan_balance = 0
                        issued_loan.loan_status = 'settled'
                        issued_loan.save()

                        Collateral.objects.filter(loan=issued_loan).update(loan_status='settled')
                        Guarantor.objects.filter(loan=issued_loan).update(loan_status='settled')

                        account.savings += overpayment
                        account.save()

                        # Record the loan repayment transaction
                        EntityAccountsLedger.objects.create(
                            entity=entity,
                            tr_amount=issued_loan.loan_balance,
                            external_ref_code=external_ref_code,
                            tr_type='credit',
                            tr_account='loan_repayment',
                            tr_mode_id=1,  # Default to Mpesa for now
                            tr_origin='entity_deposit',
                            tr_destn='entity_account',
                            updated_by=request.user,
                            updated_at=timezone.now()
                        )

                        # Record the overpayment transaction
                        EntityAccountsLedger.objects.create(
                            entity=entity,
                            tr_amount=overpayment,
                            external_ref_code=external_ref_code,
                            tr_type='credit',
                            tr_account='savings',
                            tr_mode_id=1,  # Default to Mpesa for now
                            tr_origin='entity_deposit',
                            tr_destn='entity_account',
                            updated_by=request.user,
                            updated_at=timezone.now()
                        )

                        messages.success(request, f'Loan of Ksh {issued_loan.loan_balance} fully repaid. Overpayment of Ksh {overpayment} added to savings.')
                    else:
                        # Partially repay the loan
                        issued_loan.loan_balance -= amount
                        issued_loan.save()

                        EntityAccountsLedger.objects.create(
                            entity=entity,
                            tr_amount=amount,
                            external_ref_code=external_ref_code,
                            tr_type='credit',
                            tr_account='loan_repayment',
                            tr_mode_id=1,  # Default to Mpesa for now
                            tr_origin='entity_deposit',
                            tr_destn='entity_account',
                            updated_by=request.user,
                            updated_at=timezone.now()
                        )

                        messages.success(request, f'Loan repayment of Ksh {amount} successful. Remaining loan balance is Ksh {issued_loan.loan_balance}.')
                else:
                    messages.error(request, f'No active loan found for {entity.entity_name}.')
            except Exception as e:
                messages.error(request, f'Error processing loan repayment: {str(e)}')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LoanRepaymentFormForm()

    return render(request, 'groups/loan_repayment.html', {'form': form, 'entity': entity})

@login_required
def deposit(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    account = get_object_or_404(EntityAccount, entity=entity)

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
                else:
                    messages.error(request, 'Invalid account type for deposit.')
                    raise ValueError('Invalid account type.')

                account.save()

                # Record the transaction
                EntityAccountsLedger.objects.create(
                    entity=entity,
                    tr_amount=amount,
                    external_ref_code=external_ref_code,
                    tr_type='credit',
                    tr_account=account_type,
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin='entity_deposit',
                    tr_destn='entity_account',
                    updated_by=request.user,
                    updated_at=timezone.now()
                )

                # Send SMS notification
                phone_number = entity.office_phone_number
                message = f"Dear {entity.entity_name}, a deposit of Ksh {amount} has been made to your {account_type} account. Your new balance is Ksh {getattr(account, account_type)}."
                send_notification(phone_number, message)

                messages.success(request, f'Deposit of Ksh {amount} successfully credited to {entity.entity_name}.')
                form = DepositForm()
                return redirect('groups:entity_details', entity_id=entity_id)
            except Exception as e:
                messages.error(request, f'Error processing deposit: {str(e)}')
        else:
            # Collect form errors
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = DepositForm()

    return render(request, 'groups/deposit.html', {'form': form, 'entity': entity})
@login_required
def withdraw(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    account = get_object_or_404(EntityAccount, entity=entity)
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account_type = form.cleaned_data['account_type']
            external_ref_code = form.cleaned_data.get('external_ref_code', None)

            if account_type == 'savings':
                account.savings -= amount
            elif account_type == 'share_capital':
                account.share_capital -= amount

            account.save()# Record the transaction
            EntityAccountsLedger.objects.create(
                entity=entity,
                tr_amount=amount,
                external_ref_code=external_ref_code,
                tr_type='debit',
                tr_account=account_type,
                tr_mode_id=1,  # Default to Mpesa for now
                tr_origin='entity_withdraw',
                tr_destn='cash',
                updated_by=request.user,
                updated_at=timezone.now()
            )

            account.save()
            # Send SMS notification
            phone_number = entity.office_phone_number
            message = f"Dear {entity.entity_name}, a Withdrawal of Ksh {amount} has been made to your {account_type} account. Your new balance is Ksh {getattr(account, account_type)}."
            send_notification(phone_number, message)
            messages.success(request, f'Withdrawal of Ksh {amount} successfully debited from {entity.entity_name}.')
            return redirect('groups:withdraw', entity_id=entity_id)
    else:
        form = WithdrawForm()
    return render(request, 'groups/withdraw.html', {'form': form, 'entity': entity})

@login_required
def transfer(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            recipient_id = form.cleaned_data['recipient_id']
            transfer_from_account_type = form.cleaned_data['transfer_from_account_type']
            transfer_to_account_type = form.cleaned_data['transfer_to_account_type']
           
            recipient = get_object_or_404(Entity, id=recipient_id)
            entity_account = EntityAccount.objects.get(entity=entity)
            recipient_account = EntityAccount.objects.get(entity=recipient)

            if transfer_from_account_type == 'savings':
                entity_account.savings -= amount
                if transfer_to_account_type == 'savings':
                    recipient_account.savings += amount
                elif transfer_to_account_type == 'share_capital':
                    recipient_account.share_capital += amount
                elif transfer_to_account_type == 'loan_repayment':
                    recipient_account.loan -= amount
            elif transfer_from_account_type == 'share_capital':
                entity_account.share_capital -= amount
                if transfer_to_account_type == 'savings':
                    recipient_account.savings += amount
                elif transfer_to_account_type == 'share_capital':
                    recipient_account.share_capital += amount
                elif transfer_to_account_type == 'loan_repayment':
                    recipient_account.loan -= amount
            elif transfer_from_account_type == 'loan_repayment':
                entity_account.loan -= amount
                if transfer_to_account_type == 'savings':
                    recipient_account.savings += amount
                elif transfer_to_account_type == 'share_capital':
                    recipient_account.share_capital += amount
                elif transfer_to_account_type == 'loan_repayment':
                    recipient_account.loan -= amount

            entity_account.save()
            recipient_account.save()
            
                # Record the transaction for the sender
            EntityAccountsLedger.objects.create(
                    entity=entity,
                    tr_amount=amount,
                    tr_type = 'debit',
                    tr_account=transfer_from_account_type,
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin = f'{entity.entity_name}({transfer_from_account_type})',
                    tr_destn=f'{recipient.entity_name} ({transfer_to_account_type})',
                    updated_by=request.user,
                    updated_at=timezone.now()
                )
                
                # Record the transaction for the recipient
            EntityAccountsLedger.objects.create(
                    entity=entity,
                    tr_amount=amount,
                    tr_type = 'credit',
                    tr_account=transfer_to_account_type,
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin = f'{entity.entity_name} ({transfer_from_account_type})',
                    tr_destn=f'{recipient.entity_name}({transfer_to_account_type})',
                    updated_by=request.user,
                    updated_at=timezone.now()
                )
                # Send SMS notification to the sender
            phone_number = entity.office_phone_number
            message = f"Dear {entity.entity_name}, a transfer of Ksh {amount} has been made from your {transfer_from_account_type} account to {recipient.entity_name}."
            send_notification(phone_number, message)
                
                # Send SMS notification to the recipient
            recipient_phone_number = recipient.office_phone_number
            recipient_message = f"Dear {recipient.entity_name}, you have received a transfer of Ksh {amount} to your {transfer_to_account_type} account from {entity.entity_name}. Your new balance is Ksh {getattr(recipient_account, transfer_to_account_type)}."
            send_notification(recipient_phone_number, recipient_message)
            messages.success(request, f'Transfer of Ksh {amount} from {entity.entity_name} to {recipient.entity_name} successful.')
            return redirect('groups:transfer', entity_id=entity_id)
    else:
        form = TransferForm()
    return render(request, 'groups/transfer.html', {'form': form, 'entity': entity})

# groups/views.py

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .forms import EntityStatementFilterForm
from .models import Entity, EntityAccountsLedger
from django.http import HttpResponse

@login_required
def entity_statement_form(request):
    if request.method == 'POST':
        form = EntityStatementFilterForm(request.POST)
        if form.is_valid():
            entity_id = form.cleaned_data.get('entity_id')
            account_type = form.cleaned_data.get('account_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # Redirect to entity_statement view with query parameters
            return render(request, 'groups/entity_statement.html', {
                'entity_id': entity_id,
                'account_type': account_type,
                'start_date': start_date,
                'end_date': end_date,
            })

    else:
        form = EntityStatementFilterForm()

    return render(request, 'groups/entity_statement_form.html', {'form': form})
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .forms import EntityStatementFilterForm
from .models import Entity, EntityAccountsLedger, EntityAccount
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .utils import generate_pdf_report, generate_excel_report

@login_required
def entity_statement(request):
    if request.method == 'POST':
        form = EntityStatementFilterForm(request.POST)
        if form.is_valid():
            entity_id = form.cleaned_data.get('entity_id')
            account_type = form.cleaned_data.get('account_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            try:
                # Fetch entity details if entity_id is provided
                entity = None
                account_balance = None
                if entity_id:
                    entity = get_object_or_404(Entity, id=entity_id)

                    # Fetch the account balance based on the account type
                    entity_account = EntityAccount.objects.get(entity=entity)
                    if account_type == 'savings':
                        account_balance = entity_account.savings
                    elif account_type == 'share_capital':
                        account_balance = entity_account.share_capital
                    elif account_type == 'loan':
                        account_balance = entity_account.loan

                # Retrieve transactions and filter based on form inputs
                transactions = EntityAccountsLedger.objects.all()

                if entity_id:
                    transactions = transactions.filter(entity_id=entity_id)

                if start_date and end_date:
                    end_date_plus_one = end_date + timedelta(days=1)
                    transactions = transactions.filter(updated_at__range=(start_date, end_date_plus_one))

                if account_type:
                    transactions = transactions.filter(tr_account=account_type)

                if not transactions.exists():
                    form.add_error(None, 'No transactions found for the given criteria.')

                context = {
                    'entity': entity,
                    'transactions': transactions,
                    'account_type': account_type,
                    'account_balance': account_balance,
                    'today': timezone.now(),
                    'form': form,
                }

                return render(request, 'groups/entity_statement.html', context)
            except Entity.DoesNotExist:
                form.add_error('entity_id', 'Entity not found.')
            except EntityAccount.DoesNotExist:
                form.add_error(None, 'Entity account not found.')
            except Exception as e:
                form.add_error(None, f"Error: {e}")

    else:
        form = EntityStatementFilterForm()

    return render(request, 'groups/entity_statement_form.html', {'form': form})


@login_required
def download_pdf(request):
    try:
        context = request.GET.copy()
        transactions = EntityAccountsLedger.objects.filter(entity_id=context['entity_id'])

        response = generate_pdf_report(context, 'groups/entity_statement_pdf.html')
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {e}")

@login_required
def download_excel(request):
    try:
        context = request.GET.copy()
        transactions = EntityAccountsLedger.objects.filter(entity_id=context['entity_id'])

        response = generate_excel_report(transactions, 'entity_statement')
        return response
    except Exception as e:
        return HttpResponse(f"Error generating Excel: {e}")
@login_required
def entity_profile(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    
    # Fetch active loans and calculate their total principal
    active_loans = IssuedLoan.objects.filter(object_id=entity_id, loan_status='active')
    active_loan_principal = active_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    active_loan_balance = active_loans.aggregate(Sum('loan_balance'))['loan_balance__sum'] or 0
    # Fetch all loans and calculate their total balance
    all_loans = IssuedLoan.objects.filter(object_id=entity_id)
    total_loans_taken = all_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    
    entityofficial = EntityOfficial.objects.filter(entity_id=entity_id)

    context = {
        'entity': entity,
        'entityofficial': entityofficial,
        'active_loan_principal': active_loan_principal,
        'total_loans_taken': total_loans_taken,
        'active_loan_balance':active_loan_balance,
    }
    return render(request, 'groups/entity_profile.html', context)
