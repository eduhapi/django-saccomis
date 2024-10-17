from django.urls import path
from . import views  # Assuming your views are imported from the current directory

app_name = 'accounting'

urlpatterns = [
    path('add_expenditure/', views.add_expenditure, name='add_expenditure'),
    path('add_asset/', views.add_asset, name='add_asset'),
    path('add_account/', views.add_account, name='add_account'),
    path('chart_of_accounts/', views.view_chart_of_accounts, name='chart_of_accounts'),
    path('reports/', views.generate_reports, name='generate_reports'),
    path('account_statement/<int:account_id>/', views.account_statement, name='account_statement'),
    path('add_sacco_charge/', views.add_sacco_charge, name='add_sacco_charge'),
    path('update_sacco_charge/<int:pk>/', views.update_sacco_charge, name='update_sacco_charge'),
    path('list_sacco_charges/', views.list_sacco_charges, name='list_sacco_charges'),
    path('mpesa_reconciliation_upload/', views.mpesa_reconciliation_upload, name='mpesa_reconciliation_upload'),
    path('filter_and_format_excel/', views.filter_and_format_excel, name='filter_and_format_excel'),
    path('download/<path:filename>/', views.download_filtered_statement, name='download_filtered_statement'),
    path('reconciliation-records/', views.view_reconciliation_records, name='view_reconciliation_records'),
    path('process_payment_notification/', views.process_payment_notification, name='process_payment_notification'),
    path('daily-accounts-posting/', views.daily_accounts_posting, name='daily_accounts_posting'),
]

