import datetime
from django.urls import reverse
import pytest

from .views import enqueue_new_ingestion, update_end_ingestion_time
from .models import (
    IngestionMetadata,
    IngestionStatus,
    IngestionTimespan,
    StockIngestion,
    Tickers,
)

dummy_old_date = datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dummy_recent_date = datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)


def create_dummy_ticker():
    return Tickers.objects.create(symbol="AAPL", name="Apple Inc.", exchange="N", type="tech")


def create_dummy_ingestion_metadata(dummy_ticker):
    StockIngestion.objects.create(
        ticker=dummy_ticker,
        ingestion_started_at=dummy_old_date,
        ingestion_status=IngestionStatus.SUCCESS,
        ingestion_finished_at=dummy_old_date,
        created_at=dummy_old_date,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=dummy_old_date,
            end_ingestion_time=dummy_old_date,
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )

    StockIngestion.objects.create(
        ticker=dummy_ticker,
        ingestion_started_at=dummy_old_date,
        ingestion_status=IngestionStatus.FAILURE,
        ingestion_finished_at=dummy_old_date,
        created_at=dummy_old_date,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=dummy_old_date,
            end_ingestion_time=dummy_old_date,
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )
    StockIngestion.objects.create(
        ticker=dummy_ticker,
        ingestion_started_at=dummy_old_date,
        ingestion_status=IngestionStatus.ON_QUEUE,
        ingestion_finished_at=dummy_old_date,
        created_at=dummy_old_date,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=dummy_old_date,
            end_ingestion_time=dummy_old_date,
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )
    StockIngestion.objects.create(
        ticker=dummy_ticker,
        ingestion_started_at=dummy_old_date,
        ingestion_status=IngestionStatus.DEPLOYING,
        ingestion_finished_at=dummy_old_date,
        created_at=dummy_old_date,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=dummy_old_date,
            end_ingestion_time=dummy_old_date,
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )


# Create your tests here.
@pytest.mark.django_db
def test_create_ticker(client):
    response = client.post(
        reverse("tickers"),
        {"name": "AAPL", "symbol": "AAPL", "exchange": "N", "type": "tec"},
    )
    assert response.status_code == 200
    all_tickers_response = client.get(reverse("tickers"))

    assert all_tickers_response.status_code == 200
    assert len(all_tickers_response.json()["data"]) == 1


@pytest.mark.django_db
def test_fail_create_ticker(client):
    response = client.post(reverse("ticker"), {"name": "AAPL", "exchange": "N", "type": "tec"})
    assert response.status_code == 400
    all_tickers_response = client.get(reverse("tickers"))

    assert all_tickers_response.status_code == 200
    assert len(all_tickers_response.json()["data"]) == 0


@pytest.mark.django_db
def test_update_ingestion_time(client):
    ticker = create_dummy_ticker()
    create_dummy_ingestion_metadata(ticker)

    response = client.get(reverse("list_ingestion_data"))
    for entry in response.json()["data"]:
        assert entry["ingestion_status"] in [
            IngestionStatus.SUCCESS,
            IngestionStatus.FAILURE,
            IngestionStatus.ON_QUEUE,
            IngestionStatus.DEPLOYING,
        ]
    assert len(response.json()["data"]) == 4

    update_end_ingestion_time()

    response = client.get(reverse("list_ingestion_data"))
    for entry in response.json()["data"]:
        assert entry["ingestion_status"] in [
            IngestionStatus.SUCCESS,
            IngestionStatus.FAILURE,
            IngestionStatus.ON_QUEUE,
            IngestionStatus.DEPLOYING,
        ]
        if entry["ingestion_status"] != IngestionStatus.ON_QUEUE:
            assert datetime.datetime.fromisoformat(entry["metadata__end_ingestion_time"]) == dummy_old_date
        else:
            assert datetime.datetime.fromisoformat(entry["metadata__end_ingestion_time"]) != dummy_old_date
    assert len(response.json()["data"]) == 4


@pytest.mark.django_db
def test_enqueue_new_ingestion_non_existent(client):
    ticker = create_dummy_ticker()
    enqueue_new_ingestion(ticker)

    response = client.get(reverse("list_ingestion_data"))
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["ingestion_status"] == IngestionStatus.ON_QUEUE
    assert data[0]["ticker__symbol"] == ticker.symbol
    assert datetime.datetime.fromisoformat(data[0]["metadata__start_ingestion_time"]) == datetime.datetime(
        2000, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
    )


@pytest.mark.django_db
def test_enqueue_new_ingestion_with_existing(client):
    ticker = create_dummy_ticker()

    StockIngestion.objects.create(
        ticker=ticker,
        ingestion_started_at=dummy_old_date,
        ingestion_status=IngestionStatus.SUCCESS,
        ingestion_finished_at=dummy_old_date,
        created_at=dummy_old_date,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=dummy_old_date,
            end_ingestion_time=dummy_recent_date,
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )
    enqueue_new_ingestion(ticker)

    response = client.get(reverse("list_ingestion_data"))
    data = response.json()["data"]
    assert len(data) == 2
    new_entry = data[1]
    assert new_entry["ingestion_status"] == IngestionStatus.ON_QUEUE
    assert datetime.datetime.fromisoformat(new_entry["metadata__start_ingestion_time"]) == dummy_recent_date


@pytest.mark.django_db
def test_register_new_ingestions_no_prev_ingestion(client):
    ticker = create_dummy_ticker()
    response = client.get(reverse("register_new_ingestions"))
    assert response.status_code == 200

    response = client.get(reverse("list_ingestion_data"))
    data = response.json()["data"]
    assert len(data) == 1
    assert ticker.symbol == data[0]["ticker__symbol"]
    assert data[0]["ingestion_status"] == IngestionStatus.ON_QUEUE
    assert datetime.datetime.fromisoformat(data[0]["metadata__end_ingestion_time"]) == datetime.datetime.fromisoformat(
        data[0]["metadata__start_ingestion_time"]
    ) + datetime.timedelta(days=30)


@pytest.mark.django_db
def test_no_next_ingestion(client):
    response = client.get(reverse("start_next_ingestion"))
    assert response.json()["data"] is None


@pytest.mark.django_db
def test_start_next_ingestion(client):
    ticker = create_dummy_ticker()
    StockIngestion.objects.create(
        ticker=ticker,
        ingestion_status=IngestionStatus.ON_QUEUE,
        created_at=dummy_old_date,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=dummy_old_date,
            end_ingestion_time=dummy_old_date + datetime.timedelta(days=3),
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )
    response = client.get(reverse("start_next_ingestion"))
    assert response.json()["data"] is not None
