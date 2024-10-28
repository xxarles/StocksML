import time
import logging
from urllib import response
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


def register_new_ingestions():
    response = requests.get(os.environ.get("REGISTER_NEW_INGESTIONS_URL", ""))
    try:
        response.raise_for_status()
    except Exception as e:
        logger.error(e)


def cleanup_stale_ingestion():
    response = requests.get(os.environ.get("CLEANUP_INGESTION_PENDING_STATUS", ""))
    try:
        response.raise_for_status()
    except Exception as e:
        logger.error(e)


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
            logger.info("Cleaning up stale ingestion")
            cleanup_stale_ingestion()

            logger.info("Checking to register new ingestions")
            register_new_ingestions()

            logger.info("Checking for new ingestions.")
            start_next_ingestion()

            logger.info("Sleeping for 10 seconds before next loop")
            time.sleep(2)

        except Exception as e:
            logger.error(e)
            time.sleep(2)
