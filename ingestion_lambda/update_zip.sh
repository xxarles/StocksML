# This created the zip file for the lambda function and updates the zip file in the packaged_lambda folder
export STOCKS_INGESTION_ZIP_NAME=stocks_ingestion.zip
rm -f $STOCKS_INGESTION_ZIP_NAME
cd .venv/lib/python3.12/site-packages
zip ../../../../$STOCKS_INGESTION_ZIP_NAME -r .
cd ../../../..
zip -r $STOCKS_INGESTION_ZIP_NAME lambda_function.py
mv $STOCKS_INGESTION_ZIP_NAME ../packaged_lambda/$STOCKS_INGESTION_ZIP_NAME