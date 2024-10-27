from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class IngestionStatus(models.TextChoices):
    """Choices for ingestion status"""

    ON_QUEUE = "ON_QUEUE"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    IN_PROGRESS = "IN_PROGRESS"
    DEPLOYING = "DEPLOYING"


class IngestionTimespan(models.TextChoices):
    """Choices for ingestion timespan"""

    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"


class Tickers(models.Model):
    """Model to store ticker data"""

    symbol = models.CharField(max_length=10, primary_key=True, auto_created=True)
    name = models.CharField(max_length=100)
    exchange = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=50, null=True)
    relations = models.ManyToManyField("Tickers", symmetrical=False)

    class Meta(TypedModelMeta):
        """Indexing on every column since input is rare"""

        indexes = [
            models.Index(fields=["symbol"], name="symbol_idx"),
            models.Index(fields=["name"], name="name_idx"),
            models.Index(fields=["exchange"], name="exchange_idx"),
        ]


class IngestionMetadata(models.Model):
    """This keeps track of the parameters used for ingestion."""

    id = models.AutoField(primary_key=True, auto_created=True)
    start_ingestion_time = models.DateTimeField()
    end_ingestion_time = models.DateTimeField()
    delta_category = models.TextField(choices=IngestionTimespan.choices)
    delta_multiplier = models.SmallIntegerField()


class StockIngestion(models.Model):
    """This keeps track of the timing of ingestion to help with orchestration."""

    id = models.AutoField(primary_key=True, auto_created=True)
    ticker = models.ForeignKey(Tickers, on_delete=models.CASCADE)
    ingestion_started_at = models.DateTimeField(null=True)
    ingestion_status = models.TextField(choices=IngestionStatus.choices)
    ingestion_finished_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.ForeignKey(IngestionMetadata, on_delete=models.CASCADE)


# Create your models here.
class StockIdx(models.Model):
    """Base model for stocks."""

    id = models.AutoField(primary_key=True, auto_created=True)
    ticker = models.ForeignKey(Tickers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        """Indexing on every column since input is rare"""

        indexes = [
            models.Index(fields=["created_at"], name="created_at_idx"),
            models.Index(fields=["updated_at"], name="updated_at_idx"),
            models.Index(fields=["deleted"], name="deleted_idx"),
        ]


# Basic app settings
class AppSettings(models.Model):
    """Model to store app settings"""

    key = models.CharField(max_length=50, primary_key=True)
    value = models.TextField()

    class Meta:
        """Indexing on every column since input is rare"""

        indexes = [
            models.Index(fields=["key"], name="key_idx"),
            models.Index(fields=["value"], name="value_idx"),
        ]
