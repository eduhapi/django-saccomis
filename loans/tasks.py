# loans/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_task():
    logger.info("Starting test_task")
    try:
        print("Test Task Executed")
        logger.info("Test Task Executed")
        return "Test Task Executed"
    except Exception as e:
        logger.error(f"Error in test_task: {e}")
        raise e
