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

@csrf_exempt
def process_payment_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            trans_amount = data.get('TransAmount')
            if trans_amount is None:
                return JsonResponse({"ResultCode": "C2B00013", "ResultDesc": "Invalid Amount"}, status=400)
            
            try:
                trans_amount = Decimal(trans_amount)
            except InvalidOperation:
                return JsonResponse({"ResultCode": "C2B00013", "ResultDesc": "Invalid Amount"}, status=400)

            transaction_type = data.get('TransactionType')
            trans_id = data.get('TransID')
            trans_time = parse_datetime(data.get('TransTime'))
            bill_ref_number = data.get('BillRefNumber')
            msisdn = data.get('MSISDN')

            if '/' not in bill_ref_number:
                return JsonResponse({"ResultCode": "C2B00012", "ResultDesc": "Invalid Account Number"})

            trans_type, account_ref = bill_ref_number.split('/')
            try:
                if account_ref.isdigit():
                    # It's a member
                    account_holder = Member.objects.get(id=account_ref)
                else:
                    # It's an entity
                    account_holder = Entity.objects.get(id=account_ref)

                if trans_type.lower() == 'loan':
                    process_loan_payment(account_holder, trans_amount)
                elif trans_type.lower() == 'savings':
                    process_savings_deposit(account_holder, trans_amount)
                else:
                    raise ValueError("Invalid transaction type")

                return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})
        
            except (Member.DoesNotExist, Entity.DoesNotExist):
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
            return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Other Error"})

def process_loan_payment(account_holder, amount):
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
                record_transaction(account_holder, loan_repayment_amount, 'loan_repayment', 'loan')
            
            if savings_amount > 0:
                account.savings += savings_amount
                account.save()
                record_transaction(account_holder, savings_amount, 'credit', 'savings')
        else:
            account.savings += amount
            account.save()
            record_transaction(account_holder, amount, 'credit', 'savings')
    except Exception as e:
        raise e

def process_savings_deposit(account_holder, amount):
    try:
        if isinstance(account_holder, Member):
            account = MemberAccount.objects.get(member=account_holder)
        else:
            account = EntityAccount.objects.get(entity=account_holder)
        
        account.savings += amount
        account.save()
        record_transaction(account_holder, amount, 'credit', 'savings')
    except Exception as e:
        raise e

def record_transaction(account_holder, amount, tr_type, tr_account):
    if isinstance(account_holder, Member):
        MemberAccountsLedger.objects.create(
            member_id=account_holder,
            tr_amount=amount,
            tr_type=tr_type,
            tr_account=tr_account,
            tr_mode_id=1,  # Assuming 1 for Mpesa
            tr_origin='mpesa',
            tr_destn='member account',
            external_ref_code=get_unique_external_ref_code(trans_id, MemberAccountsLedger),
        )
    else:
        EntityAccountsLedger.objects.create(
            entity=account_holder,
            tr_amount=amount,
            tr_type=tr_type,
            tr_account=tr_account,
            tr_mode_id=1,  # Assuming 1 for Mpesa
            tr_origin='mpesa',
            tr_destn='entity account',
            external_ref_code=get_unique_external_ref_code(trans_id, EntityAccountsLedger),
        )



