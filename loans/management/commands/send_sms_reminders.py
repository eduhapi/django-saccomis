import os
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta
from loans.models import IssuedLoan
from members.models import MemberAccount, Member
from sms.utils import send_notification  # Adjust the import path as necessary

class Command(BaseCommand):
    help = 'Send SMS reminders to members with outstanding loans'

    def handle(self, *args, **kwargs):
        today = datetime.now().date()
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'sms_reminders_{today.strftime("%Y_%m_%d")}.log')

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        try:
            # Fetch members with outstanding loans
            member_accounts = MemberAccount.objects.filter(loan__lt=0)
            for account in member_accounts:
                issued_loans = IssuedLoan.objects.filter(member_id=account.member_id, loan_balance__lt=0)
                member = Member.objects.get(id=account.member_id)
                
                for loan in issued_loans:
                    # Calculate the due date
                    repayment_start_date = loan.repayments_start_date
                    due_date = repayment_start_date

                    # Find the next due date
                    while due_date < today:
                        due_date += relativedelta(months=1)

                    reminder_date = due_date - timedelta(days=3)

                    if today == reminder_date:
                        # Prepare the SMS content
                        phone_number = member.phone_number  # Assume member has a phone_number field
                        message = (
                            f"Reminder: Your loan installment of {loan.installment_amount} is due on {due_date}. "
                            f"Outstanding amount: {abs(account.loan)}. Please make your payment on time."
                        )
                        
                        # Send the SMS
                        success, result = send_notification(phone_number, message)
                        
                        if success:
                            logging.info(f'SMS sent to {phone_number} for loan ID {loan.id}: {message}')
                        else:
                            logging.error(f'Failed to send SMS to {phone_number} for loan ID {loan.id}: {result}')

            logging.info('SMS reminders processed successfully.')

        except Exception as e:
            logging.error(f'Error sending SMS reminders: {str(e)}')
            self.stdout.write(self.style.ERROR(f'Error sending SMS reminders: {str(e)}'))
