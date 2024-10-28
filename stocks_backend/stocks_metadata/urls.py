from django.urls import path

from stocks_metadata import views

urlpatterns = [
    path("tickers", views.tickers, name="tickers"),
    path("list_ingestion_data", views.list_ingestion_data, name="list_ingestion_data"),
    path("register_new_ingestions", views.register_new_ingestions, name="register_new_ingestions"),
    path("start_next_ingestion", views.start_next_ingestion, name="start_next_ingestion"),
    path("tickers_relations/?P<str:ticker1>/?P<str:ticker2>", views.tickers_relations, name="tickers_relations"),
    path("update_ingestion_status", views.update_ingestion_status, name="update_ingestion_status"),
    path(
        "cleanup_ingestion_pending_status",
        views.cleanup_ingestion_pending_status,
        name="cleanup_ingestion_pending_status",
    ),
]
