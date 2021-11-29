from django.urls import re_path
from .views import check_status

urlpatterns = [
    re_path(r'^submission_status/.*$', check_status, name='submission_status'),
]