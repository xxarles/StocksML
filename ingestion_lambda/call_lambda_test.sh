docker run -e TICKER=PDD -e FROM_DATE=2023-01-01 -e TO_DATE=2023-01-31 -e TYPE=HOUR -e INGESTION_ID=1655 -e MULTIPLIER=1 -e BUCKET=stocks -e ORG=MyOrg -e INFLUX_TOKEN=MyInitialAdminToken0== -e INFLUX_URL=http://marketdataml-influxdb2-1:8086 -e POLYGON_API_KEY=J9VFvuEFRQ0CoJ06AHDP4zoXEbsyHVVX -e INGESTION_STATUS_UPDATE_URL=http://stocks-backend:8000/stocks_metadata/update_ingestion_status -e ID=1655 --network marketdataml_default ingestion_lambda:latest