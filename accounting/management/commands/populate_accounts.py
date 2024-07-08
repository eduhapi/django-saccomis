from django.core.management.base import BaseCommand
from accounting.models import SaccoAccount

class Command(BaseCommand):
    help = 'Populate initial accounts structure'

    def handle(self, *args, **kwargs):
        accounts = [
            {'account_code': '1000', 'account_name': 'ASSETS', 'account_type': 'ASSETS'},
            {'account_code': '1001', 'account_name': 'ASSETS:DEPOSITS', 'account_type': 'ASSETS'},
            {'account_code': '2000', 'account_name': 'INCOME', 'account_type': 'INCOME'},
            {'account_code': '2001', 'account_name': 'INCOME:FINES_FEES_PENALTIES', 'account_type': 'INCOME'},
            {'account_code': '2002', 'account_name': 'INCOME:LOAN_INTEREST', 'account_type': 'INCOME'},
            {'account_code': '3000', 'account_name': 'EXPENDITURE', 'account_type': 'EXPENDITURE'},
            {'account_code': '3001', 'account_name': 'EXPENDITURE:ADMINISTRATION_EXPENDITURE', 'account_type': 'EXPENDITURE'},
            {'account_code': '3002', 'account_name': 'EXPENDITURE:OFFICE_EXPENDITURE', 'account_type': 'EXPENDITURE'},
            {'account_code': '4000', 'account_name': 'WORKING_CAPITAL', 'account_type': 'WORKING_CAPITAL'},
        ]

        for account in accounts:
            SaccoAccount.objects.get_or_create(**account)

        self.stdout.write(self.style.SUCCESS('Successfully populated initial accounts structure'))
