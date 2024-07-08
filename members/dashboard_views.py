from django.shortcuts import render, redirect
from django.db.models import Sum
from .forms import MemberForm, MemberAccountForm, NextOfKinForm
from .models import Member, MemberAccount, NextOfKin
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def dashboard(request):
    current_time = timezone.now()
    context = {
    'current_time': current_time,
    }
    members_count = Member.objects.count()
    total_savings = MemberAccount.objects.aggregate(Sum('savings'))['savings__sum'] or 0
    total_share_capital = MemberAccount.objects.aggregate(Sum('share_capital'))['share_capital__sum'] or 0
    context = {
        'members_count': members_count,
        'total_savings': total_savings,
        'total_share_capital': total_share_capital,
    }
    return render(request, 'members/dashboard.html', context)