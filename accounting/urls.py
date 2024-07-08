
from django.urls import path
from .import views 
app_name = 'accounting'
urlpatterns = [
    path('add_expenditure/',views. add_expenditure, name='add_expenditure'),
    path('add_asset/', views.add_asset, name='add_asset'),
    path('add_account/', views.add_account, name='add_account'),
    path('chart_of_accounts/', views.view_chart_of_accounts, name='chart_of_accounts'),
    path('reports/', views.generate_reports, name='generate_reports'),
    path('account_statement/<int:account_id>/', views.account_statement, name='account_statement'),
    path('add_sacco_charge/', views.add_sacco_charge, name='add_sacco_charge'),
    path('update_sacco_charge/<int:pk>/', views.update_sacco_charge, name='update_sacco_charge'),
    path('list_sacco_charges/', views.list_sacco_charges, name='list_sacco_charges'),
]
