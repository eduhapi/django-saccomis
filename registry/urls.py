# registry/urls.py
from django.urls import path
from . import views 
app_name = 'registry'
urlpatterns = [
    path('download-member-template/', views.download_member_excel_template, name='download_member_excel_template'),
    path('upload-bulk-members/', views.upload_bulk_members, name='upload_bulk_members'),
    path('download-member-account-template/',views.download_member_account_excel_template, name='download_member_account_excel_template'),
    path('upload-bulk-member-accounts/', views.upload_bulk_member_accounts, name='upload_bulk_member_accounts'),
    path('download-next-of-kin-template/', views.download_next_of_kin_excel_template, name='download_next_of_kin_excel_template'),
    path('upload-bulk-next-of-kin/', views.upload_bulk_next_of_kin, name='upload_bulk_next_of_kin'),
]
