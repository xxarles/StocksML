from django.urls import path

from . import views

urlpatterns = [
    path("tickers/<str:pk>", views.tickers, name="tickers"),
    path("list_ingestion_data", views.list_ingestion_data, name="list_ingestion_data"),
    path("register_new_ingestions", views.register_new_ingestions, name="register_new_ingestions"),
    path("start_next_ingestion", views.start_next_ingestion, name="start_next_ingestion"),
]
