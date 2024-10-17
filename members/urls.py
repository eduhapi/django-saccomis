from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .register_member_views import MemberRegistrationWizard
from .dashboard_views import dashboard
from . member_views import view_members,view_transactions,mini_statement_view, mini_statement_form,member_profile
from . import update_member_accounts_views
from  .update_member_accounts_views import search_member
from .import views


app_name = 'members'

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/', permanent=False)),  # Redirect root to dashboard
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('view_members/', view_members, name='view_members'),
    path('transactions/', view_transactions, name='transactions'),
    path('mini_statement/', mini_statement_view, name='mini_statement'),
    path('mini_statement_form/', mini_statement_view, name='mini_statement_form'),  # Add this line
    path('search_member/', search_member, name='search_member'),
    path('register_member/', MemberRegistrationWizard.as_view(), name='register_member'),
    path('update_member_accounts/<int:member_id>/', update_member_accounts_views.update_member_accounts, name='update_member_accounts'),
    path('member_details/<int:member_id>/', update_member_accounts_views.member_details, name='member_details'),
    path('select_action/<int:member_id>/', update_member_accounts_views.select_action, name='select_action'),
    path('deposit/<int:member_id>/', update_member_accounts_views.deposit, name='deposit'),
    path('loan-repayment/<int:member_id>/', update_member_accounts_views.loan_repayment, name='loan_repayment'),
    path('withdraw/<int:member_id>/', update_member_accounts_views.withdrawal, name='withdraw'),
    path('transfer/<int:member_id>/', update_member_accounts_views.transfer, name='transfer'),
    path('member_profile/<int:member_id>/', member_profile, name='member_profile'),
    #more urls
    path('edit/', views.search_member_to_edit, name='search_member_1'),
    path('statement/', views.mini_statement_form, name='mini_statement_form'),
    path('report/savings', views.savings_report, name='savings_report'),
    path('report/loans/', views.loans_report, name='loans_report'),
    path('report/share-capital/', views.share_capital_report, name='share_capital_report'),
    path('report/all-accounts/', views.all_accounts_report, name='all_accounts_report'),
    path('edit/personal/<int:member_id>/', views.edit_personal_details, name='edit_personal_details'),
    path('edit/personal', views.edit_personal_details, name='edit_personal_details'),
    path('edit/next-of-kin/', views.edit_next_of_kin, name='edit_next_of_kin'),
    path('edit/register/', views.register_member, name='register_member'),
    path('deactivate/', views.deactivate_member, name='deactivate_member'),
    path('statistics/membership/', views.membership_stats, name='membership_stats'),
    path('statistics/accounts/', views.accounts_stats, name='accounts_stats'),
    path('statistics/joining/', views.member_joining_stats, name='member_joining_stats'),
    path('statistics/dormant/', views.dormant_members, name='dormant_members'),
    path('statistics/deceased/', views.deceased_members, name='deceased_members'),
    path('statistics/top-savers/', views.top_savers, name='top_savers'),
    path('statistics/top-borrowers/', views.top_borrowers, name='top_borrowers'),
    path('statistics/next-of-kin/', views.non_member_next_of_kins, name='non_member_next_of_kins'),
]
