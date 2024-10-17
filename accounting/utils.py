from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from members.models import Member, MemberAccount, MemberAccountsLedger
from loans.models import IssuedLoan
from groups.models import Entity, EntityAccount, EntityAccountsLedger

def get_unique_external_ref_code(base_code, model):
    """
    Generate a unique external_ref_code by appending a counter.
    """
    counter = 1
    unique_code = base_code
    while model.objects.filter(external_ref_code=unique_code).exists():
        unique_code = f"{base_code}_{counter}"
        counter += 1
    return unique_code

def process_reconciliation_entries(entries):
    for entry in entries:
        # Ensure paid_in has a value
        if not entry.paid_in:
            continue

        try:
            # Convert paid_in to decimal
            entry.paid_in = Decimal(entry.paid_in)
        except (InvalidOperation, ValueError):
            entry.reconciled = False
            entry.save()
            continue

        account_no = str(entry.account_no)  # Convert account_no to string
        if account_no.isdigit():
            try:
                # Handle member account reconciliation
                member = Member.objects.get(id=account_no)
                account = MemberAccount.objects.get(member=member)
                active_loan = IssuedLoan.objects.filter(object_id=member.id, loan_status='active').first()

                if entry.priority == 'savings_first':
                    if active_loan:
                        min_savings_amount = Decimal(1000)
                        savings_amount = min(entry.paid_in, min_savings_amount)
                        loan_repayment_amount = entry.paid_in - savings_amount

                        account.savings += savings_amount
                        account.save()

                        if loan_repayment_amount > 0:
                            active_loan.loan_balance -= loan_repayment_amount
                            active_loan.save()

                            MemberAccountsLedger.objects.create(
                                member_id=member,
                                tr_amount=loan_repayment_amount,
                                tr_type='loan_repayment',
                                tr_account='loan',
                                account_id=active_loan.id,
                                tr_mode_id=1,  # Assuming 1 for Mpesa
                                tr_origin='mpesa',
                                tr_destn='member account',
                                external_ref_code=get_unique_external_ref_code(entry.receipt_no, MemberAccountsLedger),
                            )
                    else:
                        account.savings += entry.paid_in
                        account.save()

                    MemberAccountsLedger.objects.create(
                        member_id=member,
                        tr_amount=entry.paid_in,
                        tr_type='credit',
                        tr_account='savings',
                        account_id=account.id,
                        tr_mode_id=1,  # Assuming 1 for Mpesa
                        tr_origin='mpesa',
                        tr_destn='member account',
                        external_ref_code=get_unique_external_ref_code(entry.receipt_no, MemberAccountsLedger),
                    )

                elif entry.priority == 'loan_repayment_first':
                    if active_loan:
                        installment_amount = active_loan.installment_amount
                        loan_repayment_amount = min(entry.paid_in, installment_amount)
                        savings_amount = entry.paid_in - loan_repayment_amount

                        active_loan.loan_balance -= loan_repayment_amount
                        active_loan.save()

                        if savings_amount > 0:
                            account.savings += savings_amount
                            account.save()

                            MemberAccountsLedger.objects.create(
                                member_id=member,
                                tr_amount=savings_amount,
                                tr_type='credit',
                                tr_account='savings',
                                account_id=account.id,
                                tr_mode_id=1,  # Assuming 1 for Mpesa
                                tr_origin='mpesa',
                                tr_destn='member account',
                                external_ref_code=get_unique_external_ref_code(entry.receipt_no, MemberAccountsLedger),
                            )

                        MemberAccountsLedger.objects.create(
                            member_id=member,
                            tr_amount=loan_repayment_amount,
                            tr_type='loan_repayment',
                            tr_account='loan',
                            account_id=active_loan.id,
                            tr_mode_id=1,  # Assuming 1 for Mpesa
                            tr_origin='mpesa',
                            tr_destn='member account',
                            external_ref_code=get_unique_external_ref_code(entry.receipt_no, MemberAccountsLedger),
                        )
                    else:
                        account.savings += entry.paid_in
                        account.save()

                        MemberAccountsLedger.objects.create(
                            member_id=member,
                            tr_amount=entry.paid_in,
                            tr_type='credit',
                            tr_account='savings',
                            account_id=account.id,
                            tr_mode_id=1,  # Assuming 1 for Mpesa
                            tr_origin='mpesa',
                            tr_destn='member account',
                            external_ref_code=get_unique_external_ref_code(entry.receipt_no, MemberAccountsLedger),
                        )

                entry.reconciled = True
                entry.reconciled_at = datetime.now()
                entry.save()

            except Member.DoesNotExist:
                entry.reconciled = False
                entry.save()

        else:
            try:
                entity = Entity.objects.get(id=account_no)
                entity_account = EntityAccount.objects.get(entity=entity)
                active_loan = IssuedLoan.objects.filter(object_id=entity.id, loan_status='active').first()

                if entry.priority == 'savings_first':
                    if active_loan:
                        min_savings_amount = Decimal(1000)
                        savings_amount = min(entry.paid_in, min_savings_amount)
                        loan_repayment_amount = entry.paid_in - savings_amount

                        entity_account.savings += savings_amount
                        entity_account.save()

                        if loan_repayment_amount > 0:
                            active_loan.loan_balance -= loan_repayment_amount
                            active_loan.save()

                            EntityAccountsLedger.objects.create(
                                entity=entity,
                                tr_amount=loan_repayment_amount,
                                tr_type='loan_repayment',
                                tr_account='loan',
                                tr_mode_id=1,  # Assuming 1 for Mpesa
                                tr_origin='mpesa',
                                tr_destn='entity account',
                                external_ref_code=get_unique_external_ref_code(entry.receipt_no, EntityAccountsLedger),
                            )
                    else:
                        entity_account.savings += entry.paid_in
                        entity_account.save()

                    EntityAccountsLedger.objects.create(
                        entity=entity,
                        tr_amount=entry.paid_in,
                        tr_type='credit',
                        tr_account='savings',
                        tr_mode_id=1,  # Assuming 1 for Mpesa
                        tr_origin='mpesa',
                        tr_destn='entity account',
                        external_ref_code=get_unique_external_ref_code(entry.receipt_no, EntityAccountsLedger),
                    )

                elif entry.priority == 'loan_repayment_first':
                    if active_loan:
                        installment_amount = active_loan.installment_amount
                        loan_repayment_amount = min(entry.paid_in, installment_amount)
                        savings_amount = entry.paid_in - loan_repayment_amount

                        active_loan.loan_balance -= loan_repayment_amount
                        active_loan.save()

                        if savings_amount > 0:
                            entity_account.savings += savings_amount
                            entity_account.save()

                            EntityAccountsLedger.objects.create(
                                entity=entity,
                                tr_amount=savings_amount,
                                tr_type='credit',
                                tr_account='savings',
                                tr_mode_id=1,  # Assuming 1 for Mpesa
                                tr_origin='mpesa',
                                tr_destn='entity account',
                                external_ref_code=get_unique_external_ref_code(entry.receipt_no, EntityAccountsLedger),
                            )

                        EntityAccountsLedger.objects.create(
                            entity=entity,
                            tr_amount=loan_repayment_amount,
                            tr_type='loan_repayment',
                            tr_account='loan',
                            tr_mode_id=1,  # Assuming 1 for Mpesa
                            tr_origin='mpesa',
                            tr_destn='entity account',
                            external_ref_code=get_unique_external_ref_code(entry.receipt_no, EntityAccountsLedger),
                        )
                    else:
                        entity_account.savings += entry.paid_in
                        entity_account.save()

                        EntityAccountsLedger.objects.create(
                            entity=entity,
                            tr_amount=entry.paid_in,
                            tr_type='credit',
                            tr_account='savings',
                            tr_mode_id=1,  # Assuming 1 for Mpesa
                            tr_origin='mpesa',
                            tr_destn='entity account',
                            external_ref_code=get_unique_external_ref_code(entry.receipt_no, EntityAccountsLedger),
                        )

                entry.reconciled = True
                entry.reconciled_at = datetime.now()
                entry.save()

            except Entity.DoesNotExist:
                entry.reconciled = False
                entry.save()
import uuid
import base64

def generate_unique_ref_id():
    # Generate UUID and encode it to base64
    unique_id = uuid.uuid4().hex[:10]
   # encoded_id = base64.b64encode(unique_id).decode('utf-8')

    # Remove non-alphanumeric characters and truncate to desired length
    #clean_id = ''.join(char for char in encoded_id if char.isalnum())[:15]

    return unique_id

# utils.py
from django.http import HttpResponse
import pdfkit
import pandas as pd
from django.template.loader import render_to_string

def generate_pdf_report(context, template_path):
    html_string = render_to_string(template_path, context)
    pdf = pdfkit.from_string(html_string, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report.pdf"'
    return response

def generate_excel_report(transactions, filename):
    data = [{
        'Date': txn.updated_at,
        'Account': txn.tr_account,
        'Amount': txn.tr_amount,
        'Type': txn.tr_type,
        'Mode': txn.get_tr_mode_id_display(),
        'Origin': txn.tr_origin,
        'Destination': txn.tr_destn
    } for txn in transactions]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    df.to_excel(response, index=False)
    return response

