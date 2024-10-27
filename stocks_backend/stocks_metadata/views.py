import subprocess
import datetime
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, JsonResponse
from django.db import transaction
from django.db.models import Q, QuerySet
from django.views.decorators.http import require_GET
from django.core import serializers

from stocks_backend.enums import Environments
from stocks_backend.settings import (
    ENVIRONMENT,
    INFLUX_TOKEN,
    INFLUX_URL,
    LOCAL_DOCKER_NAME_DEFAULT,
    LOCAL_DOCKER_NETWORK_NAME,
    LOCAL_DOCKER_SETTINGS_KEY,
    LOCAL_INGESTION_BUCKET_DEFAULT,
    LOCAL_INGESTION_BUCKET_SETTING_KEY,
    LOCAL_ORG_DEFAULT,
    LOCAL_ORG_SETTING_KEY,
    MAX_PARALLEL_INGESTIONS,
    POLYGON_API_KEY,
)
from stocks_backend.utils import get_module_logger
from stocks_metadata.models import (
    AppSettings,
    IngestionMetadata,
    IngestionStatus,
    IngestionTimespan,
    StockIdx,
    StockIngestion,
    Tickers,
)

# Create logger and set to info
logger = get_module_logger(__file__)


@transaction.atomic()
def tickers_relations(request: HttpRequest, ticker1: str, ticker2: str) -> HttpResponse:
    if request.method == "PUT":
        ticker_object1 = Tickers.objects.filter(Q(symbol=ticker1)).first()
        ticker_object2 = Tickers.objects.filter(Q(symbol=ticker2)).first()
        if not ticker_object1 or not ticker_object2:
            return HttpResponseServerError("Tickers do not exist please validate.", status=500)
        else:
            ticker_object1.relations.add(ticker_object2)
            ticker_object2.relations.add(ticker_object1)
            Tickers().save()
            return HttpResponse(f"Created relation between {ticker1} and {ticker2}", status=201)

    else:
        return HttpResponseNotAllowed(permitted_methods=["PUT"])


@transaction.atomic()
def tickers(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = StockIdx.objects.filter(deleted=False).values()
        return JsonResponse({"data": list(data.values())}, status=200)

    elif request.method == "POST":
        name = request.POST.get("name")
        symbol = request.POST.get("symbol")
        exchange = request.POST.get("exchange")
        type = request.POST.get("type")

        logger.info(
            f"""Creating new ticker with info: 
                    name: {name}
                    symbol: {symbol}
                    exchange: {exchange}
                    type: {type}
                    """
        )
        try:
            new_ticker = Tickers.objects.create(symbol=symbol, name=name, exchange=exchange, type=type)
            StockIdx.objects.create(ticker=new_ticker, deleted=False)
            return HttpResponse("Created new ticker", status=200)

        except Exception as e:
            logger.error(e)
            return HttpResponseServerError(f"Internal Server Error: {e}", status=500)

    else:
        return HttpResponseNotAllowed(permitted_methods=["GET", "POST"])


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


def get_idle_ingestion_tickers() -> QuerySet[Tickers]:
    return Tickers.objects.filter(
        Q(
            symbol__in=StockIngestion.objects.filter(~Q(ingestion_status=IngestionStatus.ON_QUEUE)).values(
                "ticker__symbol"
            )
        )
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
            end_ingestion_time=min(end_ingestion_time, last_end_time + datetime.timedelta(days=30)),
            delta_category=IngestionTimespan.HOUR,
            delta_multiplier=1,
        ),
    )
    logger.info(f"Equeued new ingestion for symbol {ticker.symbol} with end_time or {last_end_time}")


@transaction.atomic()
def register_new_ingestions(request: HttpRequest | None) -> HttpResponse:
    # Gets all symbols that have never been ingested before
    on_queue_symbols = get_idle_ingestion_tickers()
    idle_symbols = list(Tickers.objects.difference(on_queue_symbols))

    for idle_symbol in idle_symbols:
        enqueue_new_ingestion(idle_symbol)

    return HttpResponse("Enqueued new ingestions and updated existing ones", status=200)


def get_ingestion_in_progress() -> QuerySet[StockIngestion]:
    return StockIngestion.objects.filter(
        Q(ingestion_status=IngestionStatus.DEPLOYING) | (Q(ingestion_status=IngestionStatus.IN_PROGRESS))
    )


def get_settings_value(key: str) -> str | None:
    if value := AppSettings.objects.filter(key=key).first():
        return value.value
    else:
        return None


def deploy_ingestion(ingestion: StockIngestion):
    if ENVIRONMENT == Environments.LOCAL:
        logger.info("Starting local container for ingestion")

        command = [
            "docker",
            "run",
            "-e",
            f"TICKER={ingestion.ticker.symbol}",
            "-e",
            f"FROM_DATE={ingestion.metadata.start_ingestion_time.date().isoformat()}",
            "-e",
            f"TO_DATE={ingestion.metadata.end_ingestion_time.date().isoformat()}",
            "-e",
            f"TYPE={ingestion.metadata.delta_category}",
            "-e",
            f"MULTIPLIER={ingestion.metadata.delta_multiplier}",
            "-e",
            f"BUCKET={get_settings_value(LOCAL_INGESTION_BUCKET_SETTING_KEY) or LOCAL_INGESTION_BUCKET_DEFAULT}",
            "-e",
            f"ORG={get_settings_value(LOCAL_ORG_SETTING_KEY) or LOCAL_ORG_DEFAULT}",
            "-e",
            f"INFLUX_TOKEN={INFLUX_TOKEN}",
            "-e",
            f"INFLUX_URL={INFLUX_URL}",
            "-e",
            f"POLYGON_API_KEY={POLYGON_API_KEY}",
            "--network",
            LOCAL_DOCKER_NETWORK_NAME,
            get_settings_value(LOCAL_DOCKER_SETTINGS_KEY) or LOCAL_DOCKER_NAME_DEFAULT,
        ]

        subprocess.run(command)

    else:
        raise NotImplementedError("Only local environment is supported for now")


@require_GET
@transaction.atomic
def start_next_ingestion(request: HttpRequest):
    # Gets the oldest ingestion in the queue
    if get_ingestion_in_progress().count() >= MAX_PARALLEL_INGESTIONS:
        logger.info("Not starting ingestion because max parallel ingestion are already running")
        return JsonResponse({"data": None, "reason": "Max parallel ingestions running"}, status=200)

    next_ingestion = (
        StockIngestion.objects.filter(ingestion_status=IngestionStatus.ON_QUEUE)
        .order_by("metadata__end_ingestion_time")
        .first()
    )
    if next_ingestion:
        logger.info(
            f"Starting ingestion for {next_ingestion.ticker.symbol} with start time {next_ingestion.metadata.start_ingestion_time} and end time {next_ingestion.metadata.end_ingestion_time}"
        )
        next_ingestion.ingestion_status = IngestionStatus.DEPLOYING
        deploy_ingestion(next_ingestion)

        return JsonResponse(
            {
                "data": serializers.serialize(
                    "json",
                    [
                        next_ingestion,
                    ],
                )
            },
            status=200,
        )

    else:
        return JsonResponse({"data": None, "reason": "No ingestions in queue"}, status=200)
