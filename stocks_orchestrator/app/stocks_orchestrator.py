import time
import logging
import requests
import os


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger = get_module_logger(__file__)


def start_next_ingestion():
    response = requests.get(os.environ.get("NEXT_INGESTION_URL", ""))
    try:
        response.raise_for_status()
    except Exception as e:
        logger.error(e)

    if response.json()["data"]:
        logger.info("New ingestion started.")
        start_next_ingestion()
    else:
        logger.info("No ingestion started.")
        return


if __name__ == "__main__":
    while True:
        try:
            logger.info("Checking for new ingestions.")
            start_next_ingestion()

            logger.info("Sleeping for 10 seconds before next loop")
            time.sleep(10)

        except Exception as e:
            logger.error(e)
            time.sleep(10)
