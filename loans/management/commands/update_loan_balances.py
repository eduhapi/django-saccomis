import os
import logging
from decimal import Decimal
from django.core.management.base import BaseCommand
from datetime import datetime
from loans.models import IssuedLoan
from members.models import MemberAccount

class Command(BaseCommand):
    help = 'Update loan balances with 1% interest on the 23rd day of each month'

    def handle(self, *args, **kwargs):
        today = datetime.now()
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'update_loans_{today.strftime("%Y_%m_%d")}.log')

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        if today.day == 22:
            try:
                interest_rate = Decimal('1.01')

                # Update MemberAccount loan balances for accounts with negative loan balances
                member_accounts = MemberAccount.objects.filter(loan__lt=0)
                for account in member_accounts:
                    new_loan_balance = account.loan * interest_rate  # Applying 1% interest
                    account.loan = new_loan_balance
                    account.save()
                    logging.info(f'Updated MemberAccount ID {account.id}: New Loan Balance = {new_loan_balance}')

                # Update IssuedLoan balances for loans with negative balances
                issued_loans = IssuedLoan.objects.filter(loan_balance__lt=0)
                for loan in issued_loans:
                    new_loan_balance = loan.loan_balance * interest_rate  # Applying 1% interest
                    loan.loan_balance = new_loan_balance
                    loan.save()
                    logging.info(f'Updated IssuedLoan ID {loan.id}: New Loan Balance = {new_loan_balance}')

                logging.info('Loan balances updated successfully.')

            except Exception as e:
                logging.error(f'Error updating loan balances: {str(e)}')
                self.stdout.write(self.style.ERROR(f'Error updating loan balances: {str(e)}'))
        else:
            logging.warning('Today is not the 23rd day of the month. No updates performed.')
            self.stdout.write(self.style.WARNING('Today is not the 23rd day of the month. No updates performed.'))
