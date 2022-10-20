import sqlite3

def read_db(db_path: str):
    print(db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM aggregated_data")
    print(res)
    return res.fetchall()

def fixture(db_path: str):
    con = sqlite.connect(db_path)
    cur = con.cursor()
    res = cur.execute("CREATE TABLE aggregated_data(timestamp, val1, val2)")
    return res
