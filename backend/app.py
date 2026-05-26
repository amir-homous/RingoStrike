from functools import wraps
import os
from urllib.parse import quote
from flask_cors import CORS
from flask import g,Flask, request,redirect, jsonify, render_template_string,render_template, make_response
from datetime import datetime as dt, timedelta, timezone
import jwt
import requests
from auth_telegram import verify_telegram_login
from config import Config
from notion_client import NotionClient
from auth_telegram import verify_telegram_login
from dotenv import load_dotenv
import sqlite3
from database import get_user_challenges , get_db_connection
from database import init_db
from datetime import datetime, timedelta, timezone

from auth import register_auth_routes, require_auth, make_jwt

load_dotenv()


app = Flask(__name__)
app.config.from_object(Config)

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:4173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:4173",
        ]
    }
})


# ✅ NOW YOUR OTHER ROUTES FOLLOW BELOW
@app.get("/health")
def health():
    return {"ok": True}


# --- توابع Helper جدید (جایگزین notion_*) ---
def get_db():
    """اتصال به دیتابیس در هر درخواست (Request Context)"""
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.teardown_appcontext
def close_db(error):
    """بستن اتصال بعد از پایان درخواست"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize database
init_db()

# Register auth routes BEFORE other routes
register_auth_routes(app)



@app.get("/challenges/public")
def public_challenges():
    try:
        db = get_db()
        # استفاده از row_factory برای اینکه خروجی به صورت دیکشنری باشد (خوانا با نام ستون‌ها)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        # کوئری برای دریافت چالش‌های عمومی
        # فیلتر visibility مطابق ساختار جدول شما اعمال شده است
        query = "SELECT * FROM challenges WHERE visibility = 'Public' AND status = 'Active'"
        cursor.execute(query)
        rows = cursor.fetchall()

        items = []
        for row in rows:
            # مپ کردن ستون‌های دیتابیس به ساختاری که فرانت‌اِند انتظار دارد
            items.append({
                "challenge_id": row['id'],
                "name": row['name'],
                "visibility": row['visibility'],
                "status": row['status'],
                "description": row['description'],
                "duration_days": row['duration_days'],
                # اگر در فرانت به join_code هم نیاز داری می‌تونی اینجا اضافه‌اش کنی:
                # "join_code": row['join_code']
            })

        return jsonify({
            "ok": True, 
            "items": items
        })

    except Exception as e:
        # مدیریت خطا در صورت بروز مشکل در کوئری یا دیتابیس
        return jsonify({
            "ok": False, 
            "error": str(e)
        }), 500


def _iso_to_date(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()

def _date_to_iso(d):
    return d.isoformat()

def _calc_current_streak(checkin_dates_iso, today_iso: str) -> int:
    if not checkin_dates_iso:
        return 0

    s = set(checkin_dates_iso)
    today = _iso_to_date(today_iso)
    yesterday = today - timedelta(days=1)

    anchor = today if today_iso in s else yesterday
    if _date_to_iso(anchor) not in s:
        return 0

    streak = 0
    d = anchor
    while _date_to_iso(d) in s:
        streak += 1
        d = d - timedelta(days=1)
    return streak



@app.route("/challenges/<int:challenge_id>/join", methods=["POST"])
def join_challenge(challenge_id):
    claims = require_auth()
    
    # اینجا دیباگ رو اضافه کن
    print(f"DEBUG: Claims received: {claims}")
    
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
        
    if False: 
        print(f"DEBUG: User {claims.get('user_id')} failed registration check")
        return jsonify({"ok": False, "error": "not_registered"}), 403

    user_id = int(claims["user_id"])

    body = request.get_json(silent=True) or {}
    provided_code = str(body.get("join_code") or "").strip()

    conn = get_db_connection()
    try:
        # چالش رو از DB بخون
        ch = conn.execute(
            "SELECT id, name, visibility, join_code, status FROM challenges WHERE id = ?",
            (challenge_id,)
        ).fetchone()

        if not ch:
            return jsonify({"ok": False, "error": "challenge_not_found"}), 404

        # اگر Archived بود نذار عضو بشه (اختیاری ولی منطقی)
        if (ch["status"] or "Active") != "Active":
            return jsonify({"ok": False, "error": "challenge_inactive"}), 403

        visibility = (ch["visibility"] or "Private").strip()
        required_code = (ch["join_code"] or "").strip()

        if visibility == "Private":
            return jsonify({"ok": False, "error": "challenge_private"}), 403

        if visibility == "Invite-only":
            if not required_code:
                return jsonify({"ok": False, "error": "invite_only_not_configured"}), 403
            if not provided_code:
                return jsonify({"ok": False, "error": "join_code_required"}), 400
            if provided_code != required_code:
                return jsonify({"ok": False, "error": "invalid_join_code"}), 403

        # upsert enrollment:
        # تلاش برای INSERT؛ اگر قبلاً عضو بوده UNIQUE خطا میده و میریم existing رو برمی‌گردونیم
        try:
            cur = conn.execute(
                "INSERT INTO enrollments (user_id, challenge_id, status) VALUES (?, ?, 'Active')",
                (user_id, challenge_id)
            )
            conn.commit()
            enrollment_id = cur.lastrowid

            return jsonify({
                "ok": True,
                "mode": "created",
                "enrollment_id": enrollment_id,
                "challenge_id": challenge_id
            })
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT id, status FROM enrollments WHERE user_id = ? AND challenge_id = ?",
                (user_id, challenge_id)
            ).fetchone()

            # اگر قبلاً Left بوده، می‌تونی تصمیم بگیری reactivate کنی یا نه:
            if row and row["status"] == "Left":
                conn.execute(
                    "UPDATE enrollments SET status='Active' WHERE id=?",
                    (row["id"],)
                )
                conn.commit()
                return jsonify({
                    "ok": True,
                    "mode": "reactivated",
                    "enrollment_id": row["id"],
                    "challenge_id": challenge_id
                })

            return jsonify({
                "ok": True,
                "mode": "existing",
                "enrollment_id": row["id"] if row else None,
                "challenge_id": challenge_id
            })

    finally:
        conn.close()


def make_jwt(payload: dict):
    exp = dt.now(timezone.utc) + timedelta(days=7)
    payload = dict(payload)
    payload["exp"] = int(exp.timestamp())
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")

def require_auth():
    token = None

    # 1) Try Cookie first (HttpOnly)
    cookie_name = app.config.get("JWT_COOKIE_NAME", "ringo_token")
    token = request.cookies.get(cookie_name)

    # 2) Fallback to Authorization header Bearer
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token:
        return None

    try:
        claims = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
        return claims
    except Exception:
        return None


def set_auth_cookie(resp, token: str):
    cookie_name = app.config.get("JWT_COOKIE_NAME", "ringo_token")

    # Dev: localhost => secure False
    secure = (os.getenv("JWT_COOKIE_SECURE", "0") == "1")

    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    resp.set_cookie(
        cookie_name,
        token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=7 * 24 * 3600,
        path="/",
    )
    return resp


# این دکوراتور رو به این اسم تغییر بده:
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        claims = require_auth() # از همون تابع کمکی استفاده می‌کنه
        if not claims:
            return jsonify({"ok": False, "error": "unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper



@app.get("/me")
def me():
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    # For local auth users (from database.py)
    auth_method = claims.get("auth_method", "telegram")
    
    if auth_method == "local":
        from database import get_user_by_id
        user = get_user_by_id(claims["user_id"])
        if not user:
            return jsonify({"ok": False, "error": "user_not_found"}), 404
        
        return jsonify({
            "ok": True,
            "user_id": claims.get("user_id"),
            "username": user.get("username"),
            "name": user.get("name"),
            "email": user.get("email"),
            "auth_method": "local",
            "registered": True,
        })
    
    # For Telegram auth users (existing logic)
    return jsonify({
        "ok": True,
        "telegram_id": claims.get("telegram_id"),
        "user_id": claims.get("user_id"),
        "telegram_username": claims.get("telegram_username"),
        "first_name": claims.get("first_name"),
        "registered": claims.get("registered", False),
        "auth_method": "telegram"
    })

def update_user_stats_after_checkin(user_id):
    from datetime import datetime, timedelta, timezone
    import sqlite3
    
    conn = get_db_connection() 
    conn.row_factory = sqlite3.Row
    
    try:
        user_id = int(user_id)
        today = utc_today_iso() # استفاده از همون تابعی که لیدربورد استفاده می‌کنه

        # ۱. محاسبه کل چک‌این‌ها و امتیاز
        # نکته: امتیاز رو از کل چک‌این‌های کاربر می‌گیریم، نه فقط یک چالش
        points_row = conn.execute("""
            SELECT COUNT(*) as total FROM checkins 
            WHERE user_id = ? AND status = 'Done'
        """, (user_id,)).fetchone()
        
        total_checkins = int(points_row['total'] or 0)
        total_points = total_checkins * 10 

        # ۲. محاسبه استریک (دقیقاً مثل منطق لیدربورد)
        # تمام تاریخ‌های چک‌این کاربر رو به ترتیب نزولی می‌گیریم
        rows = conn.execute("""
            SELECT DISTINCT date FROM checkins 
            WHERE user_id = ? AND status = 'Done' 
            ORDER BY date DESC
        """, (user_id,)).fetchall()
        
        date_list = [r["date"] for r in rows]
        
        # استفاده از همون تابع کمکی که توی لیدربورد داری
        current_streak = _calc_current_streak(date_list, today)

        # ۳. پیدا کردن Longest Streak قدیمی برای مقایسه
        user_row = conn.execute("SELECT longest_streak FROM users WHERE id = ?", (user_id,)).fetchone()
        old_longest = int(user_row['longest_streak'] or 0) if user_row else 0
        new_longest = max(old_longest, current_streak)

        # ۴. حالا غول مرحله آخر: آپدیت کردن هر دو جدول که خیالت راحت باشه
        # آپدیت جدول users (منبع اصلی داشبورد)
        conn.execute("""
            UPDATE users 
            SET total_points = ?, current_streak = ?, longest_streak = ?
            WHERE id = ?
        """, (total_points, current_streak, new_longest, user_id))

        # آپدیت یا اینسرت در user_stats (برای اطمینان)
        conn.execute("""
            INSERT INTO user_stats (user_id, total_checkins, total_points, current_streak, longest_streak, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                total_checkins = excluded.total_checkins,
                total_points = excluded.total_points,
                current_streak = excluded.current_streak,
                longest_streak = excluded.longest_streak,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, total_checkins, total_points, current_streak, new_longest))
        
        conn.commit()
        print(f"✅ STATS SYNCED: User {user_id} | Streak: {current_streak} | Points: {total_points}")
        
    except Exception as e:
        print(f"❌ STATS ERROR: {str(e)}")
    finally:
        conn.close()





@app.get("/me/challenges")
def me_dashboard():
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    user_id = int(claims["user_id"])
    today = utc_today_iso()
    
    # همگام‌سازی لحظه‌ای قبل از نمایش
    update_user_stats_after_checkin(user_id)

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    
    try:
        # تغییر در کوئری داشبورد برای خواندن از user_stats
        user_info = conn.execute("""
            SELECT 
                u.name, 
                u.username, 
                CAST(IFNULL(s.total_points, 0) AS INTEGER) as total_points, 
                CAST(IFNULL(s.current_streak, 0) AS INTEGER) as current_streak, 
                CAST(IFNULL(s.longest_streak, 0) AS INTEGER) as longest_streak 
            FROM users u
            LEFT JOIN user_stats s ON u.id = s.user_id
            WHERE u.id = ?
        """, (user_id,)).fetchone()

        if not user_info:
            return jsonify({"ok": False, "error": "user_not_found"}), 404

        # دریافت لیست چالش‌ها و وضعیت چک‌این امروز
        rows = conn.execute("""
            SELECT 
                e.id AS enrollment_id,
                c.name AS enrollment_name,
                e.status AS status,
                c.id AS challenge_id
            FROM enrollments e
            JOIN challenges c ON e.challenge_id = c.id
            WHERE e.user_id = ? AND e.status = 'Active'
        """, (user_id,)).fetchall()

        challenge_items = []
        for r in rows:
            checkin = conn.execute("""
                SELECT 1 FROM checkins 
                WHERE enrollment_id = ? AND date = ? AND status = 'Done'
                LIMIT 1
            """, (r['enrollment_id'], today)).fetchone()
            
            challenge_items.append({
                "enrollment_id": r['enrollment_id'],
                "enrollment_name": r['enrollment_name'],
                "status": r['status'],
                "challenge_id": r['challenge_id'],
                "today_checked": bool(checkin)
            })

        return jsonify({
            "ok": True,
            "date": today,
            "user": {
                "name": user_info['name'],
                "stats": {
                    "total_points": user_info['total_points'],
                    "current_streak": user_info['current_streak'],
                    "longest_streak": user_info['longest_streak']
                }
            },
            "challenges": challenge_items
        })
    finally:
        conn.close()





# --- Endpointهای دیباگ (SQLite-only) ---
@app.get("/debug/sqlite/schema/<table>")
def debug_sqlite_schema(table):
    # محدود کردن جداول مجاز برای امنیت
    allowed = {"users", "challenges", "enrollments", "checkins", "user_stats", "sessions"}
    if table not in allowed:
        return jsonify({"ok": False, "error": "table_not_allowed"}), 400
    
    conn = get_db()
    # گرفتن اطلاعات ستون‌ها
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return jsonify({
        "ok": True, 
        "table": table, 
        "columns": [dict(c) for c in cols]
    })

@app.get("/debug/sqlite/counts")
def debug_sqlite_counts():
    conn = get_db()
    tables = ["users", "challenges", "enrollments", "checkins", "user_stats"]
    out = {}
    for t in tables:
        try:
            res = conn.execute(f"SELECT COUNT(*) as n FROM {t}").fetchone()
            out[t] = res["n"]
        except Exception as e:
            out[t] = str(e)
    return jsonify({"ok": True, "counts": out})



from datetime import datetime, timezone,timedelta

def utc_today_iso():
    return datetime.now(timezone.utc).date().isoformat()




@app.post("/me/challenges/<int:enrollment_id>/checkin")
def checkin(enrollment_id):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    user_id = int(claims["user_id"])
    date_iso = utc_today_iso()

    conn = get_db_connection() 
    conn.row_factory = sqlite3.Row

    try:
        # ۱. بررسی دسترسی کاربر به این ثبت‌نام
        enroll = conn.execute("SELECT id, challenge_id FROM enrollments WHERE id = ? AND user_id = ?", 
                              (enrollment_id, user_id)).fetchone()
        if not enroll:
            return jsonify({"ok": False, "error": "forbidden_enrollment"}), 403

        challenge_id = enroll["challenge_id"]

        # ۲. ثبت یا بروزرسانی چک‌این
        existing = conn.execute("SELECT id FROM checkins WHERE enrollment_id = ? AND date = ?", 
                                (enrollment_id, date_iso)).fetchone()

        if existing:
            conn.execute("UPDATE checkins SET status = 'Done' WHERE id = ?", (existing["id"],))
        else:
            conn.execute("""
                INSERT INTO checkins (enrollment_id, user_id, challenge_id, date, status, is_counted) 
                VALUES (?, ?, ?, ?, 'Done', 1)
            """, (enrollment_id, user_id, challenge_id, date_iso))

        # ۳. حیاتی: اول همین‌جا Commit کن که چک‌این قطعی بشه
        conn.commit()
        
        # ۴. حالا که مطمئنیم چک‌این ثبت شده، آمار رو بروزرسانی کن
        # نکته: تابع رو همین‌جا صدا می‌زنیم
        update_user_stats_after_checkin(user_id)
        
        return jsonify({"ok": True, "message": "Check-in recorded"})

    except Exception as e:
        print(f"❌ Checkin Error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        # کانکشن حتماً در آخر بسته بشه
        conn.close()



from database import get_db_conn, get_user_enrollments,update_user_stats_after_checkin

@app.get("/challenges")
def list_challenges():
    claims = require_auth()
    if not claims: return jsonify({"ok": False, "error": "unauthorized"}), 401
    
    user_id = claims["user_id"]
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    
    # ۱. فقط چالش‌هایی را بیاور که Active هستند
    # و یا Public/Invite-only هستند، یا اگر Private هستند کاربر قبلاً عضو شده باشد
    challenges = conn.execute("""
        SELECT c.* FROM challenges c
        LEFT JOIN enrollments e ON c.id = e.challenge_id AND e.user_id = ?
        WHERE c.status = 'Active' 
        AND (c.visibility IN ('Public', 'Invite-only') OR e.id IS NOT NULL)
    """, (user_id,)).fetchall()
    
    enrollments = conn.execute(
        "SELECT id, challenge_id FROM enrollments WHERE user_id = ?", 
        (user_id,)
    ).fetchall()
    enroll_map = {e['challenge_id']: e['id'] for e in enrollments}
    
    items = []
    for ch in challenges:
        ch_id = ch['id']
        enroll_id = enroll_map.get(ch_id)
        vis_lower = ch['visibility'].lower()
        
        members_count = conn.execute(
            "SELECT COUNT(*) as n FROM enrollments WHERE challenge_id = ? AND status = 'Active'", 
            (ch_id,)
        ).fetchone()['n']

        # داخل حلقه for ch in challenges:
        previews = conn.execute("""
            SELECT u.name FROM users u
            JOIN enrollments e ON u.id = e.user_id
            WHERE e.challenge_id = ? AND e.status = 'Active'
            LIMIT 3
        """, (ch_id,)).fetchall()
        
        members_preview = [p['name'] for p in previews]

        
        items.append({
            "challenge_id": ch_id,
            "name": ch['name'],
            "description": ch['description'],
            "visibility": vis_lower,
            "status": ch['status'].lower(),
            "duration_days": ch['duration_days'],
            "members_count": members_count,
            "members_preview": members_preview,
            "is_joined": enroll_id is not None,
            "enrollment_id": enroll_id,
            # اصلاح شرط: هم برای private و هم برای invite-only باکس کد نشان داده شود
            "needs_code": vis_lower in ['private', 'invite-only']
        })

        
    conn.close()
    return jsonify({"ok": True, "items": items})



def notion_multi_select(props: dict, key: str) -> list[str]:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return []
    arr = obj.get("multi_select", [])
    if not isinstance(arr, list):
        return []
    out = []
    for x in arr:
        if isinstance(x, dict) and x.get("name"):
            out.append(x["name"])
    return out


@app.get("/challenges/<int:challenge_id>")
def challenge_detail(challenge_id):
    try:
        db = get_db()
        db.row_factory = sqlite3.Row  # اطمینان از دسترسی دیکشنری‌مانند
        
        # ۱. دریافت اطلاعات چالش
        row = db.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,)).fetchone()
        
        if row is None:
            return jsonify({"ok": False, "error": f"Challenge with ID {challenge_id} not found"}), 404

        # ۲. محاسبه تعداد واقعی شرکت‌کنندگان (اصلاح شد)
        # استفاده از fetchone()[0] برای گرفتن مقدار عددی مستقیم
        count_row = db.execute(
            "SELECT COUNT(*) FROM enrollments WHERE challenge_id = ? AND status = 'Active'",
            (challenge_id,)
        ).fetchone()
        members_count = count_row[0] if count_row else 0

        # ۳. پردازش تگ‌ها و آماده‌سازی خروجی
        # استفاده از dict(row) برای اطمینان از اینکه همه کلیدها درست مپ می‌شوند
        res = dict(row)
        
        tags_list = res.get('tags').split(',') if res.get('tags') else []

        return jsonify({
            "ok": True,
            "item": {
                "challenge_id": res['id'],
                "name": res['name'],
                "description": res.get('description', ''),
                "visibility": res.get('visibility', 'Public'),
                "status": res.get('status', 'Active'),
                "duration_days": res.get('duration_days', 0),
                "max_members": res.get('max_members', 0),
                "requires_proof": bool(res.get('requires_proof', 0)),
                "checkin_method": res.get('checkin_method', 'Manual'),
                "goal_type": res.get('goal_type', ''),
                "tags": tags_list,
                "members_count": members_count,
                "join_code_required": (res.get('visibility') == 'Invite-only' and bool(res.get('join_code')))
            }
        })

    except Exception as e:
        # چاپ خطا در کنسول اوبونتو برای دیباگ راحت‌تر تو
        print(f"Error in challenge_detail: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500




def safe_int(x, default=0):
    try:
        return int(str(x).strip())
    except:
        return default

def safe_bool(val) -> bool:
    s = str(val or "").strip().lower()
    return s in ("1", "true", "yes", "on")


# def compute_enrollment_stats(enrollment_id: str, daily_db_id: str):
#     """Recompute Total Check-ins + Current Streak from Daily Logs for THIS enrollment.

#     Streak rule:
#     - If today is checked → streak counts from today backward.
#     - Else if yesterday is checked → streak counts from yesterday backward.
#     - Else → streak = 0
#     """
#     payload = {
#         "filter": {
#             "and": [
#                 {"property": "Enrollment", "relation": {"contains": enrollment_id}},
#                 {"property": "Is Counted", "checkbox": {"equals": True}},
#             ]
#         },
#         "page_size": 100
#     }

#     pages = notion_query_all(daily_db_id, payload)

#     dates = set()
#     for page in pages:
#         props = page.get("properties", {}) or {}
#         d = (props.get("Date", {}) or {}).get("date", {})
#         d = d.get("start") if isinstance(d, dict) else None
#         if d:
#             dates.add(d)

#     total_checkins = len(dates)

#     today = dt.now(timezone.utc).date()
#     today_iso = today.isoformat()
#     yday_iso = (today - timedelta(days=1)).isoformat()

#     # choose start date for streak
#     if today_iso in dates:
#         cur = today
#     elif yday_iso in dates:
#         cur = today - timedelta(days=1)
#     else:
#         return total_checkins, 0

#     streak = 0
#     while True:
#         d = cur.isoformat()
#         if d in dates:
#             streak += 1
#             cur = cur - timedelta(days=1)
#         else:
#             break

#     return total_checkins, streak

# def compute_user_streaks(user_id: str, daily_db_id: str):
#     """
#     Current streak + Longest streak برای کاربر از روی Daily Logs
#     معیار: لاگ‌هایی که Is Counted = True و Users relation شامل user_id باشد.
#     """
#     payload = {
#         "filter": {
#             "and": [
#                 {"property": "Users", "relation": {"contains": user_id}},
#                 {"property": "Is Counted", "checkbox": {"equals": True}},
#             ]
#         },
#         "page_size": 100
#     }

#     pages = notion_query_all(daily_db_id, payload)

#     dates = set()
#     for page in pages:
#         props = page.get("properties", {}) or {}
#         d = (props.get("Date", {}) or {}).get("date", {})
#         d = d.get("start") if isinstance(d, dict) else None
#         if d:
#             dates.add(d)

#     # Current streak از امروز به عقب (UTC)
#     cur = dt.now(timezone.utc).date()
#     current = 0
#     while True:
#         ds = cur.isoformat()
#         if ds in dates:
#             current += 1
#             cur = cur - timedelta(days=1)
#         else:
#             break

#     # Longest streak: با اسکن تاریخ‌های مرتب شده
#     if not dates:
#         return 0, 0

#     sorted_days = sorted(dates)  # ISO => sortable
#     longest = 1
#     run = 1
#     prev = dt.fromisoformat(sorted_days[0]).date()

#     for s in sorted_days[1:]:
#         d = dt.fromisoformat(s).date()
#         if (d - prev).days == 1:
#             run += 1
#             longest = max(longest, run)
#         else:
#             run = 1
#         prev = d

#     return current, longest


@app.get("/challenges/<int:challenge_id>/members")
def challenge_members(challenge_id):
    try:
        db = get_db()
        db.row_factory = sqlite3.Row
        
        limit = safe_int(request.args.get("limit"), 20)
        limit = max(1, min(limit, 50))
        offset = safe_int(request.args.get("offset"), 0)

        # کوئری را به شکلی می‌نویسیم که ستون‌ها را دقیق پیدا کند
        query = """
            SELECT 
                enrollments.id,
                enrollments.status,
                enrollments.role,
                users.id AS u_id,
                users.name,
                users.username
            FROM enrollments
            JOIN users ON enrollments.user_id = users.id
            WHERE enrollments.challenge_id = ? AND enrollments.status = 'Active'
            LIMIT ? OFFSET ?
        """
        
        rows = db.execute(query, (challenge_id, limit, offset)).fetchall()

        items = []
        for row in rows:
            # استفاده از .get() یا چک کردن ستون برای جلوگیری از خطای Key Error
            items.append({
                "enrollment_id": row[0],
                "enrollment_status": row[1],
                "role": row[2] if len(row) > 2 else "Member",
                "user_id": row['u_id'],
                "user_name": row['name'],
                "telegram_username": row['username']
            })

        return jsonify({
            "ok": True,
            "challenge_id": challenge_id,
            "items": items,
            "has_more": len(items) == limit
        })

    except Exception as e:
        # اگر خطا "no such column" بود، راهنمایی چاپ کن
        if "no such column" in str(e):
            print("--- WARNING: Your database is out of date. Delete the .db file or run ALTER TABLE. ---")
        return jsonify({"ok": False, "error": str(e)}), 500




def date_range_days(days: int):
    # returns list of iso dates from (today-days+1) ... today
    today = dt.now(timezone.utc).date()
    out = []
    for i in range(days):
        d = today - timedelta(days=(days - 1 - i))
        out.append(d.isoformat())
    return out


@app.get("/me/challenges/<int:enrollment_id>/history")
def enrollment_history(enrollment_id):
    claims = require_auth()
    if not claims: return jsonify({"ok": False, "error": "unauthorized"}), 401
    
    user_id = claims["user_id"]
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    # ۱. احراز هویت (مطمئن شو این enrollment مال همین کاربره)
    enroll = conn.execute(
        "SELECT * FROM enrollments WHERE id = ? AND user_id = ?", 
        (enrollment_id, user_id)
    ).fetchone()
    
    if not enroll:
        conn.close()
        return jsonify({"ok": False, "error": "forbidden_enrollment"}), 403

    # ۲. گرفتن پارامتر روزها
    days = safe_int(request.args.get("days"), 30)
    days = max(1, min(days, 120))

    # محاسبه بازه زمانی
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days - 1)
    
    # ۳. گرفتن چک‌این‌های کاربر در این بازه از دیتابیس
    # فرض: جدول checkins داری با ستون‌های date (فرمت YYYY-MM-DD) و status
    logs = conn.execute("""
        SELECT date, status 
        FROM checkins 
        WHERE enrollment_id = ? AND date BETWEEN ? AND ?
    """, (enrollment_id, start_date.isoformat(), end_date.isoformat())).fetchall()
    
    by_date = {row['date']: row['status'] for row in logs}
    conn.close()

    # ۴. ساخت تایم‌لاین (مثل قبل)
    timeline = []
    checked_days = 0
    
    for i in range(days):
        current_date = (start_date + timedelta(days=i)).isoformat()
        status = by_date.get(current_date)
        
        if status:
            checked_days += 1
        
        timeline.append({
            "date": current_date,
            "status": status,
            "is_counted": True if status else False
        })

    return jsonify({
        "ok": True,
        "summary": {
            "checked_days": checked_days,
            "total_days": days
        },
        "items": timeline
    })


@app.get("/me/enrollments/<int:enrollment_id>")
def me_enrollment_detail(enrollment_id: int):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    user_id = claims["user_id"]
    today = utc_today_iso()

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    try:
        # 1) enrollment + challenge (مالکیت هم اینجا چک میشه)
        row = conn.execute("""
            SELECT
                e.id              AS enrollment_id,
                e.user_id         AS user_id,
                e.challenge_id    AS challenge_id,
                e.status          AS status,
                c.name            AS challenge_name,
                c.description     AS challenge_description,
                c.duration_days   AS duration_days
            FROM enrollments e
            JOIN challenges c ON c.id = e.challenge_id
            WHERE e.id = ? AND e.user_id = ?
            LIMIT 1
        """, (enrollment_id, user_id)).fetchone()

        if not row:
            return jsonify({"ok": False, "error": "enrollment_not_found"}), 404

        challenge_id = row["challenge_id"]

        # 2) today_checked
        today_checked = conn.execute("""
            SELECT 1
            FROM checkins
            WHERE enrollment_id = ? AND date = ?
            LIMIT 1
        """, (enrollment_id, today)).fetchone() is not None

        # 3) total_checkins
        total_checkins = conn.execute("""
            SELECT COUNT(*) AS n
            FROM checkins
            WHERE enrollment_id = ?
        """, (enrollment_id,)).fetchone()["n"]

        # 4) current_streak (از روی تاریخ‌های checkin)
        dates = conn.execute("""
            SELECT date
            FROM checkins
            WHERE enrollment_id = ?
            GROUP BY date
            ORDER BY date DESC
        """, (enrollment_id,)).fetchall()
        date_list = [r["date"] for r in dates if r["date"]]
        current_streak = _calc_current_streak(date_list, today)

        # 5) recent_logs (آخرین 20 روز ثبت‌شده)
        logs = conn.execute("""
            SELECT id AS daily_log_id, date
            FROM checkins
            WHERE enrollment_id = ?
            ORDER BY date DESC, id DESC
            LIMIT 20
        """, (enrollment_id,)).fetchall()

        recent_logs = [{"daily_log_id": r["daily_log_id"], "date": r["date"]} for r in logs]

        enrollment = {
            "enrollment_id": row["enrollment_id"],
            # Vue تو enrollment.name می‌خونه، پس name رو ست می‌کنیم:
            "name": row["challenge_name"],
            "status": row["status"],
            "challenge_id": row["challenge_id"],
            "today_checked": bool(today_checked),
            "total_checkins": int(total_checkins),
            "current_streak": int(current_streak),
        }

        challenge = {
            "id": challenge_id,
            "name": row["challenge_name"],
            "description": row["challenge_description"],
            "duration_days": row["duration_days"],
        }

        return jsonify({
            "ok": True,
            "enrollment": enrollment,
            "challenge": challenge,
            "recent_logs": recent_logs,
        })

    finally:
        conn.close()

@app.get("/me/enrollments/<int:enrollment_id>/leaderboard")
def enrollment_leaderboard(enrollment_id):
    claims = require_auth()
    if not claims: return jsonify({"ok": False, "error": "unauthorized"}), 401
    
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    try:
        # ۱. پیدا کردن challenge_id
        enroll = conn.execute("SELECT challenge_id FROM enrollments WHERE id = ?", (enrollment_id,)).fetchone()
        if not enroll: return jsonify({"ok": False, "error": "not_found"}), 404
        challenge_id = enroll["challenge_id"]
        
        # ۲. گرفتن همه اعضای چالش
        rows = conn.execute("""
            SELECT e.id as enrollment_id, u.name, u.username
            FROM enrollments e
            JOIN users u ON e.user_id = u.id
            WHERE e.challenge_id = ? AND e.status = 'Active'
        """, (challenge_id,)).fetchall()

        today = utc_today_iso()
        leaderboard = []

        for row in rows:
            eid = row["enrollment_id"]
            
            # محاسبه total
            total = conn.execute("SELECT COUNT(*) as n FROM checkins WHERE enrollment_id = ? AND is_counted = 1", (eid,)).fetchone()["n"]
            
            # محاسبه استریک (برای هر کاربر)
            dates = conn.execute("SELECT date FROM checkins WHERE enrollment_id = ? AND is_counted = 1 ORDER BY date DESC", (eid,)).fetchall()
            date_list = [r["date"] for r in dates]
            streak = _calc_current_streak(date_list, today) # از همان تابع کمکی بالا استفاده کن
            
            leaderboard.append({
                "name": row["name"],
                "username": row["username"],
                "enrollment_id": eid,
                "total_checkins": total,
                "current_streak": streak
            })
        
        # مرتب‌سازی بر اساس total_checkins (و سپس streak)
        leaderboard.sort(key=lambda x: (x["total_checkins"], x["current_streak"]), reverse=True)
        
        return jsonify({"ok": True, "overall": leaderboard, "today": []})
        
    finally:
        conn.close()




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
