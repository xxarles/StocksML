from operator import index
from django.db import models

class Tickers(models.Model):
    """Model to store ticker data"""
    symbol = models.CharField(max_length=4, primary_key=True, auto_created=True)
    name = models.CharField(max_length=100)
    exchange = models.CharField(max_length=50, null=True)
    industry = models.CharField(max_length=50, null=True)
    sector = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    
    class Meta:
        """Indexing on every column since input is rare"""
        indexes = [
            models.Index(fields=["symbol"], name="symbol_idx"),
            models.Index(fields=["name"], name="name_idx"),
            models.Index(fields=["exchange"], name="exchange_idx"),
            models.Index(fields=["industry"], name="industry_idx"),
            models.Index(fields=["sector"], name="sector_idx"),
            models.Index(fields=["country"], name="country_idx"),
        ]


class IngestionMetadata(models.Model):
    """This keeps track of the parameters used for ingestion."""
    id = models.UUIDField(primary_key=True, auto_created=True)
    start_ingestion_time = models.DateTimeField()
    end_ingestion_time = models.DateTimeField()
    delta_category = models.CharField(max_length=20)
    delta_multiplier = models.SmallIntegerField()



        
class StockIngestion(models.Model):
    """This keeps track of the timing of ingestion to help with orchestration."""
    id = models.IntegerField(primary_key=True, auto_created=True)
    symbol = models.ForeignKey(Tickers, on_delete=models.CASCADE)
    started = models.DateTimeField()
    finished = models.DateTimeField()
    succeeded = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.ForeignKey(IngestionMetadata, on_delete=models.CASCADE)
    

# Create your models here.
class StockIdx(models.Model):
    """Base model for stocks."""
    id = models.AutoField(primary_key=True, auto_created=True)
    symbol = models.ForeignKey(Tickers, on_delete=models.CASCADE)
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
        
