from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("stocks_metadata/", include("stocks_metadata.urls")),
    path("admin/", admin.site.urls),
]