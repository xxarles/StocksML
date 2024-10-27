from django.urls import path

from . import views

urlpatterns = [
    path("list_all_tickers", views.list_all_tickers, name="list_all_tickers"),
    path("register_new_ticker", views.register_new_ticker, name="register_new_ticker"),
    path("list_ingestion_data", views.list_ingestion_data, name="list_ingestion_data"),
    path("register_new_ingestions", views.register_new_ingestions, name="register_new_ingestions"),
]
