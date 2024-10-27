from django.db import migrations, models

from stocks_metadata.models import Tickers

import os


def populate_tickers(_, __):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "../initial_data/base_list_of_stocks.txt")
    with open(filename) as f:
        for symbol in f.readlines():
            Tickers.objects.get_or_create(symbol=symbol)


class Migration(migrations.Migration):
    initial = True
    dependencies = [("stocks_metadata", "0004_alter_tickers_symbol")]
    operations = [
        migrations.RunPython(populate_tickers),
    ]
