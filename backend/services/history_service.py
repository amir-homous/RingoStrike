from datetime import datetime, timedelta, timezone
from database import get_db_connection
from utils.validation_utils import safe_int


def enrollment_history(user_id:int,enrollment_id:int,days_param):
    conn=get_db_connection()
    try:
        enroll=conn.execute("SELECT * FROM enrollments WHERE id=? AND user_id=?",(enrollment_id,user_id)).fetchone()
        if not enroll: return {"ok":False,"error":"forbidden_enrollment"},403
        days=max(1,min(safe_int(days_param,30),120))
        end_date=datetime.now(timezone.utc).date(); start=end_date-timedelta(days=days-1)
        logs=conn.execute("SELECT date,status,is_counted FROM checkins WHERE enrollment_id=? AND date BETWEEN ? AND ?",(enrollment_id,start.isoformat(),end_date.isoformat())).fetchall()
        by={r['date']:r for r in logs}
        timeline=[]; checked=0
        for i in range(days):
            d=(start+timedelta(days=i)).isoformat(); row=by.get(d)
            st=row["status"] if row else None
            is_counted=bool(row["is_counted"]) if row else False
            if is_counted: checked+=1
            timeline.append({"date":d,"status":st,"is_counted":is_counted})
        return {"ok":True,"summary":{"checked_days":checked,"total_days":days},"items":timeline},200
    finally: conn.close()
