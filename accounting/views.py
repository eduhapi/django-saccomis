# views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import ExpenditureForm, AssetForm, SaccoAccountForm, ReportFilterForm
from .models import SaccoAccountsLedger, SaccoAccount
from django.db.models import Sum
from .models import SaccoCharge
from .forms import SaccoChargeForm
from django.contrib.auth.decorators import login_required



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

def add_account(request):
    if request.method == 'POST':
        form = SaccoAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account added successfully.')
            return redirect('accounting/add_account')
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

