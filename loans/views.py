from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LoanProduct, IssuedLoan, Collateral, Guarantor
from .forms import LoanProductForm, MemberSearchForm, IssueLoanForm, CollateralForm, LoanEligibilityForm, CollateralForm, GuarantorForm
from members.models import Member, MemberAccount, Transaction  # Assuming you have a Member model
from groups.models import Entity, EntityAccount, EntityAccountsLedger  # Assuming you have an Entity model
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .utils import generate_unique_loan_ref_id
from django.conf import settings  # for getting the user model
from sms.utils import send_notification  # Import the send_notification function
from django.db.models import F
from datetime import timedelta
from decimal import Decimal, getcontext

# Set precision for Decimal calculations
getcontext().prec = 28


@login_required
def search_member_or_entity(request):
    member = None
    entity = None
    savings_amount = 0
    loan_amount = 0
    guaranteed_amount = 0

    if request.method == 'POST':
        form = MemberSearchForm(request.POST)
        if form.is_valid():
            member_or_entity_id = form.cleaned_data['member_id']
            if member_or_entity_id.isdigit():
                try:
                    member = Member.objects.get(id=int(member_or_entity_id))
                    account = MemberAccount.objects.get(member=member)
                    savings_amount = account.savings
                    loan_amount = account.loan
                    guaranteed_amount = Guarantor.objects.filter(guarantor=member).aggregate(total=Sum('guarantee_amount'))['total'] or 0
                except Member.DoesNotExist:
                    form.add_error('member_id', 'Member not found.')
            else:
                try:
                    entity = Entity.objects.get(id=member_or_entity_id)
                    entity_account = EntityAccount.objects.get(entity=entity)
                    savings_amount = entity_account.savings
                    loan_amount = entity_account.loan
                except Entity.DoesNotExist:
                    form.add_error('member_id', 'Entity not found.')
    else:
        form = MemberSearchForm()

    context = {
        'form': form,
        'member': member,
        'entity': entity,
        'savings_amount': savings_amount,
        'loan_amount': loan_amount,
        'guaranteed_amount': guaranteed_amount,
    }
    return render(request, 'loans/search_member_or_entity.html', context)


@login_required
def member_details(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    account = get_object_or_404(MemberAccount, member=member)
    savings_amount = account.savings
    loan_amount = account.loan
    guaranteed_amount = Guarantor.objects.filter(guarantor=member).aggregate(total=Sum('guarantee_amount'))['total'] or 0
    context = {
        'member': member,
        'savings_amount': savings_amount,
        'loan_amount': loan_amount,
        'guaranteed_amount': guaranteed_amount,
    }
    return render(request, 'loans/member_details.html', context)

@login_required
def entity_details(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    entity_account = get_object_or_404(EntityAccount, entity=entity)
    context = {
        'entity': entity,
        'entity_account': entity_account,
    }
    return render(request, 'loans/entity_details.html', context)

@login_required
def start_application_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    return render(request, 'loans/start_application_member.html', {'member': member})

@login_required
def start_application_entity(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    return render(request, 'loans/start_application_entity.html', {'entity': entity})

from django.contrib.contenttypes.models import ContentType

@login_required
def loan_details_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member_account = get_object_or_404(MemberAccount, member=member)

    if request.method == 'POST':
        form = IssueLoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.content_type = ContentType.objects.get_for_model(member)
            loan.object_id = member.id

            loan_amount = form.cleaned_data['loan_amount']
            repayment_period = form.cleaned_data['repayment_period']

            processing_fee = Decimal('1500')
            net_loan_amount = loan_amount - processing_fee

            interest_rate = Decimal('0.01')
            months = Decimal(repayment_period)
            numerator = loan_amount * interest_rate * (1 + interest_rate) ** months
            denominator = (1 + interest_rate) ** months - 1
            installment_amount = numerator / denominator

            eligibility_results = check_loan_eligibility_member(member, net_loan_amount)

            if eligibility_results['qualified']:
                loan.installment_amount = installment_amount
                loan.loan_ref_id = generate_unique_loan_ref_id()
                loan.processed_by = request.user
                loan.loan_amount = loan_amount
                loan.save()

                return redirect('loans:collaterals', member_id=member.id, loan_id=loan.id)
            else:
                context = {
                    'member': member,
                    'loan_amount': loan_amount,
                    'eligibility_results': eligibility_results,
                }
                return render(request, 'loans/loan_eligibility_summary.html', context)
    else:
        form = IssueLoanForm()

    return render(request, 'loans/loan_details.html', {'form': form, 'member': member})

@login_required
def loan_details_entity(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    entity_account = get_object_or_404(EntityAccount, entity=entity)

    if request.method == 'POST':
        form = IssueLoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.content_type = ContentType.objects.get_for_model(entity)
            loan.object_id = entity.id

            loan_amount = form.cleaned_data['loan_amount']
            repayment_period = form.cleaned_data['repayment_period']

            processing_fee = Decimal('1500')
            net_loan_amount = loan_amount - processing_fee

            interest_rate = Decimal('0.01')
            months = Decimal(repayment_period)
            numerator = loan_amount * interest_rate * (1 + interest_rate) ** months
            denominator = (1 + interest_rate) ** months - 1
            installment_amount = numerator / denominator

            eligibility_results = check_loan_eligibility_entity(entity, net_loan_amount)

            if eligibility_results['qualified']:
                loan.installment_amount = installment_amount
                loan.loan_ref_id = generate_unique_loan_ref_id()
                loan.processed_by = request.user
                loan.loan_amount = loan_amount
                loan.loan_balance = loan_amount
                loan.save()

                return redirect('loans:collaterals_entity', entity_id=entity.id, loan_id=loan.id)
            else:
                context = {
                    'entity': entity,
                    'loan_amount': loan_amount,
                    'eligibility_results': eligibility_results,
                }
                return render(request, 'loans/loan_eligibility_entity.html', context)
    else:
        form = IssueLoanForm()

    return render(request, 'loans/loan_details.html', {'form': form, 'entity': entity})



def loan_eligibility_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = LoanEligibilityForm(request.POST)
        if form.is_valid():
            loan_amount = form.cleaned_data['loan_amount']
            eligibility_results = check_loan_eligibility_member(member, loan_amount)
            context = {
                'member': member,
                'loan_amount': loan_amount,
                'eligibility_results': eligibility_results,
            }
            return render(request, 'loans/loan_eligibility_member.html', context)
    else:
        form = LoanEligibilityForm()
    
    return render(request, 'loans/loan_eligibility_member.html', {'form': form, 'member': member})

@login_required
def loan_eligibility_entity(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    
    if request.method == 'POST':
        form = LoanEligibilityForm(request.POST)
        if form.is_valid():
            loan_amount = form.cleaned_data['loan_amount']
            eligibility_results = check_loan_eligibility_entity(entity, loan_amount)
            context = {
                'entity': entity,
                'loan_amount': loan_amount,
                'eligibility_results': eligibility_results,
            }
            return render(request, 'loans/loan_eligibility_entity.html', context)
    else:
        form = LoanEligibilityForm()
    
    return render(request, 'loans/loan_eligibility_entity.html', {'form': form, 'entity': entity})


def check_loan_eligibility_member(member, loan_amount):
    # Implement your eligibility checks based on the loan amount
    eligibility_results = {
        'qualified': True,
        'reasons': []
    }
     # Sum of guarantee_amount for the member as a guarantor
    #guaranteed_amount = Guarantor.objects.filter(guarantor=member).aggregate(total=Sum('guarantee_amount'))['total'] or 0
    guaranteed_amount = Guarantor.objects.filter(guarantor=member, loan_status__in=['active', 'pending']).aggregate(total=Sum('guarantee_amount'))['total'] or 0
    # Check free savings (loan_amount / 3)
    free_savings = member.memberaccount.savings - guaranteed_amount# Adjust this to calculate free savings correctly
    if loan_amount / 3 > free_savings:
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Insufficient free savings.')
    
    # Check existing loan balance
    if member.memberaccount.loan != 0:
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Existing loan balance must be 0.')
    
    # Check consistent savings for the last 6 months (for testing, check last 3 days)
    three_days_ago = timezone.now() - timedelta(days=3)  # For testing, change to 6 months
    savings_transactions = Transaction.objects.filter(
        member_id=member, tr_account='savings', updated_date__gte=three_days_ago
    )
    if savings_transactions.count() < 6:
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Inconsistent savings.')
    
    # Check membership duration (for testing, check last 3 days)
    if member.registration_date > (timezone.now() - timedelta(days=3)).date():
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Insufficient membership duration.')
    
    return eligibility_results

def check_loan_eligibility_entity(entity, loan_amount):
    eligibility_results = {
        'qualified': True,
        'reasons': []
    }
    entity_account = entity.account # Ensure you get the first EntityAccount

    # Check if the loan amount is not more than 3 times the entity's savings
    if loan_amount > 3 * entity_account.savings:
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Loan amount exceeds 3 times the entity\'s savings.')
    # Check for unsettled loans
    unsettled_loans = IssuedLoan.objects.filter(object_id=entity.id, loan_status='active')
    if unsettled_loans.exists():
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Entity has unsettled loans.')

    # Check for consistent savings transactions
    six_months_ago = timezone.now() - timedelta(days=180)
    savings_transactions = EntityAccountsLedger.objects.filter(
        entity=entity, tr_account='savings', updated_at__gte=six_months_ago
    )

    if savings_transactions.count() < 6:
        eligibility_results['qualified'] = False
        eligibility_results['reasons'].append('Inconsistent savings.')

    return eligibility_results

@login_required
def collaterals(request, member_id, loan_id):
    member = get_object_or_404(Member, id=member_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    
    if request.method == 'POST':
        form = CollateralForm(request.POST)
        if form.is_valid():
            collateral = form.save(commit=False)
            collateral.loan = loan
            collateral.save()
            messages.success(request, 'Collateral added successfully.')
            return redirect('loans:collaterals', member_id=member.id, loan_id=loan.id)
    else:
        form = CollateralForm()
    
    collaterals = Collateral.objects.filter(loan=loan)
    return render(request, 'loans/collaterals.html', {'form': form, 'member': member, 'loan': loan, 'collaterals': collaterals})
@login_required
def collaterals_entity(request, entity_id, loan_id):
    entity = get_object_or_404(Entity, id=entity_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    
    if request.method == 'POST':
        form = CollateralForm(request.POST)
        if form.is_valid():
            collateral = form.save(commit=False)
            collateral.loan = loan
            collateral.save()
            messages.success(request, 'Collateral added successfully.')
            return redirect('loans:collaterals_entity', entity_id=entity.id, loan_id=loan.id)
    else:
        form = CollateralForm()
    
    collaterals = Collateral.objects.filter(loan=loan)
    return render(request, 'loans/collaterals_entity.html', {'form': form, 'entity': entity, 'loan': loan, 'collaterals': collaterals})
@login_required
def guarantors(request, member_id, loan_id):
    member = get_object_or_404(Member, id=member_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    
    if request.method == 'POST':
        form = GuarantorForm(request.POST)
        if form.is_valid():
            guarantor_id = form.cleaned_data['guarantor_id']
            guarantor_member = get_object_or_404(Member, id=guarantor_id)
            
            guarantor = form.save(commit=False)
            guarantor.loan = loan
            guarantor.guarantor = guarantor_member
            guarantor.updated_by = request.user.username
            guarantor.save()
            
            messages.success(request, 'Guarantor added successfully.')
            return redirect('loans:guarantors', member_id=member.id, loan_id=loan.id)
    else:
        form = GuarantorForm()
    
    guarantors = Guarantor.objects.filter(loan=loan)
    return render(request, 'loans/guarantors.html', {'form': form, 'member': member, 'loan': loan, 'guarantors': guarantors})
@login_required
def guarantors_entity(request, entity_id, loan_id):
    entity = get_object_or_404(Entity, id=entity_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    
    if request.method == 'POST':
        form = GuarantorForm(request.POST)
        if form.is_valid():
            guarantor_id = form.cleaned_data['guarantor_id']
            guarantor_member = get_object_or_404(Member, id=guarantor_id)
            
            guarantor = form.save(commit=False)
            guarantor.loan = loan
            guarantor.guarantor = guarantor_member
            guarantor.updated_by = request.user.username
            guarantor.save()
            
            messages.success(request, 'Guarantor added successfully.')
            return redirect('loans:guarantors_entity', entity_id=entity.id, loan_id=loan.id)
    else:
        form = GuarantorForm()
    
    guarantors = Guarantor.objects.filter(loan=loan)
    return render(request, 'loans/guarantors_entity.html', {'form': form, 'entity': entity, 'loan': loan, 'guarantors': guarantors})



@login_required
def collateral_and_guarantor_check(request, member_id, loan_id):
    member = get_object_or_404(Member, id=member_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    collaterals = Collateral.objects.filter(loan=loan)
    guarantors = Guarantor.objects.filter(loan=loan)
    
    total_collateral_value = collaterals.aggregate(total=Sum('value'))['total'] or 0
    total_guarantor_value = guarantors.aggregate(total=Sum('guarantee_amount'))['total'] or 0
    total_value = total_collateral_value + total_guarantor_value
    
    # Check if any guarantor's guarantee amount exceeds their free savings
    insufficient_guarantors = []
    for guarantor in guarantors:
        # Calculate free savings for each guarantor
        member_account = MemberAccount.objects.get(member=guarantor.guarantor)
        savings = member_account.savings
        #guaranteed_amount = Guarantor.objects.filter(guarantor=guarantor.guarantor).aggregate(total=Sum('guarantee_amount'))['total'] or 0
        guaranteed_amount = Guarantor.objects.filter(guarantor=member, loan_status__in=['active', 'pending']).aggregate(total=Sum('guarantee_amount'))['total'] or 0
        free_savings = savings - guaranteed_amount
        
        # Check if guarantee amount exceeds free savings
        if guarantor.guarantee_amount > free_savings:
            insufficient_guarantors.append({
                'guarantor': guarantor.guarantor,
                'guarantee_amount': guarantor.guarantee_amount,
                'free_savings': free_savings,
            })

    context = {
        'member': member,
        'loan': loan,
        'total_value': total_value,
        'required_value': loan.loan_amount,
        'collaterals': collaterals,
        'guarantors': guarantors,
        'is_sufficient': total_value >= loan.loan_amount and not insufficient_guarantors,
        'insufficient_guarantors': insufficient_guarantors,
    }
        
    return render(request, 'loans/collateral_and_guarantor_check.html', context)
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from members.models import MemberAccount
from groups.models import Entity
from loans.models import IssuedLoan, Collateral, Guarantor

@login_required
def collateral_and_guarantor_check_entity(request, entity_id, loan_id):
    entity = get_object_or_404(Entity, id=entity_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    
    collaterals = Collateral.objects.filter(loan=loan)
    guarantors = Guarantor.objects.filter(loan=loan)
    
    total_collateral_value = collaterals.aggregate(total=Sum('value'))['total'] or 0
    total_guarantor_value = guarantors.aggregate(total=Sum('guarantee_amount'))['total'] or 0
    total_value = total_collateral_value + total_guarantor_value
    
    # Check if any guarantor's guarantee amount exceeds their free savings
    insufficient_guarantors = []
    for guarantor in guarantors:
        # Calculate free savings for each guarantor
        member_account = MemberAccount.objects.get(member=guarantor.guarantor)
        savings = member_account.savings
        guaranteed_amount = Guarantor.objects.filter(
            guarantor=guarantor.guarantor,
            loan__loan_status__in=['active', 'pending']
        ).aggregate(total=Sum('guarantee_amount'))['total'] or 0
        free_savings = savings - guaranteed_amount
        
        # Check if guarantee amount exceeds free savings
        if guarantor.guarantee_amount > free_savings:
            insufficient_guarantors.append({
                'guarantor': guarantor.guarantor,
                'guarantee_amount': guarantor.guarantee_amount,
                'free_savings': free_savings,
            })

    context = {
        'entity': entity,
        'loan': loan,
        'total_value': total_value,
        'required_value': loan.loan_amount,
        'collaterals': collaterals,
        'guarantors': guarantors,
        'is_sufficient': total_value >= loan.loan_amount and not insufficient_guarantors,
        'insufficient_guarantors': insufficient_guarantors,
    }
    
    return render(request, 'loans/collateral_and_guarantor_check.html', context)


@login_required
def release_loan(request, member_id, loan_id):
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    member = get_object_or_404(Member, id=member_id)

    if request.method == 'POST':
        cheque_number = request.POST.get('cheque_number')

        if cheque_number:
            member_account = get_object_or_404(MemberAccount, member=member)

            # Deduct the loan amount from the member's loan balance
            member_account.loan = F('loan') - loan.loan_amount
            member_account.save()

            # Record the transaction
            Transaction.objects.create(
                member_id=member,
                tr_amount=loan.loan_amount,
                tr_type='debit',  # Assuming releasing a loan is a debit transaction
                tr_account='loan',  # Assuming 'loan' is the account type for loans
                account_id=loan.id,
                tr_mode_id=1,  # Default to Mpesa for now
                tr_origin='working_capital',  # Update accordingly
                tr_destn='member account',
                updated_by=request.user.username,
                updated_date=timezone.now()
            )

            # Save the cheque number or any other related info
            loan.cheque_number = cheque_number
            loan.save()

            # Send SMS notification
            phone_number = member.phone_number
            message = f"Dear {member.first_name}, a loan of Ksh {loan.loan_amount} has been released to your account. Your new balance is Ksh {member_account.loan}."
            # Assuming `send_notification` is a function to send SMS notifications
            send_notification(phone_number, message)

            # Redirect to loan summary
            return redirect('loans:loan_summary', loan_id=loan.id, member_id=member.id)

    return render(request, 'loans/release_loan.html', {'loan': loan})


@login_required
def release_loan_entity(request, entity_id, loan_id):
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    entity = get_object_or_404(Entity, id=entity_id)

    if request.method == 'POST':
        cheque_number = request.POST.get('cheque_number')

        if cheque_number:
            entity_account = get_object_or_404(EntityAccount, entity=entity)

            # Deduct the loan amount from the member's loan balance
            entity_account.loan = F('loan') - loan.loan_amount
            entity_account.save()

            # Record the transaction
            EntityAccountsLedger.objects.create(
                entity=entity,
                tr_amount=loan.loan_amount,
                tr_type='debit',  # Assuming releasing a loan is a debit transaction
                tr_account='loan',  # Assuming 'loan' is the account type for loans
                tr_mode_id=1,  # Default to Mpesa for now
                tr_origin='working_capital',  # Update accordingly
                tr_destn='entity account',
                updated_by=request.user
            )

            # Save the cheque number or any other related info
            loan.cheque_number = cheque_number
            loan.save()

            # Send SMS notification
            phone_number = entity.office_phone_number
            message = f"Dear {entity.entity_name}, a loan of Ksh {loan.loan_amount} has been released to your account. Your new balance is Ksh {entity_account.loan}."
            # Assuming `send_notification` is a function to send SMS notifications
            send_notification(phone_number, message)

            # Redirect to loan summary
            return redirect('loans:loan_summary_entity', loan_id=loan.id, entity_id=entity.id)

    return render(request, 'loans/release_loan.html', {'loan': loan, 'entity': entity})



@login_required
def loan_summary(request, member_id, loan_id):
    member = get_object_or_404(Member, id=member_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    collaterals = Collateral.objects.filter(loan=loan)
    guarantors = Guarantor.objects.filter(loan=loan)
    
    context = {
        'loan': loan,
        'collaterals': collaterals,
        'guarantors': guarantors,
    }
    return render(request, 'loans/loan_summary.html', context)
@login_required
def loan_summary_entity(request, entity_id, loan_id):
    entity = get_object_or_404(Entity, id=entity_id)
    loan = get_object_or_404(IssuedLoan, id=loan_id)
    collaterals = Collateral.objects.filter(loan=loan)
    guarantors = Guarantor.objects.filter(loan=loan)
    
    context = {
        'loan': loan,
        'collaterals': collaterals,
        'guarantors': guarantors,
    }
    return render(request, 'loans/loan_summary_entity.html', context)

@login_required
def create_loan_product(request):
    if request.method == 'POST':
        form = LoanProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan product created successfully.')
            return redirect('loans:create_loan_product')
    else:
        form = LoanProductForm()
    return render(request, 'loans/create_loan_product.html', {'form': form})

@login_required
def view_loan_products(request):
    loan_products = LoanProduct.objects.all()
    return render(request, 'loans/view_loan_products.html', {'loan_products': loan_products})
@login_required
def view_issued_loans(request):
    issued_loans = IssuedLoan.objects.all()
    return render(request, 'loans/view_issued_loans.html', {'issued_loans': issued_loans})


@login_required
def delete_guarantor(request, member_id, loan_id, guarantor_id):
    guarantor = get_object_or_404(Guarantor, id=guarantor_id)
    guarantor.delete()
    return redirect('loans:collateral_and_guarantor_check', member_id=member_id, loan_id=loan_id)

@login_required
def delete_collateral(request, member_id, loan_id, collateral_id):
    collateral = get_object_or_404(Collateral, id=collateral_id)
    collateral.delete()
    return redirect('loans:collateral_and_guarantor_check', member_id=member_id, loan_id=loan_id)

@login_required
def delete_guarantor_entity(request, entity_id, loan_id, guarantor_id):
    guarantor = get_object_or_404(Guarantor, id=guarantor_id)
    guarantor.delete()
    return redirect('loans:guarantors_entity', entity_id=entity_id, loan_id=loan_id)

@login_required
def delete_collateral_entity(request, entity_id, loan_id, collateral_id):
    collateral = get_object_or_404(Collateral, id=collateral_id)
    collateral.delete()
    return redirect('loans:collaterals_entity', entity_id=entity_id, loan_id=loan_id)

