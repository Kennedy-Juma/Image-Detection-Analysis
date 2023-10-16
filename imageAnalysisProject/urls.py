"""
URL configuration for imageAnalysisProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView, RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('image_analysis.urls')),
    re_path(r'^$', RedirectView.as_view(url='/upload/', permanent=True), name='index'),

    #path("accounts/", include("django.contrib.auth.urls")),
    #path('', TemplateView.as_view(template_name='index.html'), name='index'),
    #path('upload/', TemplateView.as_view(template_name='image_analysis/templates/upload_image.html'), name='upload_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
