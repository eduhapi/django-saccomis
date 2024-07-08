from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlwt

def generate_pdf_report(context, template_path):
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="loan_balances.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with code %s' % pisa_status.err)
    return response

def generate_excel_report(loan_balances, filename):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Loan Balances')

    # Header
    row_num = 0
    columns = [
        'ID', 'Name', 'Phone', 'Principal', 'Installment', 'Last Repayment Date',
        'Remaining Repayment Period', 'Current Loan Balance', 'Arrears Amount', 'Arrears Period', 'Type'
    ]

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, xlwt.easyxf(strg_to_parse='font: bold on;'))

    # Data
    for loan_balance in loan_balances:
        row_num += 1
        ws.write(row_num, 0, loan_balance['id'])
        ws.write(row_num, 1, loan_balance['name'])
        ws.write(row_num, 2, loan_balance['phone'])
        ws.write(row_num, 3, float(loan_balance['principal']))
        ws.write(row_num, 4, float(loan_balance['installment']))
        ws.write(row_num, 5, loan_balance['last_repayment_date'].strftime("%d/%m/%Y"))
        ws.write(row_num, 6, loan_balance['remaining_repayment_period'])
        ws.write(row_num, 7, float(loan_balance['current_loan_balance']))
        ws.write(row_num, 8, float(loan_balance['arrears_amount']))
        ws.write(row_num, 9, loan_balance['arrears_period'])
        ws.write(row_num, 10, loan_balance['type'])

    wb.save(response)
    return response
