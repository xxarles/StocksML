docker build -t ingestion_lambda ./ingestion_lambda
docker build -t stocks_backend ./stocks_backend
docker build -t stocks_orchestrator ./stocks_orchestrator
docker compose down
docker compose up