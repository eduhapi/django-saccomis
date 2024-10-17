from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('create-loan-product/', views.create_loan_product, name='create_loan_product'),
    path('search-member/', views.search_member_or_entity, name='search_member'),
    path('search-member/', views.search_member_or_entity, name='search_member_or_entity'),
    path('member-details/<int:member_id>/', views.member_details, name='member_details'),
    path('entity-details/<str:entity_id>/', views.entity_details, name='entity_details'),
    path('start-application/member/<int:member_id>/', views.start_application_member, name='start_application_member'),
    path('start-application/entity/<str:entity_id>/', views.start_application_entity, name='start_application_entity'),
    #path('loan-eligibility/<int:member_id>/', views.loan_eligibility, name='loan_eligibility'),
    path('start-application/member/<int:member_id>/', views.loan_eligibility_member, name='loan_eligibility_member'),
    path('start-application/entity/<str:entity_id>/', views.loan_eligibility_entity, name='loan_eligibility_entity'),
    path('loan-details/<int:member_id>/', views.loan_details_member, name='loan_details_member'),
    path('loan-details/<str:entity_id>/', views.loan_details_entity, name='loan_details_entity'),
    path('collaterals/<int:member_id>/<int:loan_id>/', views.collaterals, name='collaterals'),
    path('collaterals-entity/<str:entity_id>/<int:loan_id>/', views.collaterals_entity, name='collaterals_entity'),
    path('release-loan/<int:member_id>/<int:loan_id>/', views.release_loan, name='release_loan'),
    path('release-loan-entity/<str:entity_id>/<int:loan_id>/', views.release_loan_entity, name='release_loan_entity'),
    path('loan-summary/<int:member_id>/<int:loan_id>/', views.loan_summary, name='loan_summary'),
    path('loan-summary-entity/<str:entity_id>/<int:loan_id>/', views.loan_summary_entity, name='loan_summary_entity'),
    path('view-loan-products/',views. view_loan_products, name='view_loan_products'),
    path('view-issued-loans/',views. view_issued_loans, name='view_issued_loans'),
    #path('loan-eligibility/<int:member_id>/', views.loan_eligibility, name='loan_eligibility'),
    #path('collaterals/<int:member_id>/<int:loan_id>/', views.collaterals, name='collaterals'),
    path('guarantors/<int:member_id>/<int:loan_id>/', views.guarantors, name='guarantors'),
    path('guarantors_entity/<str:entity_id>/<int:loan_id>/', views.guarantors_entity, name='guarantors_entity'),
     # Other URL patterns...
    path('delete-guarantor/<int:member_id>/<int:loan_id>/<int:guarantor_id>/', views.delete_guarantor, name='delete_guarantor'),
    path('delete-collateral/<int:member_id>/<int:loan_id>/<int:collateral_id>/', views.delete_collateral, name='delete_collateral'),
    path('delete-guarantor-entity/<str:entity_id>/<int:loan_id>/<int:guarantor_id>/', views.delete_guarantor_entity, name='delete_guarantor_entity'),
    path('delete-collateral-entity/<str:entity_id>/<int:loan_id>/<int:collateral_id>/', views.delete_collateral_entity, name='delete_collateral_entity'),
    path('collateral-and-guarantor-check/<int:member_id>/<int:loan_id>/', views.collateral_and_guarantor_check, name='collateral_and_guarantor_check'),
    path('collateral-and-guarantor-check-entity/<str:entity_id>/<int:loan_id>/', views.collateral_and_guarantor_check_entity, name='collateral_and_guarantor_check_entity'),
    path('loan-approvals/', views.loan_approval_list, name='loan_approval_list'),
    #path('loan-approval/<int:loan_id>/', views.loan_approval_detail, name='loan_approval_detail'),
    path('loan-approval/member/<int:loan_id>/', views.loan_approval_member_detail, name='loan_approval_member_detail'),
    path('loan-approval/entity/<int:loan_id>/', views.loan_approval_entity_detail, name='loan_approval_entity_detail'),


]


