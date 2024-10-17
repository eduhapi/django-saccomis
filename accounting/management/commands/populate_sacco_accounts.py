from django.core.management.base import BaseCommand
from accounting.models import SaccoAccount

class Command(BaseCommand):
    help = 'Populate initial SACCO accounts structure'

    def handle(self, *args, **kwargs):
        accounts = [
            # Income Accounts
            {'account_code': '110010', 'account_name': 'Mobile Loan Interest', 'account_type': 'INCOME'},
            {'account_code': '110011', 'account_name': 'Development Loan Interest', 'account_type': 'INCOME'},
            {'account_code': '110012', 'account_name': 'School fees Loan Interest', 'account_type': 'INCOME'},
            {'account_code': '110013', 'account_name': 'Instant Loan Interest', 'account_type': 'INCOME'},
            {'account_code': '111000', 'account_name': 'Loan Topup Charges', 'account_type': 'INCOME'},
            {'account_code': '111001', 'account_name': 'Loan Apraisal Fee', 'account_type': 'INCOME'},
            {'account_code': '122000', 'account_name': 'Mpesa Commission', 'account_type': 'INCOME'},
            {'account_code': '123000', 'account_name': 'Lump sum Deposit', 'account_type': 'INCOME'},
            {'account_code': '124000', 'account_name': 'Registration/Membership Fee', 'account_type': 'INCOME'},
            {'account_code': '124002', 'account_name': 'Transaction Charge', 'account_type': 'INCOME'},
            {'account_code': '124003', 'account_name': 'Transaction Charge Mobile', 'account_type': 'INCOME'},
            {'account_code': '124004', 'account_name': 'Penalty', 'account_type': 'INCOME'},
            {'account_code': '124005', 'account_name': 'Legal fee', 'account_type': 'INCOME'},
            {'account_code': '124006', 'account_name': 'Other Income', 'account_type': 'INCOME'},

            # Expenditure Accounts
            {'account_code': '301000', 'account_name': 'Interest Expense On Deposit', 'account_type': 'EXPENDITURE'},
            {'account_code': '303000', 'account_name': 'Dividend Expenses On Share', 'account_type': 'EXPENDITURE'},
            {'account_code': '306001', 'account_name': 'Other Expenses', 'account_type': 'EXPENDITURE'},
            {'account_code': '309000', 'account_name': 'Salaries & Wages', 'account_type': 'EXPENDITURE'},
            {'account_code': '309001', 'account_name': 'Nssf', 'account_type': 'EXPENDITURE'},
            {'account_code': '309002', 'account_name': 'Shif', 'account_type': 'EXPENDITURE'},
            {'account_code': '309003', 'account_name': 'Allowances', 'account_type': 'EXPENDITURE'},
            {'account_code': '310003', 'account_name': 'Ushirika Day', 'account_type': 'EXPENDITURE'},
            {'account_code': '310004', 'account_name': 'Agm & Sgm', 'account_type': 'EXPENDITURE'},
            {'account_code': '310005', 'account_name': 'Public Relations', 'account_type': 'EXPENDITURE'},
            {'account_code': '310006', 'account_name': 'Board Travell/subsistense', 'account_type': 'EXPENDITURE'},
            {'account_code': '311001', 'account_name': 'Marketing Expenses', 'account_type': 'EXPENDITURE'},
            {'account_code': '312000', 'account_name': 'Depn Expense-comp & Peripherals', 'account_type': 'EXPENDITURE'},
            {'account_code': '312001', 'account_name': 'Depn Expense-software', 'account_type': 'EXPENDITURE'},
            {'account_code': '313001', 'account_name': 'Airtime', 'account_type': 'EXPENDITURE'},
            {'account_code': '313002', 'account_name': 'Consultancy', 'account_type': 'EXPENDITURE'},
            {'account_code': '313003', 'account_name': 'Print And Stationery', 'account_type': 'EXPENDITURE'},
            {'account_code': '313004', 'account_name': 'Office Expenses', 'account_type': 'EXPENDITURE'},
            {'account_code': '313005', 'account_name': 'Bookkeeping Fees', 'account_type': 'EXPENDITURE'},
            {'account_code': '313006', 'account_name': 'Refreshments', 'account_type': 'EXPENDITURE'},

            # Fixed Assets Accounts
            {'account_code': '501000', 'account_name': 'Furniture & Fittings', 'account_type': 'ASSETS'},
            {'account_code': '501001', 'account_name': 'Computer & accessories', 'account_type': 'ASSETS'},
            {'account_code': '501002', 'account_name': 'Office Container', 'account_type': 'ASSETS'},
            {'account_code': '501003', 'account_name': 'Office Equipments', 'account_type': 'ASSETS'},
            {'account_code': '501004', 'account_name': 'Office Phone', 'account_type': 'ASSETS'},
            {'account_code': '501005', 'account_name': 'TV Set', 'account_type': 'ASSETS'},
            {'account_code': '501006', 'account_name': 'Loose Tools', 'account_type': 'ASSETS'},
            {'account_code': '503000', 'account_name': 'Software', 'account_type': 'ASSETS'},
            {'account_code': '502000', 'account_name': 'Prepaid Rent Deposit', 'account_type': 'ASSETS'},

            # Current Assets Accounts
            {'account_code': '600000', 'account_name': 'Cash A/c', 'account_type': 'ASSETS'},
            {'account_code': '660000', 'account_name': "Thro' , contra Ctrl A/c", 'account_type': 'ASSETS'},
            {'account_code': '601000', 'account_name': 'Equity Bank Current A/c', 'account_type': 'ASSETS'},
            {'account_code': '601001', 'account_name': 'Bank 2', 'account_type': 'ASSETS'},
            {'account_code': '623000', 'account_name': 'CIC Money Market', 'account_type': 'ASSETS'},
            {'account_code': '601002', 'account_name': 'Paybill-XXXXXX', 'account_type': 'ASSETS'},
            {'account_code': '601003', 'account_name': 'Bulk Payment-XXXXXXX', 'account_type': 'ASSETS'},
            {'account_code': '610000', 'account_name': 'Interest Receivable', 'account_type': 'ASSETS'},
            {'account_code': '610001', 'account_name': 'Interest Control', 'account_type': 'ASSETS'},
            {'account_code': '610002', 'account_name': 'Loans Recoverable', 'account_type': 'ASSETS'},

            # Current Liabilities Accounts
            {'account_code': '700000', 'account_name': 'Member Deposits', 'account_type': 'LIABILITIES'},
            {'account_code': '701000', 'account_name': 'Unpaid Dividends', 'account_type': 'LIABILITIES'},

            # Long-term Liabilities Accounts
            {'account_code': '800000', 'account_name': 'Share Capital', 'account_type': 'LIABILITIES'},
        ]

        for account in accounts:
            SaccoAccount.objects.get_or_create(**account)

        self.stdout.write(self.style.SUCCESS('Successfully populated initial SACCO accounts structure'))
