from django.urls import path

from stocks_metadata import views

urlpatterns = [
    path("tickers", views.tickers, name="tickers"),
    path("list_ingestion_data", views.list_ingestion_data, name="list_ingestion_data"),
    path("register_new_ingestions", views.register_new_ingestions, name="register_new_ingestions"),
    path("start_next_ingestion", views.start_next_ingestion, name="start_next_ingestion"),
    path("tickers_relations/?P<str:ticker1>/?P<str:ticker2>", views.tickers_relations, name="tickers_relations"),
]
