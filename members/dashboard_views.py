from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q
from .forms import MemberForm, MemberAccountForm, NextOfKinForm
from .models import Member, MemberAccount, NextOfKin
from loans.models import IssuedLoan
from groups.models import Entity
from accounting.models import SaccoAccount, MpesaReconciliationLedger
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def dashboard(request):
    current_time = timezone.now()

    # Members and Entities stats
    members_count = Member.objects.count()
    entities_count = Entity.objects.count()

    # Financial stats
    total_savings = MemberAccount.objects.aggregate(Sum('savings'))['savings__sum'] or 0
    total_share_capital = MemberAccount.objects.aggregate(Sum('share_capital'))['share_capital__sum'] or 0

    # Loan stats
    active_loans = IssuedLoan.objects.filter(loan_status='active').count()
    pending_loans = IssuedLoan.objects.filter(loan_status='pending').count()
    defaulted_loans = IssuedLoan.objects.filter(loan_status='defaulted').count()
    total_loan_amount = IssuedLoan.objects.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    total_repaid_amount = IssuedLoan.objects.aggregate(Sum('loan_balance'))['loan_balance__sum'] or 0

    # SaccoAccount stats
    sacco_accounts_count = SaccoAccount.objects.count()
    total_account_balance = SaccoAccount.objects.aggregate(Sum('account_balance'))['account_balance__sum'] or 0

    # MpesaReconciliationLedger stats
    total_reconciled = MpesaReconciliationLedger.objects.filter(reconciled=True).count()
    total_unreconciled = MpesaReconciliationLedger.objects.filter(reconciled=False).count()
    total_paid_in = MpesaReconciliationLedger.objects.aggregate(Sum('paid_in'))['paid_in__sum'] or 0


    context = {
        'current_time': current_time,
        'members_count': members_count,
        'entities_count': entities_count,
        'total_savings': total_savings,
        'total_share_capital': total_share_capital,
        'active_loans': active_loans,
        'pending_loans': pending_loans,
        'defaulted_loans': defaulted_loans,
        'total_loan_amount': total_loan_amount,
        'total_repaid_amount': total_repaid_amount,
        'sacco_accounts_count': sacco_accounts_count,
        'total_account_balance': total_account_balance,
        'total_reconciled': total_reconciled,
        'total_unreconciled': total_unreconciled,
        'total_paid_in': total_paid_in,
       
    }
    return render(request, 'members/dashboard.html', context)
