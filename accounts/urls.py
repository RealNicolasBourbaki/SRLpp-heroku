from django.urls import path
from .views import MyPasswordResetView, reset_password, signup, activate


urlpatterns = [
    path('signup/', signup(), name='signup'),
    path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
    path('password_reset/', MyPasswordResetView.as_view(), name="password_reset"),
]
