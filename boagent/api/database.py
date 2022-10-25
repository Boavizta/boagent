from datetime import datetime, timedelta
from typing import Any, Optional

import pandas as pd
from sqlalchemy import Column, DateTime, Integer, Float, insert, select, inspect
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, declared_attr

import json
from utils import filter_date_range
from config import settings


Base = declarative_base()


class TimeSeriesRecord(Base):
    __abstract__ = True

    id = Column(Integer, autoincrement=True, primary_key=True)
    timestamp = Column(DateTime, unique=True, nullable=False)
    value = Column(Float, nullable=False)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class CarbonIntensity(TimeSeriesRecord):
    pass


metrics = {
    'carbonintensity': CarbonIntensity
}


def create_database(engine: Engine) -> None:
    inspector = inspect(engine)
    for model_name, model in metrics.items():
        if not inspector.has_table(model_name):
            model.__table__.create(engine)


def get_session(db_path: str) -> Session:
    engine = get_engine(db_path)
    return Session(engine)


def get_engine(db_path: str) -> Engine:
    return create_engine(f'sqlite:///{db_path}')


def insert_metric(session: Session, metric_name: str, timestamp: datetime, value: Any):
    model = metrics[metric_name]
    statement = insert(model).values(timestamp=timestamp, value=value)
    session.execute(statement)
    session.commit()


def select_metric(session: Session,
                  metric_name: str,
                  start_date: Optional[datetime] = None,
                  stop_date: Optional[datetime] = None) -> pd.DataFrame:
    model = metrics[metric_name]
    if stop_date is None:
        stop_date = datetime.now()
    if start_date is None:
        start_date = stop_date - timedelta(hours=1)
    statement = select(model.timestamp, model.value).where(
        model.timestamp >= start_date,
        model.timestamp <= stop_date
    )
    results = session.execute(statement).all()
    return pd.DataFrame(results)


def power_to_csv(start_date: datetime, stop_date: datetime) -> pd.DataFrame:
    with open(settings.power_file_path,'r') as f: # if scaphandre is writing in the json -> KABOUM
        data = json.loads(f.read())
        lst = [d["host"] for d in data]
        wanted_data = filter_date_range(lst, start_date, stop_date)
        for d in wanted_data:
            #d["timestamp"] = datetime.fromtimestamp(d["timestamp"]).isoformat()
            d["timestamp"] = datetime.fromisoformat(datetime.fromtimestamp(d["timestamp"]).isoformat()).strftime("%Y-%m-%dT%H:%M:%SZ")
            d["consumption"] = float("{:.4f}".format(d["consumption"] * 10**-3))
        return pd.DataFrame(wanted_data,columns=["timestamp", "consumption"])
