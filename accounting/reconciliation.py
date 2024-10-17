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

            if '/' not in bill_ref_number:
                logger.error("BillRefNumber does not contain '/'")
                return JsonResponse({"ResultCode": "C2B00012", "ResultDesc": "Invalid Account Number"}, status=400)

            try:
                trans_time = datetime.strptime(trans_time, "%Y%m%d%H%M%S")
            except ValueError:
                logger.error("Invalid transaction time format")
                return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Invalid Transaction Time"}, status=400)

            trans_type, account_ref = bill_ref_number.split('/')
            try:
                if account_ref.isdigit():
                    # It's a member
                    account_holder = Member.objects.get(id=account_ref)
                else:
                    # It's an entity
                    account_holder = Entity.objects.get(id=account_ref)

                if trans_type.lower() == 'loan':
                    process_loan_payment(account_holder, trans_amount, trans_id)
                elif trans_type.lower() == 'savings':
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
                record_transaction(account_holder, savings_amount, trans_id, 'savings')
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
                member=account_holder,
                tr_amount=amount,
                tr_type='credit',
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
