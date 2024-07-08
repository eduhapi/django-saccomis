# groups/utils.py

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from openpyxl import Workbook
from datetime import datetime
def generate_pdf_report(context, template_path):
    template = get_template(template_path)
    html = template.render(context)  # Render template with context data

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        # If PDF generation is successful, return HttpResponse with PDF content
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Entity_Statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    # If there's an error in PDF generation, handle appropriately (e.g., log or return None)
    # For debugging, you might want to print pdf.err for error details
    return None

def generate_excel_report(transactions, filename_prefix):
    output = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Entity Statement"

    # Define column headers
    headers = ['Date', 'Particulars', 'Amount']
    sheet.append(headers)

    # Append transaction data
    for transaction in transactions:
        row = [
            transaction.updated_at.strftime('%d/%m/%Y %H:%M:%S'),
            transaction.tr_account,
            f"{transaction.tr_amount}{' Dr' if transaction.tr_type == 1 else ' Cr'}"
        ]
        sheet.append(row)

    workbook.save(output)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
