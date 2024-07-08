from django.shortcuts import render,get_object_or_404
from .models import Member, MemberAccount,Transaction
from .forms import MiniStatementForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime

# Get the current time in the current time zone
current_time = timezone.now()

@login_required
def view_members(request):
    members = Member.objects.all().select_related('memberaccount')
    context = {'members': members}
    return render(request, 'members/view_members.html', context)


@login_required
def member_profile(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    savings = member.memberaccount.savings
    loan = member.memberaccount.loan
    potential_loan = (savings * 3) - loan

    context = {
        'member': member,
        'potential_loan': potential_loan,
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
