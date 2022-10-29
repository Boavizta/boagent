from datetime import datetime, timedelta
from typing import Any, Optional
from click import option

import pandas as pd
import numpy as np
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

class Power(TimeSeriesRecord):
    pass

class CpuUsage(TimeSeriesRecord):
    pass

class RamCurrentUsage(TimeSeriesRecord):
    pass

metrics = {
    'carbonintensity': CarbonIntensity,
    'power': Power,
#    'cpuusage': CpuUsage,
#    'ram': RamCurrentUsage,
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


def insert_metric_and_commit(session: Session, metric_name: str, timestamp: datetime, value: Any):
    model = metrics[metric_name]
    statement = insert(model).values(timestamp=timestamp, value=value)
    session.execute(statement)
    session.commit()

def select_metric(session: Session,
                  metric_name: str,
                  start_date: Optional[datetime] = None,
                  stop_date: Optional[datetime] = None) -> pd.DataFrame:
    if metric_name not in metrics:
        return pd.DataFrame()
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
    with open(settings.power_file_path, 'r') as f:  # if scaphandre is writing in the json -> KABOUM
        data = json.loads(f.read())
        lst = [d["host"] for d in data]
        print("in power_to_csv start_date: {} stop_date: {}".format(start_date, stop_date))
        wanted_data = filter_date_range(lst, start_date, stop_date)
        for d in wanted_data:
            # d["timestamp"] = datetime.fromtimestamp(d["timestamp"]).isoformat()
            d["timestamp"] = datetime.fromtimestamp(d["timestamp"])
            # datetime.fromisoformat(d["timestamp"]).strftime("%Y-%m-%dT%H:%M:%SZ") #
            d["consumption"] = float("{:.4f}".format(d["consumption"] * 10 ** -3))
        return pd.DataFrame(wanted_data, columns=["timestamp", "consumption"])


def get_full_peak(start: int, diffs: list) -> list:
    val = diffs[start]
    sign = -1 if val < 0 else 0 if val == 0 else 1
    res = []
    recover = 0.25
    i = 1
    if sign > 0:
        while val > recover * val and start + i < len(diffs):
            val += diffs[start + i]
            res.append(start + i)
            i = i + 1
    else:
        while val < (- 3 * recover * val) and start + i < len(diffs):
            val += diffs[start + i]
            res.append(start + i)
            i = i + 1
    return res, sign


def highlight_spikes(data: pd.DataFrame, colname: str = None) -> pd.DataFrame:
    if len(data.keys()) > 0:
        if colname is None:
            colname = data.keys()[1]

        diffs = np.diff(data[colname])

        factor = 1.2

        avg_diff = sum([abs(d) for d in diffs]) / len(diffs)

        peaks_ids = np.where(abs(diffs) > avg_diff * factor)

        data["peak"] = 0

        for i in peaks_ids[0].tolist():
            full_peak = get_full_peak(i, diffs.tolist())
            data["peak"][full_peak[0]] = full_peak[1]
            # data.loc[:, ("peak", full_peak[0])] = full_peak[1]
        
        data["peak"][data[[colname]].idxmin()] = -1
        data["peak"][data[[colname]].idxmax()] = 1

    return data


def new_highlight_spikes(df: pd.DataFrame, col: str = 'value') -> pd.DataFrame:
    rol_col = f'_rolling_{col}'
    quant_max = df[col].quantile(q=0.70)
    quant_min = df[col].quantile(q=0.20)
    window = 3
    df[rol_col] = df[col].ewm(span=window).mean()
    df['peak'] = 0
    indexes_max = df[df[rol_col] >= quant_max].index
    indexes_min = df[df[rol_col] <= quant_min].index
    df.loc[indexes_max, 'peak'] = 1
    df.loc[indexes_min, 'peak'] = -1

    for row in df.itertuples():
        if row.peak != 0 and row.Index > window + 2:
            for i in range(window+1):
                df.loc[row.Index - i, 'peak'] = row.peak

    df = df.drop(columns=[rol_col])
    return df

def get_most_recent_timestamp(session, table):
    """ Get a single row from the table which has the most recent timestamp"""
    toto = session.query(table).order_by(table.timestamp.desc()).first()
    return toto.timestamp if toto != None else None


def add_from_scaphandre(session, table):
    last_timestamp = get_most_recent_timestamp(session, table=Power)
    last_timestamp = last_timestamp + timedelta(seconds=5) if last_timestamp != None else datetime.now() - timedelta(hours=24)
    print("\n\n\n" + str(last_timestamp) + "\n\n\n")
    if table == Power:
        df = power_to_csv(start_date=last_timestamp,stop_date=datetime.now())
    else:
        pass
    if df.empty:
        return
    else:
        for row in df.itertuples():
            insert_metric(session, metric_name='power' , timestamp=row.timestamp, value=row.consumption)
