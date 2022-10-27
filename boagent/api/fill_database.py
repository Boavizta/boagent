import random
from datetime import datetime, timedelta

from database import get_engine, get_session, create_database, insert_metric, CarbonIntensity
from config import settings


def fill_carbon_intensity():
    engine = get_engine(settings.db_path)
    CarbonIntensity.__table__.drop(engine)
    create_database(engine)

    session = get_session(settings.db_path)
    now = datetime.utcnow()
    curr_date = now - timedelta(days=1)
    while curr_date < now:
        insert_metric(session, 'carbonintensity', curr_date, random.gauss(540, 50))
        curr_date += timedelta(minutes=5)


if __name__ == '__main__':
    fill_carbon_intensity()
