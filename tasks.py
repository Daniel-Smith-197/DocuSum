from celery import Celery
from summarize import docuSum
from database import SessionClass, Summary
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery("tasks", broker = os.getenv("broker_url"), backend = os.getenv("backend_url"))

@celery_app.task
def work(text, mode, filename):
    session = SessionClass()
    try:
        response, tokens = docuSum(text, mode)
        date = datetime.now(tz = timezone.utc)
        record = Summary(filename = filename, sumMode = mode, summary = response, timestamp = date, token_usage = tokens)
        session.add(record)
        session.commit()
        return {"Summary": response}
    finally:
        session.close()