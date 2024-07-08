from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
   
    path('loan_balances/', views.loan_balances, name='loan_balances'),
    path('loan_defaulters/', views.loan_defaulters, name='loan_defaulters'),
    path('reports/member_statement/', views.member_statement, name='member_statement'),
    path('reports/member_statement_form/', views.member_statement_form, name='member_statement_form'),
    path('member_details/<int:member_id>/', views.member_details, name='member_details'),
]
