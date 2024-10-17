from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from loans.models import Member, IssuedLoan, MemberAccount
from members.models import Transaction,MemberAccountsLedger
from .utils import generate_pdf_report, generate_excel_report
from datetime import datetime, timedelta
from django.utils import timezone

from django.shortcuts import render
from .forms import MemberStatementFilterForm

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .forms import MemberStatementFilterForm

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .forms import MemberStatementFilterForm

@login_required
def member_statement_form(request):
    form = MemberStatementFilterForm()
    return render(request, 'reports/member_statement_form.html', {'form': form})

@login_required
def member_statement(request):
    if request.method == 'POST':
        form = MemberStatementFilterForm(request.POST)
        if form.is_valid():
            member_id = form.cleaned_data.get('member_id')
            account_type = form.cleaned_data.get('account_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # Fetch member details
            member = get_object_or_404(Member, id=member_id) if member_id else None
            
            # Fetch appropriate account from MemberAccount
            member_account = get_object_or_404(MemberAccount, member=member) if member else None

            # Filter transactions based on form inputs
            transactions = MemberAccountsLedger.objects.all()
            if start_date and end_date:
                end_date = end_date + timedelta(days=1)  # Add one day to include the end date
                transactions = transactions.filter(updated_at__range=(start_date, end_date))

            if account_type:
                transactions = transactions.filter(tr_account=account_type)

            if member_id:
                transactions = transactions.filter(member_id=member_id)

            account_balance = None
            if member_account:
                if account_type == 'savings':
                    account_balance = member_account.savings
                elif account_type == 'share_capital':
                    account_balance = member_account.share_capital
                elif account_type == 'loan':
                    account_balance = member_account.loan

            context = {
                'member': member,
                'transactions': transactions,
                'account_balance': account_balance,
                'account_type': account_type,
                'today': timezone.now(),
                'form': form,
            }

            if 'download' in request.POST:
                format = request.POST.get('format', 'pdf')
                if format == 'pdf':
                    return generate_pdf_report(context, 'reports/member_statement_pdf.html')
                elif format == 'excel':
                    return generate_excel_report(transactions, 'member_statement')

            return render(request, 'reports/member_statement.html', context)

    else:
        form = MemberStatementFilterForm()

    return render(request, 'reports/member_statement_form.html', {'form': form})



@login_required
def member_details(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    context = {
        'member': member,
    }
    return render(request, 'reports/member_details.html', context)


@login_required
def loan_defaulters(request):
    today = date.today()
    defaulters = IssuedLoan.objects.filter(repayments_start_date__lt=today, installment_amount__gt=0)
    
    context = {
        'defaulters': defaulters,
    }
    
    if 'download' in request.GET:
        format = request.GET.get('format', 'pdf')
        if format == 'pdf':
            return generate_pdf_report(context, 'reports/loan_defaulters_pdf.html')
        elif format == 'excel':
            return generate_excel_report(defaulters, 'loan_defaulters')
    
    return render(request, 'reports/loan_defaulters.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from loans.models import IssuedLoan
from members.models import Member
from groups.models import Entity
from .utils import generate_pdf_report, generate_excel_report

@login_required
def loan_balances(request):
    # Filter loans with loan_status as active
    issued_loans = IssuedLoan.objects.filter(loan_status='active')
    loan_balances = []

    for loan in issued_loans:
        today = timezone.now().date()
        repayments_start_date = loan.created_at + timedelta(days=28)  # Repayment starts 28 days from loan creation
        days_since_repayments_start = (today - repayments_start_date).days
        total_months = days_since_repayments_start // 28
        
        # Calculate the expected balance
        expected_balance = loan.loan_amount - total_months * loan.installment_amount

        # Calculate the arrears amount
        arrears_amount = max(0, expected_balance - loan.loan_balance)
        missed_installments = arrears_amount // loan.installment_amount

        remaining_repayment_period = max(0, loan.repayment_period - total_months)
        last_repayment_date = repayments_start_date + timedelta(days=total_months * 28)
        
        if isinstance(loan.content_object, Member):
            identifier = loan.content_object.id
            name = f'{loan.content_object.first_name} {loan.content_object.last_name}'
            phone = loan.content_object.phone_number
            type_ = 'Member'
        else:
            identifier = loan.content_object.id
            name = loan.content_object.entity_name
            phone = loan.content_object.office_phone_number
            type_ = 'Entity'

        loan_balances.append({
            'id': identifier,
            'name': name,
            'phone': phone,
            'principal': loan.loan_amount,
            'installment': loan.installment_amount,
            'last_repayment_date': last_repayment_date,
            'remaining_repayment_period': remaining_repayment_period,
            'current_loan_balance': loan.loan_balance,
            'arrears_amount': arrears_amount,
            'arrears_period': missed_installments,
            'type': type_,
        })

    context = {
        'loan_balances': loan_balances,
    }

    if 'download' in request.GET:
        format = request.GET.get('format', 'pdf')
        if format == 'pdf':
            return generate_pdf_report(context, 'reports/loan_balances_pdf.html')
        elif format == 'excel':
            return generate_excel_report(loan_balances, 'loan_balances')

    return render(request, 'reports/loan_balances.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages  # Import messages
from .forms import AccountStatementForm
import logging
from members.models import Member, MemberAccountsLedger
from groups.models import Entity, EntityAccountsLedger
from reports.utils import generate_pdf_report

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def account_statement_form(request):
    form = AccountStatementForm()
    return render(request, 'reports/account_statement_form.html', {'form': form})

@login_required
def account_statement(request):
    logger.info('Processing account statement request')
    
    if request.method == 'POST':
        logger.info('Received POST request')
        form = AccountStatementForm(request.POST)
        if form.is_valid():
            account_id = form.cleaned_data.get('account_id')
            logger.info(f'Fetching statement for account_id: {account_id}')
            
            member = None
            entity = None
            transactions = []
            
            if account_id.isnumeric():
                try:
                    logger.info(f'Trying to fetch member with id: {account_id}')
                    member = get_object_or_404(Member, id=account_id)
                    transactions = MemberAccountsLedger.objects.filter(member_id=member.id)
                    logger.info(f'Found member: {member}')
                    messages.success(request, f'Successfully fetched statement for member ID: {member.id}.')
                except Exception as e:
                    logger.error(f'Error fetching member: {e}')
                    messages.error(request, f'Error fetching member: {e}')
            else:
                try:
                    logger.info(f'Trying to fetch entity with id: {account_id}')
                    entity = get_object_or_404(Entity, id=account_id)
                    transactions = EntityAccountsLedger.objects.filter(entity=entity)
                    logger.info(f'Found entity: {entity}')
                    messages.success(request, f'Successfully fetched statement for entity ID: {entity.id}.')
                except Exception as e:
                    logger.error(f'Error fetching entity: {e}')
                    messages.error(request, f'Error fetching entity: {e}')
            
            if not transactions:
                logger.warning(f'No transactions found for account_id: {account_id}')
                messages.warning(request, f'No transactions found for account ID: {account_id}')
            
            savings_transactions = transactions.filter(tr_account='savings')
            share_capital_transactions = transactions.filter(tr_account='share_capital')
            loan_transactions = transactions.filter(tr_account='loan')

            logger.info(f'Transactions fetched: {len(transactions)}')
            logger.info(f'Savings transactions: {len(savings_transactions)}')
            logger.info(f'Share capital transactions: {len(share_capital_transactions)}')
            logger.info(f'Loan transactions: {len(loan_transactions)}')

            context = {
                'member': member,
                'entity': entity,
                'savings_transactions': savings_transactions,
                'share_capital_transactions': share_capital_transactions,
                'loan_transactions': loan_transactions,
                'today': timezone.now(),
                'form': form,
            }

            if 'download' in request.POST:
                format = request.POST.get('format', 'pdf')
                if format == 'pdf':
                    logger.info('Generating PDF report')
                    return generate_pdf_report(context, 'reports/account_statement_pdf.html')

            logger.info('Rendering account statement template')
            return render(request, 'reports/account_statement.html', context)

        else:
            logger.error('Form is invalid')
            messages.error(request, 'The form is invalid. Please correct the errors and try again.')
    else:
        logger.info('Rendering empty form')
        form = AccountStatementForm()

    return render(request, 'reports/account_statement_form.html', {'form': form})


from django.shortcuts import render
from accounting.models import SaccoAccount, SaccoAccountsLedger
from groups.models import EntityAccount,EntityAccountsLedger
from members.models import MemberAccount, MemberAccountsLedger

def member_trial_balance(request):
    member_accounts = MemberAccount.objects.all()
    context = {
        'member_accounts': member_accounts,
    }
    return render(request, 'reports/member_trial_balance.html', context)

def member_cumulative_balance(request):
    # Assuming a simple cumulative balance based on ledger entries
    member_accounts = MemberAccount.objects.all()
    context = {
        'member_accounts': member_accounts,
    }
    return render(request, 'reports/member_cumulative_balance.html', context)


def entity_trial_balance(request):
    entity_accounts = EntityAccount.objects.all()
    context = {
        'entity_accounts': entity_accounts,
    }
    return render(request, 'reports/entity_trial_balance.html', context)

def entity_cumulative_balance(request):
    # Assuming a simple cumulative balance based on ledger entries
    entity_accounts = EntityAccount.objects.all()
    context = {
        'entity_accounts': entity_accounts,
    }
    return render(request, 'reports/entity_cumulative_balance.html', context)


def sacco_trial_balance(request):
    sacco_accounts = SaccoAccount.objects.all()
    context = {
        'sacco_accounts': sacco_accounts,
    }
    return render(request, 'reports/sacco_trial_balance.html', context)

def sacco_cumulative_balance(request):
    # Assuming a simple cumulative balance based on ledger entries
    sacco_accounts = SaccoAccount.objects.all()
    context = {
        'sacco_accounts': sacco_accounts,
    }
    return render(request, 'reports/sacco_cumulative_balance.html', context)





