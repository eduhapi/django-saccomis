from django.urls import path, include
from .views import signup_view, login_view, activate, password_reset_request_view, password_reset_confirm_view,logout_view

app_name = 'accounts'

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/',logout_view, name='logout'),  # Add this line
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_reset/', password_reset_request_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
]
