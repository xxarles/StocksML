import json
import logging
import datetime
from multiprocessing.managers import BaseManager
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import transaction
from django.db.models import Q, QuerySet
from django.views.decorators.http import require_POST, require_GET
from .models import IngestionMetadata, IngestionStatus, IngestionTimespan, StockIdx, StockIngestion, Tickers

# Create logger and set to info
logger = logging.Logger(__file__)


@require_GET
def list_all_tickers(request: HttpRequest) -> HttpResponse:
    data = StockIdx.objects.filter(deleted=False).values(
        "ticker__symbol", "ticker__name", "ticker__exchange", "ticker__industry", "ticker__sector", "ticker__country"
    )
    return JsonResponse({"data": list(data)}, status=200)


@require_POST
@transaction.atomic()
def register_new_ticker(request: HttpRequest) -> HttpResponse:
    name = request.POST.get("name")
    symbol = request.POST.get("symbol")
    exchange = request.POST.get("exchange")
    industry = request.POST.get("industry")
    sector = request.POST.get("sector")
    country = request.POST.get("country")

    logger.info(
        f"""Creating new ticker with info: 
                name: {name}
                symbol: {symbol}
                exchange: {exchange}
                industry: {industry}
                sector: {sector}
                country: {country}"""
    )
    if name is None or symbol is None or exchange is None or industry is None or sector is None or country is None:
        return HttpResponse("Missing required fields", status=400)

    else:
        new_ticker = Tickers.objects.create(
            symbol=symbol, name=name, exchange=exchange, industry=industry, sector=sector, country=country
        )
        StockIdx.objects.create(ticker=new_ticker, deleted=False)
        return HttpResponse("Created new ticker", status=200)


@require_GET
@transaction.atomic()
def list_ingestion_data(request) -> JsonResponse:
    query = Q()
    if symbol := request.GET.get("symbol"):
        query &= Q(symbol=symbol)
    if status := request.GET.get("status_to_return"):
        query &= Q(ingestion_status__in=status)
    data = StockIngestion.objects.filter(query).order_by("created_at")
    return JsonResponse(
        {
            "data": list(
                data.values(
                    "ticker__symbol",
                    "metadata__end_ingestion_time",
                    "ingestion_status",
                    "metadata__start_ingestion_time",
                )
            )
        },
        status=200,
    )


@transaction.atomic()
def update_end_ingestion_time() -> QuerySet[Tickers]:
    # Gets all symbols that are at least one day from last ingestion
    tickers_in_process = StockIngestion.objects.filter(Q(ingestion_status=IngestionStatus.ON_QUEUE)).distinct()
    now_time = datetime.datetime.now(datetime.timezone.utc)
    for s in tickers_in_process:
        if s.metadata.end_ingestion_time < now_time:
            s.metadata.end_ingestion_time = now_time
            s.metadata.save()

    return Tickers.objects.filter(Q(symbol__in=tickers_in_process.values("ticker__symbol")))


@transaction.atomic()
def enqueue_new_ingestion(
    ticker: Tickers, end_ingestion_time: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
):
    last_success = (
        StockIngestion.objects.filter(Q(ticker=ticker))
        .filter(Q(ingestion_status=IngestionStatus.SUCCESS))
        .order_by("-metadata__end_ingestion_time")
        .first()
    )
    last_end_time = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    if last_success:
        last_end_time = last_success.metadata.end_ingestion_time

    if (end_ingestion_time - last_end_time).days < 1:
        logger.info(f"Skipping symbol {ticker.symbol} because last_end_time is less than a day away")

    StockIngestion.objects.create(
        ticker=ticker,
        ingestion_status=IngestionStatus.ON_QUEUE,
        metadata=IngestionMetadata.objects.create(
            start_ingestion_time=last_end_time,
            end_ingestion_time=end_ingestion_time,
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )
    logger.info(f"Equeued new ingestion for symbol {ticker.symbol} with end_time or {last_end_time}")


@transaction.atomic()
def register_new_ingestions() -> HttpResponse:
    # Gets all symbols that have never been ingested before
    on_queue_symbols = update_end_ingestion_time()
    idle_symbols = list(Tickers.objects.difference(on_queue_symbols))

    for idle_symbol in idle_symbols:
        enqueue_new_ingestion(idle_symbol)

    return HttpResponse("Enqueued new ingestions and updated existing ones", status=200)
