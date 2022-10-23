import sqlite3
from numpy import diff
from pprint import pprint

TABLE_NAME="aggregated_data"

def connect_db(db_path: str):
    con = sqlite3.connect(db_path)
    return con

def get_column_names(cursor, table_name):
    res = cursor.execute("PRAGMA table_info('{}')".format(table_name))
    raw = res.fetchall()
    return [n[1] for n in raw]

def read_db(db_path: str):
    con = connect_db(db_path)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM {}".format(TABLE_NAME))
    data = res.fetchall()
    cur.close()
    con.close()
    return data

def get_timestamps_around_spike(spike, diffs, data):
    diff_id = diffs.tolist().index(spike) 
    return data[diff_id-1][0],data[diff_id+1][0]

def highlight_spikes(db_path: str):
    con = connect_db(db_path)
    cur = con.cursor()
    # get all series names from the aggregated_data table
    column_names = get_column_names(cur, TABLE_NAME)[1:]
    spikes = {}
    # get all values in a serie, as a tuple (timestamp,col)
    for c in column_names:
        print("colname = {}".format(c))
        res = cur.execute("SELECT timestamp,{} FROM {}".format(c,TABLE_NAME))
        data = res.fetchall()
        values = [v[1] for v in data]
        # run diff on values
        diffs = diff(values)
        print("diffs = {}".format(diffs))
        # get the average of diffs
        avg_diff = sum([abs(d) for d in diffs]) / len(diffs)
        print("avg_diff = {}".format(+avg_diff))
        # extract the tuples with value > 1.5 * avg_diff 
        spikes[c] = [get_timestamps_around_spike(spike, diffs, data) for spike in diffs if spike > 1.5 * avg_diff]
        if len(spikes[c]) > 0:
            res = cur.execute("INSERT INTO spikes VALUES ({},{},\"{}\")".format(spikes[c][0][0],spikes[c][0][1],c))
            insert_result = res.fetchall()
    # for each match
    #   insert a new (spike_start_timestamp,spike_stop_timestamp,spike_serie_name)
    #       with spike_start_timestamp = previous_timestamp_before_match (matched_timestamp - previous_timestamp_before_match) / 2
    #       with spike_stop_timestamp = matched_timestamp (next_timestamp_after_match - matched_timestamp) / 2
    cur.close()
    con.close()
    return spikes


def fixture(db_path: str):
    con = sqlite.connect(db_path)
    cur = con.cursor()
    res = cur.execute("CREATE TABLE aggregated_data(timestamp, val1, val2)")
    return res