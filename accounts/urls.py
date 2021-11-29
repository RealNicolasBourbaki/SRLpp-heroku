from django.urls import path
from .views import MyPasswordResetView, reset_password, SignUpView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('password_reset/', MyPasswordResetView.as_view(), name="password_reset"),
]
