# views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import ExpenditureForm, AssetForm, SaccoAccountForm, ReportFilterForm
from .models import SaccoAccountsLedger, SaccoAccount
from django.db.models import Sum
from .models import SaccoCharge
from .forms import SaccoChargeForm
from django.contrib.auth.decorators import login_required
from .utils import generate_unique_ref_id



def add_expenditure(request):
    if request.method == 'POST':
        form = ExpenditureForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            description = form.cleaned_data['description']
            amount = form.cleaned_data['amount']

            try:
                # Use the ID of the selected account
                account_id = account.id

                # Create SaccoAccountsLedger instance
                SaccoAccountsLedger.objects.create(
                    account_id=account_id,
                    description=description,
                    amount=amount,
                    transaction_type='Dr'
                )

                messages.success(request, 'Expenditure recorded successfully.')
                return redirect('accounting:add_expenditure')

            except Exception as e:
                messages.error(request, f'Failed to record expenditure: {e}')
        else:
            messages.error(request, 'Form is not valid. Please check the input.')

    else:
        form = ExpenditureForm()

    return render(request, 'accounting/add_expenditure.html', {'form': form})

def add_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            description = form.cleaned_data['description']
            amount = form.cleaned_data['amount']

            try:
                # Use the ID of the selected account
                account_id = account.id

                # Create SaccoAccountsLedger instance
                SaccoAccountsLedger.objects.create(
                    account_id=account_id,
                    description=description,
                    amount=amount,
                    transaction_type='Cr'
                )

                messages.success(request, 'Asset recorded successfully.')
                return redirect('add_asset')

            except Exception as e:
                messages.error(request, f'Failed to record asset: {e}')
        else:
            messages.error(request, 'Form is not valid. Please check the input.')

    else:
        form = AssetForm()

    return render(request, 'accounting/add_asset.html', {'form': form})

@login_required
def add_account(request):
    if request.method == 'POST':
        form = SaccoAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account added successfully.')
            return redirect('accounting:add_account')
        else:
            messages.error(request, 'Form is not valid. Please check the input.')

    else:
        form = SaccoAccountForm()

    return render(request, 'accounting/add_account.html', {'form': form})


def view_chart_of_accounts(request):
    accounts = SaccoAccount.objects.all()
    return render(request, 'accounting/chart_of_accounts.html', {'accounts': accounts})

def generate_reports(request):
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            filters = {}
            if account:
                filters['account_id'] = account.id
            if start_date:
                filters['transaction_date__gte'] = start_date
            if end_date:
                filters['transaction_date__lte'] = end_date

            ledger_entries = SaccoAccountsLedger.objects.filter(**filters)
            total_amount = ledger_entries.aggregate(Sum('amount'))['amount__sum'] or 0

            return render(request, 'accounting/reports.html', {
                'form': form,
                'ledger_entries': ledger_entries,
                'total_amount': total_amount
            })

    else:
        form = ReportFilterForm()

    return render(request, 'accounting/reports.html', {'form': form})

def account_statement(request, account_id):
    account = SaccoAccount.objects.get(id=account_id)
    ledger_entries = SaccoAccountsLedger.objects.filter(account_id=account_id).order_by('transaction_date')
    return render(request, 'accounting/account_statement.html', {
        'account': account,
        'ledger_entries': ledger_entries
    })

@login_required
def add_sacco_charge(request):
    if request.method == 'POST':
        form = SaccoChargeForm(request.POST)
        if form.is_valid():
            sacco_charge = form.save(commit=False)
            sacco_charge.updated_by = request.user
            sacco_charge.save()
            messages.success(request, 'SACCO charge added successfully.')
            return redirect('accounting:list_sacco_charges')
    else:
        form = SaccoChargeForm()
    return render(request, 'accounting/add_sacco_charge.html', {'form': form})

@login_required
def update_sacco_charge(request, pk):
    sacco_charge = get_object_or_404(SaccoCharge, pk=pk)
    if request.method == 'POST':
        form = SaccoChargeForm(request.POST, instance=sacco_charge)
        if form.is_valid():
            sacco_charge = form.save(commit=False)
            sacco_charge.updated_by = request.user
            sacco_charge.save()
            messages.success(request, 'SACCO charge updated successfully.')
            return redirect('accounting:list_sacco_charges')
    else:
        form = SaccoChargeForm(instance=sacco_charge)
    return render(request, 'accounting/update_sacco_charge.html', {'form': form, 'sacco_charge': sacco_charge})

@login_required
def list_sacco_charges(request):
    sacco_charges = SaccoCharge.objects.all()
    return render(request, 'accounting/list_sacco_charges.html', {'sacco_charges': sacco_charges})
# views.py
import pandas as pd
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .forms import RawStatementUploadForm
from datetime import datetime
import os

def filter_and_format_excel(request):
    if request.method == 'POST':
        form = RawStatementUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                df = pd.read_excel(file, header=None, skiprows=6)  # Ignore first 6 rows

                # Extract relevant columns
                relevant_data = df.iloc[:, [0, 1, 5, 12]]  # Assuming columns by index

                # Rename columns based on position
                relevant_data.columns = ['receipt_no', 'completion_date', 'paid_in', 'account_no']

                # Filter out rows with null 'paid_in'
                relevant_data = relevant_data.dropna(subset=['paid_in'])

                # Generate timestamp for filename
                timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

                # Define folder to save filtered statements
                save_folder = 'filtered_statements'
                os.makedirs(save_folder, exist_ok=True)  # Create folder if not exists

                # Save filtered data to a new Excel sheet in specified folder
                filename = f'{save_folder}/filtered_statements_{timestamp}.xlsx'
                full_file_path = os.path.join(os.getcwd(), filename)  # Full path to the file
                relevant_data.to_excel(full_file_path, index=False)

                messages.success(request, 'Excel sheet filtered and formatted successfully.')
                return render(request, 'accounting/format_success.html', {'filename': filename})

            except Exception as e:
                messages.error(request, f"Error processing the file: {str(e)}")
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = RawStatementUploadForm()

    return render(request, 'accounting/format_raw_statement.html', {'form': form})
# views.py
from django.shortcuts import HttpResponse, redirect
from django.contrib import messages
import os

def download_filtered_statement(request, filename):
    file_path = os.path.join(os.getcwd(), filename)  # Full path to the file

    try:
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        else:
            messages.error(request, 'File not found.')
            return redirect('accounting:filter_and_format_excel')
    except Exception as e:
        messages.error(request, f"Error downloading the file: {str(e)}")
        return redirect('accounting:filter_and_format_excel')
    
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MpesaReconciliationForm
from .models import MpesaReconciliationLedger
from .utils import process_reconciliation_entries
from decimal import Decimal

def mpesa_reconciliation_upload(request):
    if request.method == 'POST':
        form = MpesaReconciliationForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            priority = form.cleaned_data['priority']

            try:
                df = pd.read_excel(file)

                # Ensure the required columns are present
                required_columns = ['receipt_no', 'paid_in', 'account_no']
                if not all(col in df.columns for col in required_columns):
                    messages.error(request, 'Excel file must contain receipt_no, paid_in, and account_no columns.')
                    return redirect('accounting:mpesa_reconciliation_upload')

                # Filter out rows with null 'paid_in'
                df = df.dropna(subset=['paid_in'])

                entries = []
                for _, row in df.iterrows():
                    try:
                        paid_in = Decimal(row['paid_in'])

                        entry = MpesaReconciliationLedger(
                            receipt_no=row['receipt_no'],
                            paid_in=paid_in,
                            account_no=row['account_no'],
                            priority=priority,
                            reconciled=False
                        )
                        entries.append(entry)
                    except (ValueError, TypeError) as e:
                        messages.error(request, f"Invalid data format in row: {row.to_dict()} - {str(e)}")
                        continue

                MpesaReconciliationLedger.objects.bulk_create(entries)
                process_reconciliation_entries(entries)

                messages.success(request, 'File processed successfully.')
                return redirect('accounting:mpesa_reconciliation_upload')

            except Exception as e:
                messages.error(request, f"Error processing the file: {str(e)}")
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = MpesaReconciliationForm()

    return render(request, 'accounting/mpesa_reconciliation_upload.html', {'form': form})
# accounting/views.py

from django.shortcuts import render
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import MpesaReconciliationLedger

def view_reconciliation_records(request):
    query = MpesaReconciliationLedger.objects.all()
    
    # Filtering by date
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if start_date and end_date:
            query = query.filter(reconciled_at__date__range=(start_date, end_date))

    # Filtering by reconciliation status
    reconciled = request.GET.get('reconciled')
    if reconciled == 'true':
        query = query.filter(reconciled=True)
    elif reconciled == 'false':
        query = query.filter(reconciled=False)

    context = {
        'reconciliation_records': query,
        'start_date': start_date,
        'end_date': end_date,
        'reconciled': reconciled,
    }

    return render(request, 'accounting/view_reconciliation_records.html', context)

def get_unique_external_ref_code(account_holder_id, ledger_model):
    # Generate a unique reference code based on account holder ID and current timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'{account_holder_id}-{timestamp}'
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from members.models import Member, MemberAccount, MemberAccountsLedger
from loans.models import IssuedLoan
from groups.models import Entity, EntityAccount, EntityAccountsLedger
from accounting.models import MpesaReconciliationLedger
from decimal import Decimal, InvalidOperation
import json
import logging
from datetime import datetime
import re


# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def process_payment_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received data: {data}")
            
            trans_amount = data.get('TransAmount')
            if trans_amount is None:
                logger.error("Transaction amount is None")
                return JsonResponse({"ResultCode": "C2B00013", "ResultDesc": "Invalid Amount"}, status=400)
            
            try:
                trans_amount = Decimal(trans_amount)
            except InvalidOperation:
                logger.error("Invalid operation while converting trans_amount to Decimal")
                return JsonResponse({"ResultCode": "C2B00013", "ResultDesc": "Invalid Amount"}, status=400)

            transaction_type = data.get('TransactionType')
            trans_id = data.get('TransID')
            trans_time = data.get('TransTime')
            bill_ref_number = data.get('BillRefNumber')
            msisdn = data.get('MSISDN')

            if not all([transaction_type, trans_id, trans_time, bill_ref_number, msisdn]):
                logger.error("One or more required fields are missing in the data")
                return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Missing required fields"}, status=400)

            # Validate bill_ref_number
            if not re.match(r'^[a-zA-Z0-9/]*$', bill_ref_number):
                logger.error("BillRefNumber contains invalid characters")
                return JsonResponse({"ResultCode": "C2B00012", "ResultDesc": "Invalid Account Number"}, status=400)

            try:
                trans_time = datetime.strptime(trans_time, "%Y%m%d%H%M%S")
            except ValueError:
                logger.error("Invalid transaction time format")
                return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Invalid Transaction Time"}, status=400)

            if '/' in bill_ref_number:
                trans_type, account_ref = bill_ref_number.split('/')
            else:
                trans_type = None
                account_ref = bill_ref_number

            # Check if the trans_id or trans_id with _1 suffix already exists
            if MemberAccountsLedger.objects.filter(external_ref_code__in=[trans_id, f"{trans_id}_1"]).exists() or \
               EntityAccountsLedger.objects.filter(external_ref_code__in=[trans_id, f"{trans_id}_1"]).exists():
                logger.error(f"Transaction ID {trans_id} already used")
                return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Duplicate Transaction ID"}, status=400)
            
            try:
                if account_ref.isdigit():
                    # It's a member
                    account_holder = Member.objects.get(id=account_ref)
                else:
                    # It's an entity
                    account_holder = Entity.objects.get(id=account_ref)

                if trans_type and trans_type.lower() == 'loan':
                    process_loan_payment(account_holder, trans_amount, trans_id)
                elif trans_type and trans_type.lower() == 'savings':
                    process_savings_deposit(account_holder, trans_amount, trans_id)
                else:
                    process_general_payment(account_holder, trans_amount, trans_id)

                return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})
            
            except (Member.DoesNotExist, Entity.DoesNotExist):
                logger.warning(f"Account holder not found for reference: {account_ref}")
                MpesaReconciliationLedger.objects.create(
                    receipt_no=trans_id,
                    completion_date=trans_time,
                    paid_in=trans_amount,
                    account_no=bill_ref_number,
                    priority='',
                    reconciled=False
                )
                return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Other Error"})
        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
            return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Other Error"}, status=400)

def process_loan_payment(account_holder, amount, trans_id):
    try:
        if isinstance(account_holder, Member):
            account = MemberAccount.objects.get(member=account_holder)
        else:
            account = EntityAccount.objects.get(entity=account_holder)
        
        active_loan = IssuedLoan.objects.filter(object_id=account_holder.id, loan_status='active').first()
        if active_loan:
            loan_repayment_amount = amount
            active_loan.loan_balance -= loan_repayment_amount
            active_loan.save()
            record_transaction(account_holder, loan_repayment_amount, trans_id, 'loan')
        else:
            account.savings += amount
            account.save()
            record_transaction(account_holder, amount, trans_id, 'savings')
    except Exception as e:
        logger.error(f"Error in process_loan_payment: {e}")
        raise e

def process_savings_deposit(account_holder, amount, trans_id):
    try:
        if isinstance(account_holder, Member):
            account = MemberAccount.objects.get(member=account_holder)
        else:
            account = EntityAccount.objects.get(entity=account_holder)
        
        account.savings += amount
        account.save()
        record_transaction(account_holder, amount, trans_id, 'savings')
    except Exception as e:
        logger.error(f"Error in process_savings_deposit: {e}")
        raise e

def process_general_payment(account_holder, amount, trans_id):
    try:
        if isinstance(account_holder, Member):
            account = MemberAccount.objects.get(member=account_holder)
        else:
            account = EntityAccount.objects.get(entity=account_holder)

        active_loan = IssuedLoan.objects.filter(object_id=account_holder.id, loan_status='active').first()
        if active_loan:
            installment_amount = active_loan.installment_amount
            loan_repayment_amount = min(amount, installment_amount)
            savings_amount = amount - loan_repayment_amount
            
            if loan_repayment_amount > 0:
                active_loan.loan_balance -= loan_repayment_amount
                active_loan.save()
                record_transaction(account_holder, loan_repayment_amount, trans_id, 'loan')
            
            if savings_amount > 0:
                account.savings += savings_amount
                account.save()
                record_transaction(account_holder, savings_amount, f"{trans_id}_1", 'savings')
        else:
            account.savings += amount
            account.save()
            record_transaction(account_holder, amount, trans_id, 'savings')
    except Exception as e:
        logger.error(f"Error in process_general_payment: {e}")
        raise e

def record_transaction(account_holder, amount, trans_id, tr_account):
    try:
        if isinstance(account_holder, Member):
            MemberAccountsLedger.objects.create(
                member_id=account_holder,
                tr_amount=amount,
                tr_type='credit',
                account_id=1,
                tr_account=tr_account,
                tr_mode_id=1,  # Assuming 1 for Mpesa
                tr_origin='mpesa',
                tr_destn='member account',
                external_ref_code=trans_id,
            )
        else:
            EntityAccountsLedger.objects.create(
                entity=account_holder,
                tr_amount=amount,
                tr_type='credit',
                tr_account=tr_account,
                tr_mode_id=1,  # Assuming 1 for Mpesa
                tr_origin='mpesa',
                tr_destn='entity account',
                external_ref_code=trans_id,
            )
    except Exception as e:
        logger.error(f"Error in record_transaction: {e}")
        raise e
    
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import DailyAccountsPostingForm
from members.models import MemberAccountsLedger
from groups.models import EntityAccountsLedger
from reports.utils import generate_pdf_report, generate_excel_report
import logging

logger = logging.getLogger(__name__)

@login_required
def daily_accounts_posting(request):
    form = DailyAccountsPostingForm()
    transactions = []

    if request.method == 'POST':
        form = DailyAccountsPostingForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = timezone.datetime.combine(date, timezone.datetime.min.time()).replace(hour=1, minute=0)
            end_time = timezone.datetime.combine(date, timezone.datetime.min.time()).replace(hour=19, minute=0)
            logger.info(f'Fetching transactions from {start_time} to {end_time}')

            member_transactions = MemberAccountsLedger.objects.filter(updated_at__range=(start_time, end_time))
            entity_transactions = EntityAccountsLedger.objects.filter(updated_at__range=(start_time, end_time))
            transactions = list(member_transactions) + list(entity_transactions)

            logger.info(f'Transactions fetched: {len(transactions)}')

            if 'download' in request.POST:
                format = request.POST.get('format', 'pdf')
                context = {
                    'transactions': transactions,
                    'date': date,
                    'form': form,
                }
                if format == 'pdf':
                    logger.info('Generating PDF report')
                    return generate_pdf_report(context, 'reports/daily_accounts_posting_pdf.html')
                elif format == 'excel':
                    logger.info('Generating Excel report')
                    return generate_excel_report(transactions, 'daily_accounts_posting')

    context = {
        'form': form,
        'transactions': transactions,
    }
    return render(request, 'accounting/daily_accounts_posting.html', context)
