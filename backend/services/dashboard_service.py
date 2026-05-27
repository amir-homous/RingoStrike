from database import get_db_connection, get_user_by_id
from utils.date_utils import utc_today_iso
from services.stats_service import sync_user_stats


def get_me(claims):
    auth_method = claims.get('auth_method','telegram')
    if auth_method == 'local':
        user = get_user_by_id(claims['user_id'])
        if not user:
            return {"ok":False,"error":"user_not_found"},404
        return {"ok":True,"user_id":claims.get('user_id'),"username":user.get('username'),"name":user.get('name'),"email":user.get('email'),"auth_method":"local","registered":True},200
    return {"ok":True,"telegram_id":claims.get('telegram_id'),"user_id":claims.get('user_id'),"telegram_username":claims.get('telegram_username'),"first_name":claims.get('first_name'),"registered":claims.get('registered',False),"auth_method":"telegram"},200


def get_dashboard(user_id:int):
    today = utc_today_iso(); sync_user_stats(user_id)
    conn=get_db_connection()
    try:
        user_info=conn.execute("SELECT u.name, u.username, CAST(IFNULL(s.total_points,0) AS INTEGER) as total_points, CAST(IFNULL(s.current_streak,0) AS INTEGER) as current_streak, CAST(IFNULL(s.longest_streak,0) AS INTEGER) as longest_streak FROM users u LEFT JOIN user_stats s ON u.id=s.user_id WHERE u.id=?",(user_id,)).fetchone()
        if not user_info: return {"ok":False,"error":"user_not_found"},404
        rows=conn.execute("SELECT e.id AS enrollment_id,c.name AS enrollment_name,e.status AS status,c.id AS challenge_id FROM enrollments e JOIN challenges c ON e.challenge_id=c.id WHERE e.user_id=? AND e.status='Active'",(user_id,)).fetchall()
        items=[]
        for r in rows:
            checkin=conn.execute("SELECT 1 FROM checkins WHERE enrollment_id=? AND date=? AND status='Done' LIMIT 1",(r['enrollment_id'],today)).fetchone()
            items.append({"enrollment_id":r['enrollment_id'],"enrollment_name":r['enrollment_name'],"status":r['status'],"challenge_id":r['challenge_id'],"today_checked":bool(checkin)})
        return {"ok":True,"date":today,"user":{"name":user_info['name'],"stats":{"total_points":user_info['total_points'],"current_streak":user_info['current_streak'],"longest_streak":user_info['longest_streak']}},"challenges":items},200
    finally: conn.close()

def _level_bundle(total_points: int) -> dict:
    level = max(1, (total_points // 100) + 1)
    level_floor = (level - 1) * 100
    next_level_xp = level * 100
    xp = max(0, total_points - level_floor)
    progress_percent = int((xp / 100) * 100) if 100 else 0
    return {"level": level, "next_level_xp": next_level_xp, "xp": xp, "progress_percent": progress_percent}


def get_stats(user_id:int):
    sync = sync_user_stats(user_id)
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT id, name FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            return {"ok": False, "error": "user_not_found"}, 404

        total_points = int(sync.get("total_points", 0))
        levels = _level_bundle(total_points)

        stats = {
            "current_streak": int(sync.get("current_streak", 0)),
            "level": levels["level"],
            "longest_streak": int(sync.get("longest_streak", 0)),
            "next_level_xp": levels["next_level_xp"],
            "progress_percent": levels["progress_percent"],
            "total_checkins": int(sync.get("total_checkins", 0)),
            "total_points": total_points,
            "xp": levels["xp"],
        }
        return {"ok": True, "stats": stats, "user": {"id": int(user["id"]), "name": user["name"]}}, 200
    finally:
        conn.close()
