from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.contrib.staticfiles import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

]

if settings.DEBUG:
    from django.urls import re_path

    urlpatterns += [re_path(r"^static/(?P<path>.*)$", views.serve)]
