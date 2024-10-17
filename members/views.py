from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Member, MemberAccount, NextOfKin,MemberAccountsLedger
from .forms import MemberForm, NextOfKinForm

@login_required
def search_member_to_edit(request):
    query = request.GET.get('q')
    members = Member.objects.all()

    if query:
        members = members.filter(first_name__icontains=query)
    
    return render(request, 'members/search_member_1.html', {'members': members})

@login_required
def mini_statement_form(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        member = get_object_or_404(Member, pk=member_id)
        transactions = MemberAccountsLedger.filterobjects.all(member_id=member_id)
        return render(request, 'members/mini_statement.html', {'member': member, 'transactions': transactions})
    
    members = Member.objects.all()
    return render(request, 'members/mini_statement_form.html', {'members': members})

@login_required
def savings_report(request):
    accounts = MemberAccount.objects.all()
    return render(request, 'members/savings_report.html', {'accounts': accounts})

@login_required
def loans_report(request):
    loans = MemberAccount.objects.filter(account_type='savings')
    return render(request, 'members/loans_report.html', {'loans': loans})

@login_required
def share_capital_report(request):
    accounts = MemberAccount.objects.filter(account_type='share_capital')
    return render(request, 'members/share_capital_report.html', {'accounts': accounts})

@login_required
def all_accounts_report(request):
    accounts = MemberAccount.objects.all()
    return render(request, 'members/all_accounts_report.html', {'accounts': accounts})

@login_required
def edit_personal_details(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal details updated successfully!')
            return redirect('members:edit_personal_details', member_id=member.id)
    else:
        form = MemberForm(instance=member)
    return render(request, 'members/edit_personal_details.html', {'form': form})

@login_required
def edit_next_of_kin(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    next_of_kin = member.nextofkin
    if request.method == 'POST':
        form = NextOfKinForm(request.POST, instance=next_of_kin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Next of kin details updated successfully!')
            return redirect('members:edit_next_of_kin', member_id=member.id)
    else:
        form = NextOfKinForm(instance=next_of_kin)
    return render(request, 'members/edit_next_of_kin.html', {'form': form})

@login_required
def register_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member registered successfully!')
            return redirect('members:register_member')
    else:
        form = MemberForm()
    return render(request, 'members/register_member.html', {'form': form})

@login_required
def deactivate_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    member.is_active = False
    member.save()
    messages.success(request, 'Member deactivated successfully!')
    return redirect('members:deactivate_member')

@login_required
def membership_stats(request):
    active_members = Member.objects.filter(is_active=True).count()
    inactive_members = Member.objects.filter(is_active=False).count()
    return render(request, 'members/membership_stats.html', {
        'active_members': active_members,
        'inactive_members': inactive_members
    })

@login_required
def accounts_stats(request):
    total_savings = MemberAccount.objects.filter(account_type='savings').aggregate(Sum('balance'))['balance__sum']
    total_loans = MemberAccount.objects.filter(account_type='loan').aggregate(Sum('balance'))['balance__sum']
    return render(request, 'members/accounts_stats.html', {
        'total_savings': total_savings,
        'total_loans': total_loans
    })

@login_required
def member_joining_stats(request):
    # Example implementation
    members_joined_last_month = Member.objects.filter(joined_date__month=last_month).count()
    return render(request, 'members/member_joining_stats.html', {
        'members_joined_last_month': members_joined_last_month
    })

@login_required
def dormant_members(request):
    dormant_members = Member.objects.filter(is_active=False)
    return render(request, 'members/dormant_members.html', {'dormant_members': dormant_members})

@login_required
def deceased_members(request):
    deceased_members = Member.objects.filter(status='deceased')
    return render(request, 'members/deceased_members.html', {'deceased_members': deceased_members})

@login_required
def top_savers(request):
    account_type ='savings'
    top_savers = MemberAccount.objects.filter(account_type).order_by('-account_type')[:10]
    return render(request, 'members/top_savers.html', {'top_savers': top_savers})

@login_required
def top_borrowers(request):
    top_borrowers = MemberAccount.objects.filter(account_type='loan').order_by('-balance')[:10]
    return render(request, 'members/top_borrowers.html', {'top_borrowers': top_borrowers})

@login_required
def non_member_next_of_kins(request):
    non_members = NextOfKin.objects.filter(member__isnull=True)
    return render(request, 'members/non_member_next_of_kins.html', {'non_members': non_members})
