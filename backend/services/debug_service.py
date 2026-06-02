from database import get_db_connection


def sqlite_schema(table:str):
    allowed={"users","challenges","enrollments","checkins","user_stats"}
    if table not in allowed:
        return {"ok":False,"error":"table_not_allowed"},400
    conn=get_db_connection()
    try:
        cols=conn.execute(f"PRAGMA table_info({table})").fetchall()
        return {"ok":True,"table":table,"columns":[dict(c) for c in cols]},200
    finally: conn.close()

def sqlite_counts():
    conn=get_db_connection(); out={}
    try:
        for t in ["users","challenges","enrollments","checkins","user_stats"]:
            try: out[t]=conn.execute(f"SELECT COUNT(*) as n FROM {t}").fetchone()['n']
            except Exception as e: out[t]=str(e)
        return {"ok":True,"counts":out},200
    finally: conn.close()
