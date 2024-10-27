# Currently empty and used to test infra deploy
from dataclasses import dataclass
import datetime
import time
import requests
import os
import logging
import enum
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write.point import Point


class AggType(enum.Enum):
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"
    year = "year"
    hour = "hour"
    minute = "minute"


@dataclass
class StockData:
    ticker: str
    queryCount: int
    resultsCount: int
    results: list[dict]
    status: str
    request_id: str
    count: int
    adjusted: bool
    next_url: str | None = None


def make_request(url: str):
    params = {"apiKey": os.environ.get("POLYGON_API_KEY"), "adjusted": "true", "sort": "asc"}
    r = requests.get(url, params=params)
    print(r.url)
    r.raise_for_status()
    data = r.json()
    return data


def get_stock_data(
    ticker: str, type: str, multiplier: int, from_date: datetime.date, to_date: datetime.date, max_retries: int = 10
) -> StockData:
    logging.info(
        f"Started request for {ticker} from {from_date} to {to_date} with type {type} and multiplier {multiplier}"
    )
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{type}/{from_date}/{to_date}"
    results = None
    data = None
    next_url = url
    retries = 0

    while not results or (next_url := data.next_url if data else None):
        if retries >= max_retries:
            raise Exception(f"Failed to make request to url {url} after {retries} retries")
        try:
            data = StockData(**make_request(next_url))
            if not results:
                results = data
            else:
                results.results.extend(data.results)

            logging.info(f"Received {data.count} results from request url {url}")
        except Exception as e:
            logging.error(f"Failed to make request to url {url}")
            logging.error(e)
            time.sleep(60)
            retries += 1

    return results


def write_data_to_influx(client: InfluxDBClient, bucket_name: str, org_name, data: StockData):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    measurement = "stock_data"
    tags = {"ticker": data.ticker}
    write_data = []
    for result in data.results:
        write_data.append(
            Point.from_dict(
                {
                    "measurement": measurement,
                    "tags": tags,
                    "time": datetime.datetime.fromtimestamp(result["t"] / 1000),
                    "fields": {
                        "open": float(result["o"]),
                        "close": float(result["c"]),
                        "high": float(result["h"]),
                        "low": float(result["l"]),
                        "volume": float(result["v"]),
                        "time": int(result["t"]),
                    },
                }
            )
        )

        write_api.write(bucket_name, org_name, write_data[-1])
    logging.info(f"Finished writing {len(write_data)} data points to influxdb")


def lambda_handler(event, context=None):
    logging.getLogger().setLevel(logging.INFO)
    ticker = event.get("ticker")
    type = AggType[event.get("type")]
    multiplier = event.get("multiplier")
    from_date = datetime.date.fromisoformat(event.get("from_date"))
    to_date: datetime.date = datetime.date.fromisoformat(event.get("to_date"))
    token = os.environ.get("INFLUX_TOKEN")
    url = os.environ.get("INFLUX_URL")
    stocks_bucket = event.get("stocks_bucket")
    org = event.get("org")

    logging.info(
        f"""Passed parameters: 
                ticker={ticker}
                type={type}
                multiplier={multiplier}
                from_date={from_date}
                to_date={to_date}
                token={token is not None}
                url={url}
                stockes_bucket={stocks_bucket}
                org={org}
                 """
    )
    if (
        not ticker
        or not type
        or not multiplier
        or not from_date
        or not to_date
        or not token
        or not url
        or not stocks_bucket
        or not org
    ):
        raise ValueError("Missing required parameters")

    results = get_stock_data(ticker, type.value, multiplier, from_date, to_date)
    influx_client = InfluxDBClient(url=url, token=token, ssl=False, verify_ssl=False)
    write_data_to_influx(influx_client, stocks_bucket, org, results)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", dest="ticker", type=str, help="Ticker to be ingested")
    parser.add_argument("--type", dest="type", type=str, help="Aggregation type")
    parser.add_argument("--multiplier", dest="multiplier", type=int, help="Multiplier for aggregation")
    parser.add_argument("--from_date", dest="from_date", type=str, help="From date for data")
    parser.add_argument("--to_date", dest="to_date", type=str, help="To date for data")
    parser.add_argument("--stocks_bucket", dest="stocks_bucket", type=str, help="Bucket name for stocks data")
    parser.add_argument("--org", dest="org", type=str, help="Organization name for stocks data")
    args = parser.parse_args()
    event = {
        "ticker": args.ticker,
        "type": args.type,
        "multiplier": args.multiplier,
        "from_date": args.from_date,
        "to_date": args.to_date,
        "stocks_bucket": args.stocks_bucket,
        "org": args.org,
    }

    args = parser.parse_args()
    lambda_handler(event)
