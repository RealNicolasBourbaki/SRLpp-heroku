from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "SRL++ Administrator Tool"
admin.site.site_title = "SRL++ site admin"
urlpatterns = [  # Django look from top to bottom for url patterns
    path('admin/', admin.site.urls),
    path('submission/', include('mails.urls')),
    path('accounts/', include('accounts.urls')),
    # if there is a url route in accounts app that matches auth, it chooses accounts
    path('accounts/', include('django.contrib.auth.urls')),  # pages control for auth function
    path('catalogue/', include('catalogue.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)