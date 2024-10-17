from django.shortcuts import render,get_object_or_404
from .models import Member, MemberAccount,Transaction
from .forms import MiniStatementForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from loans.models import IssuedLoan, Collateral, Guarantor

# Get the current time in the current time zone
current_time = timezone.now()
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Member
from loans. models import IssuedLoan

from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def view_members(request):
    query = request.GET.get('q')
    
    if query:
        members = Member.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query) |
            Q(id__icontains=query)
        ).select_related('memberaccount').order_by('-id')
    else:
        members = Member.objects.all().select_related('memberaccount').order_by('-id')[:100]
    
    active_loans = IssuedLoan.objects.filter(
        loan_status='active',
        content_type=ContentType.objects.get_for_model(Member)
    )
    
    # Annotate each member with their active loan amount
    member_loan_data = {
        loan.object_id: loan.loan_balance
        for loan in active_loans
    }
    
    context = {
        'members': members,
        'member_loan_data': member_loan_data,
        'query': query
    }
    return render(request, 'members/view_members.html', context)




from django.db.models import Sum

@login_required
def member_profile(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    # Fetch active loans and calculate their total principal and balance
    active_loans = IssuedLoan.objects.filter(object_id=str(member.id), loan_status='active')
    active_loan_principal = active_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    active_loan_balance = active_loans.aggregate(Sum('loan_balance'))['loan_balance__sum'] or 0
    
    # Fetch all loans and calculate their total balance
    all_loans = IssuedLoan.objects.filter(object_id=str(member.id))
    total_loans_taken = all_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    
    context = {
        'member': member,
        'active_loan_principal': active_loan_principal,
        'total_loans_taken': total_loans_taken,
        'active_loan_balance': active_loan_balance,
    }
    return render(request, 'member_profile.html', context)

@login_required
def view_transactions(request):
    transactions = Transaction.objects.all()
    return render(request, 'members/transactions.html', {'transactions': transactions})
@login_required
def mini_statement_form(request):
    form = MiniStatementForm()
    return render(request, 'members/mini_statement_form.html', {'form': form})
@login_required
def mini_statement_view(request):
    if request.method == 'POST':
        # Process POST request
        form = MiniStatementForm(request.POST)
        if form.is_valid():
            # Extract form data
            member_id = form.cleaned_data['member_id']
            account_type = form.cleaned_data['account_type']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Query member account
            try:
                member_account = MemberAccount.objects.get(member_id=member_id)
            except MemberAccount.DoesNotExist:
                return HttpResponse("Member account not found.")

            # Fetch balance from member account based on account type
            if account_type == 'savings':
                balance_bf = member_account.savings
            elif account_type == 'share_capital':
                balance_bf = member_account.share_capital
            elif account_type == 'loan':
                balance_bf = member_account.loan
            else:
                return HttpResponse("Invalid account type.")

            # Query transactions based on account type and date range
            transactions = Transaction.objects.filter(
                member_id_id=member_id,
                tr_account=account_type,
                updated_date__range=(start_date, end_date)
            ).order_by('updated_date')

            # Prepare context
            context = {
                'member_account': member_account,
                'account_type': account_type,
                'start_date': start_date,
                'end_date': end_date,
                'transactions': transactions,
                'balance_bf': balance_bf,
            }

            # Render template
            return render(request, 'members/mini_statement.html', context)
    else:
        # Display form for GET request
        form = MiniStatementForm()
        
    # Render form template
    return render(request, 'members/mini_statement_form.html', {'form': form})
