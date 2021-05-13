from django.urls import path, include, re_path
from dj_rest_auth.registration.views import VerifyEmailView

from AuthenticationApp import views
from AuthenticationApp.views import ConfirmEmailView, GoogleLogin


urlpatterns = [
    path(r'auth/google', GoogleLogin.as_view(), name='google_login'),
    path('verify-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    re_path(r'^account/registration/account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
         name='account_confirm_email'),
    path('account/', include('dj_rest_auth.urls')),
    path('account/registration/', include('dj_rest_auth.registration.urls')),

    path('user_details/<str:email>', views.get_user_details),
]
