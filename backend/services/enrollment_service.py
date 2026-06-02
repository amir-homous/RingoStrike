from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.stats_service import sync_user_stats
from services.achievement_service import evaluate_and_unlock


def checkin(user_id:int,enrollment_id:int):
    date_iso=utc_today_iso(); conn=get_db_connection()
    try:
        enroll=conn.execute("SELECT id, challenge_id, status FROM enrollments WHERE id=? AND user_id=?",(enrollment_id,user_id)).fetchone()
        if not enroll: return {"ok":False,"error":"forbidden_enrollment"},403
        if (enroll["status"] or "") != "Active": return {"ok":False,"error":"enrollment_inactive"},403
        ex=conn.execute("SELECT id FROM checkins WHERE enrollment_id=? AND date=?",(enrollment_id,date_iso)).fetchone()
        if ex: conn.execute("UPDATE checkins SET status='Done', is_counted=1 WHERE id=?",(ex['id'],))
        else: conn.execute("INSERT INTO checkins (enrollment_id, user_id, challenge_id, date, status, is_counted) VALUES (?, ?, ?, ?, 'Done', 1)",(enrollment_id,user_id,enroll['challenge_id'],date_iso))
        conn.commit()
    finally:
        conn.close()

    sync_user_stats(user_id)
    achievement_result = evaluate_and_unlock(user_id)
    sync = sync_user_stats(user_id)
    return {
        "ok": True,
        "message": "Check-in recorded",
        "rewards": {
            "xp_total": int(sync.get("total_points", 0)),
            "achievements": achievement_result.get("newly_unlocked", []),
            "achievement_xp_reward": int(achievement_result.get("xp_reward_total", 0)),
        },
    },200
