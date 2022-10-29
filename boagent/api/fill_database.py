from datetime import datetime, timedelta

from api import query_electricity_carbon_intensity, parse_electricity_carbon_intensity
from database import get_engine, get_session, create_database, insert_metric, CarbonIntensity
from config import settings


def fill_carbon_intensity():
    engine = get_engine(settings.db_path)
    CarbonIntensity.__table__.drop(engine)
    create_database(engine)

    session = get_session(settings.db_path)
    now = datetime.utcnow()
    curr_date = now - timedelta(hours=24)

    while curr_date < now:
        # TODO: make bulk select in boaviztapi
        response = query_electricity_carbon_intensity(curr_date, curr_date + timedelta(minutes=5))
        info = parse_electricity_carbon_intensity(response)
        insert_metric(session, 'carbonintensity', info['timestamp'], info['value'])
        curr_date += timedelta(minutes=5)
    session.commit()


if __name__ == '__main__':
    fill_carbon_intensity()
    print('Database updated.')
