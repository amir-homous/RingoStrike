from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.stats_service import calculate_current_streak


def enrollment_leaderboard(enrollment_id:int):
    conn=get_db_connection()
    try:
        enroll=conn.execute("SELECT challenge_id FROM enrollments WHERE id=?",(enrollment_id,)).fetchone()
        if not enroll: return {"ok":False,"error":"not_found"},404
        rows=conn.execute("SELECT e.id as enrollment_id,u.name,u.username FROM enrollments e JOIN users u ON e.user_id=u.id WHERE e.challenge_id=? AND e.status='Active'",(enroll['challenge_id'],)).fetchall()
        today=utc_today_iso(); board=[]
        for r in rows:
            eid=r['enrollment_id']
            total=conn.execute("SELECT COUNT(*) as n FROM checkins WHERE enrollment_id=? AND is_counted=1",(eid,)).fetchone()['n']
            dates=conn.execute("SELECT date FROM checkins WHERE enrollment_id=? AND is_counted=1 ORDER BY date DESC",(eid,)).fetchall()
            streak=calculate_current_streak([x['date'] for x in dates],today)
            board.append({"name":r['name'],"username":r['username'],"enrollment_id":eid,"total_checkins":total,"current_streak":streak})
        board.sort(key=lambda x:(x['total_checkins'],x['current_streak']),reverse=True)
        return {"ok":True,"overall":board,"today":[]},200
    finally: conn.close()