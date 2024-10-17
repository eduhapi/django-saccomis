from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
   
    path('loan_balances/', views.loan_balances, name='loan_balances'),
    path('loan_defaulters/', views.loan_defaulters, name='loan_defaulters'),
    path('reports/member_statement/', views.member_statement, name='member_statement'),
    path('reports/member_statement_form/', views.member_statement_form, name='member_statement_form'),
    path('member_details/<int:member_id>/', views.member_details, name='member_details'),
    path('account-statement/', views.account_statement_form, name='account_statement_form'),
    path('account-statement/fetch/', views.account_statement, name='account_statement'),
    path('reports/member-trial-balance/', views.member_trial_balance, name='member_trial_balance'),
    path('reports/entity-trial-balance/', views.entity_trial_balance, name='entity_trial_balance'),
    path('reports/sacco-trial-balance/', views.sacco_trial_balance, name='sacco_trial_balance'),
    path('reports/member-cumulative-balance/', views.member_cumulative_balance, name='member_cumulative_balance'),
    path('reports/entity-cumulative-balance/', views.entity_cumulative_balance, name='entity_cumulative_balance'),
    path('reports/sacco-cumulative-balance/', views.sacco_cumulative_balance, name='sacco_cumulative_balance'),
]
