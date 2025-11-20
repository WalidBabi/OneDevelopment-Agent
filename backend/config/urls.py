from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from agent.views import pdf_admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pdf-admin/', pdf_admin_dashboard, name='pdf_admin_dashboard'),
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

