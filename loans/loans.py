from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from decimal import Decimal
from .models import Entity, EntityAccount, EntityAccountsLedger, IssuedLoan, SaccoCharge, SaccoAccountsLedger, SaccoAccount
from .forms import IssueLoanForm
from .utils import generate_unique_loan_ref_id
from datetime import timedelta

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

            # Fetch SACCO charges
            loan_interest = SaccoCharge.objects.get(charge_name='loan_interest')
            loan_charge_un_100000 = SaccoCharge.objects.get(charge_name='loan_charge_un_100000')
            loan_charge_ov_100000 = SaccoCharge.objects.get(charge_name='loan_charge_ov_100000')
            loan_boost_charge = SaccoCharge.objects.get(charge_name='loan_boost_charge')
            loan_top_up_charge = SaccoCharge.objects.get(charge_name='loan_top_up_charge')

            # Calculate interest
            interest_rate = loan_interest.charge_value / 100
            months = Decimal(repayment_period)
            numerator = loan_amount * interest_rate * (1 + interest_rate) ** months
            denominator = (1 + interest_rate) ** months - 1
            installment_amount = numerator / denominator

            # Determine processing fee based on loan amount
            if loan_amount < 100000:
                processing_fee = loan_charge_un_100000.charge_value
            else:
                processing_fee = loan_charge_ov_100000.charge_value

            # Calculate loan boost charge if applicable
            six_months_ago = timezone.now() - timedelta(days=180)
            two_months_ago = timezone.now() - timedelta(days=60)

            last_six_months_savings = EntityAccountsLedger.objects.filter(
                entity=entity, tr_account='savings', updated_at__gte=six_months_ago
            ).order_by('-updated_at')[:6]

            last_two_months_savings = EntityAccountsLedger.objects.filter(
                entity=entity, tr_account='savings', updated_at__gte=two_months_ago
            ).order_by('-updated_at')[:2]

            if last_six_months_savings and last_two_months_savings:
                avg_savings_last_6 = sum(tx.tr_amount for tx in last_six_months_savings) / len(last_six_months_savings)
                avg_savings_last_2 = sum(tx.tr_amount for tx in last_two_months_savings) / len(last_two_months_savings)

                if avg_savings_last_2 > avg_savings_last_6 * 1.4:
                    boost_charge = loan_boost_charge.charge_value / 100 * avg_savings_last_2
                    processing_fee += boost_charge

            # Check for existing unsettled loans and apply top-up charge if applicable
            unsettled_loans = IssuedLoan.objects.filter(object_id=entity_id, loan_status='active')
            if unsettled_loans.exists():
                unsettled_loan_balance = unsettled_loans.aggregate(total_balance=Sum('loan_balance'))['total_balance']
                top_up_charge = loan_top_up_charge.charge_value / 100 * unsettled_loan_balance
                processing_fee += top_up_charge

            # Subtract processing fee from loan amount
            net_loan_amount = loan_amount - processing_fee

            # Check loan eligibility
            eligibility_results = check_loan_eligibility_entity(entity, net_loan_amount)

            if eligibility_results['qualified']:
                loan.installment_amount = installment_amount
                loan.loan_ref_id = generate_unique_loan_ref_id()
                loan.processed_by = request.user
                loan.loan_amount = loan_amount
                loan.loan_balance = loan_amount
                loan.save()

                # Record the loan disbursement in the SaccoAccountsLedger and update accounts
                sacco_liability_account = SaccoAccount.objects.get(account_code='4001')
                sacco_income_account = SaccoAccount.objects.get(account_code='2001')

                SaccoAccountsLedger.objects.create(
                    account_id=sacco_liability_account.id,
                    description='Loan disbursement',
                    amount=net_loan_amount,
                    transaction_type='debit',
                    transaction_date=timezone.now(),
                    updated_at=timezone.now(),
                    updated_by_id=request.user.id
                )
                sacco_liability_account.account_balance -= net_loan_amount
                sacco_liability_account.save()

                SaccoAccountsLedger.objects.create(
                    account_id=sacco_income_account.id,
                    description='Processing fee',
                    amount=processing_fee,
                    transaction_type='credit',
                    transaction_date=timezone.now(),
                    updated_at=timezone.now(),
                    updated_by_id=request.user.id
                )
                sacco_income_account.account_balance += processing_fee
                sacco_income_account.save()

                # Record the loan transaction in EntityAccountsLedger
                EntityAccountsLedger.objects.create(
                    entity=entity,
                    tr_amount=loan_amount,
                    updated_at=timezone.now(),
                    entity_id=entity.id,
                    updated_by_id=request.user.id,
                    external_ref_code=loan.loan_ref_id,
                    sacco_ref_code=sacco_liability_account.account_code,
                    tr_account='loan',
                    tr_destn='entity_loan',
                    tr_mode_id=1,  # Default to Mpesa for now
                    tr_origin='loan_disbursement',
                    tr_type='debit'
                )

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
