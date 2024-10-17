# groups/urls.py

from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('register/', views.register_entity_step_1, name='register_entity'),
    path('register/step2/<str:entity_id>/', views.register_entity_step_2, name='register_entity_step_2'),
    path('register/step3/<str:entity_id>/', views.register_entity_step_3, name='register_entity_step_3'),
    path('register/done/<str:entity_id>/', views.register_entity_done, name='register_entity_done'),
    path('register/<str:entity_id>/delete_official/<int:official_id>/', views.delete_official, name='delete_official'),
    path('search/', views.search_entity, name='search_entity'),
    path('updated_entity_details/<str:entity_id>/', views.updated_entity_details, name='entity_details'),
    path('select_action/<str:entity_id>', views.select_action, name='select_action'),
    path('update_entity_accounts/<str:entity_id>/', views.update_entity_accounts, name='update_entity_accounts'),
    path('deposit/<str:entity_id>/', views.deposit, name='deposit'),
    path('withdraw/<str:entity_id>/', views.withdraw, name='withdraw'),
    path('transfer/<str:entity_id>/', views.transfer, name='transfer'),
    path('loan-repayment/<str:entity_id>/', views.loan_repayment, name='loan_repayment'),
    path('entity-statement-form/', views.entity_statement_form, name='entity_statement_form'),
    path('entity-statement/', views.entity_statement, name='entity_statement'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('download-excel/', views.download_excel, name='download_excel'),
    path('view_groups/',views.view_groups, name='view_groups'),
    path('entity_profile/<str:entity_id>/', views.entity_profile, name='entity_profile'),

]
