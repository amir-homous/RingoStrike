from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.stats_service import sync_user_stats, calculate_current_streak


def checkin(user_id:int,enrollment_id:int):
    date_iso=utc_today_iso(); conn=get_db_connection()
    try:
        enroll=conn.execute("SELECT id, challenge_id FROM enrollments WHERE id=? AND user_id=?",(enrollment_id,user_id)).fetchone()
        if not enroll: return {"ok":False,"error":"forbidden_enrollment"},403
        ex=conn.execute("SELECT id FROM checkins WHERE enrollment_id=? AND date=?",(enrollment_id,date_iso)).fetchone()
        if ex: conn.execute("UPDATE checkins SET status='Done' WHERE id=?",(ex['id'],))
        else: conn.execute("INSERT INTO checkins (enrollment_id, user_id, challenge_id, date, status, is_counted) VALUES (?, ?, ?, ?, 'Done', 1)",(enrollment_id,user_id,enroll['challenge_id'],date_iso))
        conn.commit(); sync_user_stats(user_id)
        return {"ok":True,"message":"Check-in recorded"},200
    finally: conn.close()