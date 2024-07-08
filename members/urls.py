from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .register_member_views import MemberRegistrationWizard
from .dashboard_views import dashboard
from . member_views import view_members,view_transactions,mini_statement_view, mini_statement_form,member_profile
from . import update_member_accounts_views
from  .update_member_accounts_views import search_member


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
    path('withdraw/<int:member_id>/', update_member_accounts_views.withdrawal, name='withdraw'),
    path('transfer/<int:member_id>/', update_member_accounts_views.transfer, name='transfer'),
    path('member_profile/<int:member_id>/', member_profile, name='member_profile'),
]
