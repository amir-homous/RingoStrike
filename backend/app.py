import os
from urllib.parse import quote
from flask_cors import CORS
from flask import Flask, request,redirect, jsonify, render_template_string,render_template, make_response
from datetime import datetime as dt, timedelta, timezone
import jwt
import requests
from auth_telegram import verify_telegram_login
from config import Config
from notion_client import NotionClient
from auth_telegram import verify_telegram_login


from dotenv import load_dotenv
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

notion = NotionClient(app.config["NOTION_TOKEN"])

# -----------------------------
# Helpers to read Notion props
# -----------------------------
def notion_title(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "title":
        arr = obj.get("title", [])
        if isinstance(arr, list):
            return "".join([t.get("plain_text", "") for t in arr]).strip() or None
    return None

def notion_rich_text(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "rich_text":
        arr = obj.get("rich_text", [])
        if isinstance(arr, list):
            return "".join([t.get("plain_text", "") for t in arr]).strip() or None
    return None

def notion_select(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    sel = obj.get("select")
    if isinstance(sel, dict):
        return sel.get("name")
    return None

def notion_number(props: dict, key: str) -> float | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    num = obj.get("number")
    if isinstance(num, (int, float)):
        return float(num)
    return None

def notion_status(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    st = obj.get("status")
    if isinstance(st, dict):
        return st.get("name")
    return None


# -----------------------------
# Configurable property names
# -----------------------------
CHALLENGE_DB = "NOTION_CHALLENGES_DB_ID"
ENROLL_DB = "NOTION_ENROLLMENTS_DB_ID"

# Challenges DB properties (adjust if your names differ)
CH_NAME_PROP = "Name"               # title
CH_VISIBILITY_PROP = "Visibility"   # select: Private/Invite-only/Public
CH_STATUS_PROP = "Status"           # select (optional): Active/Archived
CH_DESC_PROP = "Description"        # rich_text (optional)
CH_DURATION_PROP = "Duration (days)"  # number (optional)
CH_JOIN_CODE_PROP = "Join Code"     # rich_text (optional) for Invite-only

# Enrollments DB properties (you already have these)
EN_USERS_REL_PROP = "Users"         # relation
EN_CHALLENGE_REL_PROP = "Challenges" # relation
EN_STATUS_PROP = "Status"           # select: Active/Inactive/...
EN_ROLE_PROP = "Role"               # select (optional)
EN_JOIN_DATE_PROP = "Join Date"     # date (optional)


@app.get("/challenges/public")
def public_challenges():
    ch_db = app.config.get(CHALLENGE_DB)
    if not ch_db:
        return jsonify({"ok": False, "error": f"{CHALLENGE_DB} missing in .env"}), 500

    # Only Public challenges
    payload = {
        "filter": {
            "property": CH_VISIBILITY_PROP,
            "select": {"equals": "Public"}
        }
    }

    res = notion.query_db(ch_db, payload)
    results = res.get("results", [])

    items = []
    for page in results:
        props = page.get("properties", {})

        name = notion_title(props, CH_NAME_PROP)
        visibility = notion_select(props, CH_VISIBILITY_PROP)
        status = notion_select(props, CH_STATUS_PROP) if CH_STATUS_PROP in props else None
        desc = notion_rich_text(props, CH_DESC_PROP) if CH_DESC_PROP in props else None
        duration_days = notion_number(props, CH_DURATION_PROP) if CH_DURATION_PROP in props else None

        items.append({
            "challenge_id": page.get("id"),
            "name": name,
            "visibility": visibility,
            "status": status,
            "description": desc,
            "duration_days": duration_days,
        })

    return jsonify({"ok": True, "items": items})


@app.post("/challenges/<challenge_id>/join")
def join_challenge(challenge_id):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    user_id = claims["user_id"]

    enroll_db = app.config.get(ENROLL_DB)
    if not enroll_db:
        return jsonify({"ok": False, "error": f"{ENROLL_DB} missing in .env"}), 500

    # Challenge رو بخونیم
    ch_page = get_page(challenge_id)
    ch_props = ch_page.get("properties", {}) or {}

    visibility = notion_select(ch_props, CH_VISIBILITY_PROP) or "Private"
    required_code = (notion_rich_text(ch_props, CH_JOIN_CODE_PROP) or "").strip()

    if visibility == "Private":
        return jsonify({"ok": False, "error": "challenge_private"}), 403

    body = request.get_json(silent=True) or {}
    provided_code = str(body.get("join_code") or "").strip()

    if visibility == "Invite-only":
        if not required_code:
            return jsonify({"ok": False, "error": "invite_only_not_configured"}), 403
        if not provided_code:
            return jsonify({"ok": False, "error": "join_code_required"}), 400
        if provided_code != required_code:
            return jsonify({"ok": False, "error": "invalid_join_code"}), 403

    # Upsert Enrollment (اگر قبلاً عضو شده، دوباره نساز)
    find_payload = {
        "filter": {
            "and": [
                {"property": "Users", "relation": {"contains": user_id}},
                {"property": "Challenges", "relation": {"contains": challenge_id}},
            ]
        },
        "page_size": 1
    }
    existing = notion.query_db(enroll_db, find_payload).get("results", [])
    if existing:
        return jsonify({"ok": True, "mode": "existing", "enrollment_id": existing[0]["id"]})

    # Enrollment Name
    ch_name = notion_title(ch_props, CH_NAME_PROP) or "Challenge"
    title_text = f"{claims.get('telegram_username') or 'user'} in {ch_name}"

    create_props = {
        "Name": {"title": [{"text": {"content": title_text}}]},
        "Users": {"relation": [{"id": user_id}]},
        "Challenges": {"relation": [{"id": challenge_id}]},
        "Status": {"select": {"name": "Active"}},  # تو Enrollments معمولاً select هست
    }

    created = notion.create_page(enroll_db, create_props)
    return jsonify({"ok": True, "mode": "created", "enrollment_id": created["id"], "challenge_id": challenge_id})

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

@app.get("/health")
def health():
    return {"ok": True}

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
NOTION_TELEGRAM_PROP = os.getenv("NOTION_TELEGRAM_PROP", "telegramId").strip()

def find_user_by_telegram_id(telegram_id: str):
    users_db = app.config.get("NOTION_USERS_DB_ID")
    if not users_db:
        return None

    prop = os.getenv("NOTION_TELEGRAM_PROP", "Telegram ID").strip()

    payload = {
        "filter": {
            "property": prop,
            "rich_text": {"equals": str(telegram_id)}
        },
        "page_size": 1
    }

    res = notion.query_db(users_db, payload)
    results = res.get("results") or []
    return results[0] if results else None

def create_user_in_notion(telegram_id: str, username: str | None, first_name: str | None, last_name: str | None):
    users_db = app.config.get("NOTION_USERS_DB_ID")
    if not users_db:
        return None

    display_name = " ".join([x for x in [first_name, username] if x]) or f"tg:{telegram_id}"

    props = {
        "Name": {"title": [{"text": {"content": display_name}}]},
        "Telegram ID": {"rich_text": [{"text": {"content": str(telegram_id)}}]},
    }

    # اینا تو schema تو هست، safe هستن (rich_text)
    if username:
        props["Telegram Username"] = {"rich_text": [{"text": {"content": username}}]}
    if first_name or last_name:
        full = " ".join([x for x in [first_name, last_name] if x]).strip()
        if full:
            props["Notes"] = {"rich_text": [{"text": {"content": f"Full name: {full}"}}]}

    # Joined At (date) هم تو schema هست
    props["Joined At"] = {"date": {"start": dt.now(timezone.utc).date().isoformat()}}

    created = notion.create_page(users_db, props)
    return created

@app.route("/auth/telegram", methods=["GET"])
def auth_telegram():
    raw = request.args.to_dict(flat=True)

    # ✅ next را جدا کن تا وارد verify نشود
    nxt = raw.pop("next", "/ringostrike/dashboard")
    # ✅ normalize next to avoid /ringostrike/ringostrike
    if nxt.startswith("/ringostrike/"):
        nxt = nxt[len("/ringostrike"):]  # تبدیل میشه به /dashboard
    if nxt == "/ringostrike":
        nxt = "/"

    if not nxt.startswith("/"):
        nxt = "/ringostrike/dashboard"

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        return jsonify({"ok": False, "error": "bot_token_missing"}), 500

    # ✅ verify فقط با داده‌های تلگرام (بدون next)
    if not verify_telegram_login(raw, bot_token):
        return jsonify({"ok": False, "error": "telegram_verify_failed"}), 400

    telegram_id = str(raw.get("id") or "").strip()
    telegram_username = (raw.get("username") or "").strip() or None
    first_name = (raw.get("first_name") or "").strip() or None
    last_name = (raw.get("last_name") or "").strip() or None

    user_page = find_user_by_telegram_id(telegram_id)

    if not user_page:
        user_page = create_user_in_notion(
            telegram_id=telegram_id,
            username=telegram_username,
            first_name=first_name,
            last_name=last_name,
        )

    registered = bool(user_page)
    user_id = user_page["id"] if user_page else None

    claims = {
        "telegram_id": telegram_id,
        "telegram_username": telegram_username,
        "first_name": first_name,
        "last_name": last_name,
        "registered": registered,
        "user_id": user_id,
    }

    token = make_jwt(claims)

    resp = redirect(f"{FRONTEND_BASE_URL}{nxt}")

    cookie_name = os.getenv("JWT_COOKIE_NAME", "ringo_token")
    secure_cookie = (os.getenv("JWT_COOKIE_SECURE", "1") == "1")
    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    resp.set_cookie(
        cookie_name,
        token,
        httponly=True,
        secure=secure_cookie,
        samesite=samesite,
        max_age=7 * 24 * 3600,
        path="/",
    )
    return resp

@app.post("/logout")
def logout():
    resp = make_response(jsonify({"ok": True}), 200)

    cookie_name = app.config.get("JWT_COOKIE_NAME", "ringo_token")

    secure_cookie = (os.getenv("JWT_COOKIE_SECURE", "1") == "1")
    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    # ✅ پاک کردن قطعی کوکی (با همان policy)
    resp.set_cookie(
        cookie_name,
        "",
        max_age=0,
        expires=0,
        httponly=True,
        secure=secure_cookie,
        samesite=samesite,
        path="/",
    )
    return resp


@app.get("/me")
def me():
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    return jsonify({
        "ok": True,
        "telegram_id": claims.get("telegram_id"),
        "user_id": claims.get("user_id"),
        "registered": claims.get("registered", False),
    })

@app.get("/me/challenges")
def my_challenges():

    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": True, "items": [], "note": "user_not_registered_in_notion"}), 200

    user_id = claims["user_id"]
    enroll_db = app.config["NOTION_ENROLLMENTS_DB_ID"]

    USER_REL_PROP = "Users"
    CHALLENGE_REL_PROP = "Challenges"
    STATUS_PROP = "Status"

    # ✅ فیلتر فقط Active
    payload = {
        "filter": {
            "and": [
                {"property": USER_REL_PROP, "relation": {"contains": user_id}},
                {"property": STATUS_PROP, "select": {"equals": "Active"}},
            ]
        }
    }

    res = notion.query_db(enroll_db, payload)
    results = res.get("results", [])

    items = []
    for page in results:
        props = page.get("properties", {})

        # status
        status_name = None
        status_obj = props.get(STATUS_PROP, {})
        if isinstance(status_obj, dict):
            sel = status_obj.get("select")
            if isinstance(sel, dict):
                status_name = sel.get("name")

        # Enrollment title (Name)
        enrollment_name = None
        name_obj = props.get("Name", {})
        if isinstance(name_obj, dict) and name_obj.get("type") == "title":
            arr = name_obj.get("title", [])
            if isinstance(arr, list):
                enrollment_name = "".join([t.get("plain_text", "") for t in arr]).strip()

        # relation ids (Challenges)
        challenge_ids = []
        rel_obj = props.get(CHALLENGE_REL_PROP, {})
        if isinstance(rel_obj, dict):
            rel = rel_obj.get("relation", [])
            if isinstance(rel, list):
                challenge_ids = [x.get("id") for x in rel if x.get("id")]

        # ✅ pick first challenge (برای MVP)
        challenge_id = challenge_ids[0] if challenge_ids else None
        challenge_name = None
        if challenge_id:
            try:
                challenge_name = fetch_page_title(challenge_id)
            except Exception:
                challenge_name = None

        items.append({
            "enrollment_id": page["id"],
            "enrollment_name": enrollment_name,
            "status": status_name,
            "challenge_id": challenge_id,
            "challenge_name": challenge_name,
        })

    return jsonify({"ok": True, "items": items})

@app.get("/debug/notion/users")
def debug_notion_users():
    users_db = app.config["NOTION_USERS_DB_ID"]
    payload = {"page_size": 3}
    res = notion.query_db(users_db, payload)
    return jsonify({
        "ok": True,
        "count": len(res.get("results", [])),
        "sample_ids": [p["id"] for p in res.get("results", [])]
    })

@app.get("/debug/notion/challenges/schema")
def debug_challenges_schema():
    db_id = app.config["NOTION_CHALLENGES_DB_ID"]
    url = f"https://api.notion.com/v1/databases/{db_id}"
    r = requests.get(url, headers=notion.headers, timeout=30)
    r.raise_for_status()
    return r.json()


BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "").strip()
PUBLIC_BASE = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

@app.get("/login")
def login():
    nxt = request.args.get("next", "/dashboard")
    auth_url = f"{PUBLIC_BASE}/auth/telegram?next={nxt}"
    return render_template("login.html", bot_username=BOT_USERNAME, auth_url=auth_url)

@app.get("/debug/env")
def debug_env():
    return {
        "has_notion_token": bool(app.config["NOTION_TOKEN"]),
        "has_users_db": bool(app.config["NOTION_USERS_DB_ID"]),
        "has_bot_token": bool(app.config["TELEGRAM_BOT_TOKEN"]),
        "bot_username": app.config["TELEGRAM_BOT_USERNAME"],
    }

@app.get("/debug/notion/users/schema")
def debug_users_schema():
    db_id = app.config["NOTION_USERS_DB_ID"]
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = notion.headers
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    # فقط properties رو برگردونیم که سبک باشه
    props = data.get("properties", {})
    # خروجی: اسم property -> type
    out = {name: props[name].get("type") for name in props.keys()}
    return jsonify({"ok": True, "properties": out})

@app.get("/debug/notion/enrollments/schema")
def debug_enrollments_schema():
    db_id = app.config["NOTION_ENROLLMENTS_DB_ID"]
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = notion.headers
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    props = data.get("properties", {})
    out = {name: props[name].get("type") for name in props.keys()}
    return jsonify({"ok": True, "properties": out})

def fetch_page_title(page_id: str) -> str | None:
    url = f"{notion.base}/pages/{page_id}"
    r = requests.get(url, headers=notion.headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    props = data.get("properties", {})
    for _, pobj in props.items():
        if pobj.get("type") == "title":
            arr = pobj.get("title", [])
            return "".join([t.get("plain_text","") for t in arr]).strip()
    return None

@app.get("/debug/notion/dailylogs/schema")
def debug_dailylogs_schema():
    db_id = app.config.get("NOTION_DAILY_LOGS_DB_ID")
    if not db_id:
        return jsonify({"ok": False, "error": "NOTION_DAILY_LOGS_DB_ID missing in .env"}), 400

    url = f"https://api.notion.com/v1/databases/{db_id}"
    r = requests.get(url, headers=notion.headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    props = data.get("properties", {})
    out = {name: props[name].get("type") for name in props.keys()}
    return jsonify({"ok": True, "properties": out})

def get_page(page_id: str):
    return notion.retrieve_page(page_id)


def enrollment_belongs_to_user(enrollment_page_id: str, user_page_id: str) -> bool:
    page = get_page(enrollment_page_id)
    props = page.get("properties", {})
    rel = props.get("Users", {}).get("relation", [])
    ids = [x.get("id") for x in rel if x.get("id")]
    return user_page_id in ids

def today_iso():
    return dt.now(timezone.utc).date().isoformat()

def notion_create_page(database_id: str, properties: dict):
    url = f"{notion.base}/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties,
    }
    r = requests.post(url, headers=notion.headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def notion_update_page(page_id: str, properties: dict):
    url = f"{notion.base}/pages/{page_id}"
    payload = {"properties": properties}
    r = requests.patch(url, headers=notion.headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def find_today_log(daily_db_id: str, enrollment_id: str, date_iso: str) -> str | None:
    payload = {
        "filter": {
            "and": [
                {"property": "Enrollment", "relation": {"contains": enrollment_id}},
                {"property": "Date", "date": {"equals": date_iso}},
            ]
        },
        "page_size": 1,
        "sorts": [
            {"property": "Check-in Time", "direction": "descending"}
        ]
    }
    res = notion.query_db(daily_db_id, payload)
    results = res.get("results", [])
    if not results:
        return None
    return results[0]["id"]

@app.post("/me/challenges/<enrollment_id>/checkin")
def checkin(enrollment_id):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    user_id = claims["user_id"]

    # ✅ validate enrollment belongs to user
    if not enrollment_belongs_to_user(enrollment_id, user_id):
        return jsonify({"ok": False, "error": "forbidden_enrollment"}), 403

    body = request.get_json(silent=True) or {}

    # اختیاری‌ها
    notes = (body.get("notes") or "").strip()
    status = str(body.get("status") or "Done").strip()
    source = str(body.get("source") or "Web App").strip()
    is_counted = bool(body.get("is_counted", True))
    telegram_msg_id = str(body.get("telegram_message_id") or "").strip()

    # DB
    daily_db = app.config["NOTION_DAILY_LOGS_DB_ID"]

    # --- helpers (local) ---
    def notion_update_page(page_id: str, properties: dict):
        url = f"{notion.base}/pages/{page_id}"
        payload = {"properties": properties}
        r = requests.patch(url, headers=notion.headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def find_today_log(daily_db_id: str, enrollment_page_id: str, date_iso: str) -> str | None:
        payload = {
            "filter": {
                "and": [
                    {"property": "Enrollment", "relation": {"contains": enrollment_page_id}},
                    {"property": "Date", "date": {"equals": date_iso}},
                ]
            },
            "page_size": 1,
            "sorts": [{"property": "Check-in Time", "direction": "descending"}]
        }
        res = notion.query_db(daily_db_id, payload)
        results = res.get("results", [])
        if not results:
            return None
        return results[0]["id"]

    def sync_user_stats(user_page_id: str):
        """
        Sync Current Streak + Longest Streak روی Users DB
        معیار: Daily Logs با Users relation شامل user_page_id و Is Counted = True
        """
        try:
            payload = {
                "filter": {
                    "and": [
                        {"property": "Users", "relation": {"contains": user_page_id}},
                        {"property": "Is Counted", "checkbox": {"equals": True}},
                    ]
                },
                "page_size": 100
            }

            # pagination-safe (اگر notion_query_all داری بهتره، ولی این هم برای MVP کافیه)
            res = notion.query_db(daily_db, payload)
            pages = res.get("results", []) or []

            dates = set()
            for page in pages:
                props = page.get("properties", {}) or {}
                d = (props.get("Date", {}) or {}).get("date", {})
                d = d.get("start") if isinstance(d, dict) else None
                if d:
                    dates.add(d)

            # current streak (UTC)
            from datetime import datetime as dt, timezone, timedelta
            cur = dt.now(timezone.utc).date()
            current = 0
            while True:
                ds = cur.isoformat()
                if ds in dates:
                    current += 1
                    cur = cur - timedelta(days=1)
                else:
                    break

            # longest streak
            if not dates:
                longest = 0
            else:
                from datetime import datetime as dt
                sorted_days = sorted(dates)
                longest = 1
                run = 1
                prev = dt.fromisoformat(sorted_days[0]).date()
                for s in sorted_days[1:]:
                    d = dt.fromisoformat(s).date()
                    if (d - prev).days == 1:
                        run += 1
                        longest = max(longest, run)
                    else:
                        run = 1
                    prev = d

            notion_update_page(enrollment_id, {
                "Total Check-ins": {"number": int(total_checkins)},
                "Current Streak in Challenge": {"number": int(current_streak)},
                "Progress %": {"number": float(progress_percent)},  # اگر درصد عددی داری
            })

            return {"current_streak": current, "longest_streak": longest}
        except Exception as ex:
            app.logger.exception("Failed syncing user stats: %s", ex)
            return None

    # Challenge ID را از خود enrollment درمیاریم
    enrollment_page = get_page(enrollment_id)
    eprops = enrollment_page.get("properties", {}) or {}
    challenge_rel = (eprops.get("Challenges", {}) or {}).get("relation", [])
    challenge_ids = [x.get("id") for x in challenge_rel if x.get("id")]
    challenge_id = challenge_ids[0] if challenge_ids else None

    # Title (Name) برای لاگ
    date_iso = today_iso()
    title_text = f"Check-in {date_iso}"

    # properties برای create/update
    props = {
        "Name": {"title": [{"text": {"content": title_text}}]},
        "Date": {"date": {"start": date_iso}},
        "Users": {"relation": [{"id": user_id}]},
        "Enrollment": {"relation": [{"id": enrollment_id}]},
        "Is Counted": {"checkbox": is_counted},
    }

    # وصل کردن challenge اگر داشت
    if challenge_id:
        props["Challenges"] = {"relation": [{"id": challenge_id}]}

    # Notes
    if notes:
        props["Notes"] = {"rich_text": [{"text": {"content": notes}}]}

    # Status
    if status:
        props["Status"] = {"select": {"name": status}}

    # Source
    if source:
        props["Source"] = {"select": {"name": source}}

    # Telegram message id (optional)
    if telegram_msg_id:
        props["Message ID (Telegram)"] = {"rich_text": [{"text": {"content": telegram_msg_id}}]}

    # ✅ UPSERT: اگر برای امروز موجود بود → update، نبود → create
    existing_log_id = find_today_log(daily_db, enrollment_id, date_iso)

    user_stats_synced = None

    if existing_log_id:
        updated = notion_update_page(existing_log_id, props)

        # ✅ بعد از update هم آمار enrollment رو دوباره محاسبه و sync می‌کنیم
        try:
            total_checkins, current_streak = compute_enrollment_stats(enrollment_id, daily_db)

            duration_days = None
            if challenge_id:
                ch_page = get_page(challenge_id)
                ch_props = ch_page.get("properties", {}) or {}
                duration_days = notion_number(ch_props, "Duration (days)")

            if duration_days and duration_days > 0:
                pct = round((total_checkins / duration_days) * 100)
                progress_text = f"{total_checkins}/{duration_days} ({pct}%)"
            else:
                progress_text = str(total_checkins)

            notion_update_page(enrollment_id, {
                "Total Check-ins": {"rich_text": [{"text": {"content": str(total_checkins)}}]},
                "Progress %": {"rich_text": [{"text": {"content": progress_text}}]},
                "Current Streak in Challenge": {"rich_text": [{"text": {"content": str(current_streak)}}]},
            })
        except Exception as ex:
            app.logger.exception("Failed updating enrollment stats (update mode): %s", ex)

        # ✅ Sync user streaks (Users DB)
        user_stats_synced = sync_user_stats(user_id)

        return jsonify({
            "ok": True,
            "mode": "updated",
            "daily_log_id": updated["id"],
            "enrollment_id": enrollment_id,
            "challenge_id": challenge_id,
            "date": date_iso,
            "status": status,
            "is_counted": is_counted,
            "user_stats": user_stats_synced,
        })

    created = notion_create_page(daily_db, props)

    # ✅ بعد از create هم آمار enrollment رو دوباره محاسبه و sync می‌کنیم
    try:
        total_checkins, current_streak = compute_enrollment_stats(enrollment_id, daily_db)

        duration_days = None
        if challenge_id:
            ch_page = get_page(challenge_id)
            ch_props = ch_page.get("properties", {}) or {}
            duration_days = notion_number(ch_props, "Duration (days)")

        if duration_days and duration_days > 0:
            pct = round((total_checkins / duration_days) * 100)
            progress_text = f"{total_checkins}/{duration_days} ({pct}%)"
        else:
            progress_text = str(total_checkins)

        notion_update_page(enrollment_id, {
            "Total Check-ins": {"rich_text": [{"text": {"content": str(total_checkins)}}]},
            "Progress %": {"rich_text": [{"text": {"content": progress_text}}]},
            "Current Streak in Challenge": {"rich_text": [{"text": {"content": str(current_streak)}}]},
        })
    except Exception as ex:
        app.logger.exception("Failed updating enrollment stats (create mode): %s", ex)

    # ✅ Sync user streaks (Users DB)
    user_stats_synced = sync_user_stats(user_id)

    return jsonify({
        "ok": True,
        "mode": "created",
        "daily_log_id": created["id"],
        "enrollment_id": enrollment_id,
        "challenge_id": challenge_id,
        "date": date_iso,
        "status": status,
        "is_counted": is_counted,
        "user_stats": user_stats_synced,
    })


@app.get("/debug/notion/schema/<db_key>")
def debug_notion_schema(db_key):
    # مثال: db_key = "users" یا "challenges" یا "enrollments" یا "daily_logs"
    mapping = {
        "users": "NOTION_USERS_DB_ID",
        "challenges": "NOTION_CHALLENGES_DB_ID",
        "enrollments": "NOTION_ENROLLMENTS_DB_ID",
        "daily_logs": "NOTION_DAILY_LOGS_DB_ID",
    }

    env_key = mapping.get(db_key)
    if not env_key:
        return jsonify({"ok": False, "error": "invalid_db_key"}), 400

    db_id = app.config.get(env_key)
    if not db_id:
        return jsonify({"ok": False, "error": f"{env_key} missing in .env"}), 500

    db = notion.retrieve_database(db_id)
    props = db.get("properties", {}) or {}

    simplified = {}
    for k, v in props.items():
        if isinstance(v, dict):
            simplified[k] = v.get("type")

    return jsonify({"ok": True, "db_key": db_key, "properties": simplified})

def notion_title_text(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "title":
        arr = obj.get("title", [])
        if isinstance(arr, list):
            return "".join([t.get("plain_text", "") for t in arr]).strip() or None
    return None

def notion_select_name(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    sel = obj.get("select")
    if isinstance(sel, dict):
        return sel.get("name")
    return None

def notion_title_text(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "title":
        arr = obj.get("title", [])
        if isinstance(arr, list):
            return "".join([t.get("plain_text", "") for t in arr]).strip() or None
    return None

def notion_rich_text(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "rich_text":
        arr = obj.get("rich_text", [])
        if isinstance(arr, list):
            return "".join([t.get("plain_text", "") for t in arr]).strip() or None
    return None

def notion_select_name(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    sel = obj.get("select")
    if isinstance(sel, dict):
        return sel.get("name")
    return None

def notion_number(props: dict, key: str) -> float | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    num = obj.get("number")
    if isinstance(num, (int, float)):
        return float(num)
    return None

def notion_status_name(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    st = obj.get("status")
    if isinstance(st, dict):
        return st.get("name")
    return None

def notion_date_start(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    dt = obj.get("date")
    if isinstance(dt, dict):
        return dt.get("start")
    return None

@app.get("/me/dashboard")
def me_dashboard():
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    user_id = claims["user_id"]

    users_db = app.config.get("NOTION_USERS_DB_ID")
    enroll_db = app.config.get("NOTION_ENROLLMENTS_DB_ID")
    daily_db = app.config.get("NOTION_DAILY_LOGS_DB_ID")

    if not users_db:
        return jsonify({"ok": False, "error": "NOTION_USERS_DB_ID missing in .env"}), 500
    if not enroll_db:
        return jsonify({"ok": False, "error": "NOTION_ENROLLMENTS_DB_ID missing in .env"}), 500
    if not daily_db:
        return jsonify({"ok": False, "error": "NOTION_DAILY_LOGS_DB_ID missing in .env"}), 500

    # -------------------------
    # 1) Get user page (minimal)
    # -------------------------
    user_page = get_page(user_id)
    uprops = user_page.get("properties", {}) or {}

    user_name = notion_title_text(uprops, "Name")
    total_points = notion_rich_text(uprops, "Total Points")
    current_streak = notion_rich_text(uprops, "Current Streak")
    longest_streak = notion_rich_text(uprops, "Longest Streak")

    # -------------------------
    # 2) Get enrollments of user
    #    (کم‌هزینه: فقط Relation filter)
    # -------------------------
    enroll_payload = {
        "filter": {
            "property": "Users",
            "relation": {"contains": user_id}
        },
        "page_size": 50  # اگر خیلی زیاد شد بعداً pagination می‌زنیم
    }
    enroll_res = notion.query_db(enroll_db, enroll_payload)
    enrollments = enroll_res.get("results", [])

    # فقط داده‌های ضروری هر enrollment
    enrollment_items = []
    enrollment_ids = set()

    for e in enrollments:
        eprops = e.get("properties", {}) or {}

        enrollment_id = e.get("id")
        enrollment_ids.add(enrollment_id)

        # Status (select)
        status_name = notion_select_name(eprops, "Status")

        # Enrollment title
        enrollment_name = notion_title_text(eprops, "Name")

        # Challenge relation id (اولی)
        challenge_id = None
        rel = eprops.get("Challenges", {}).get("relation", [])
        if isinstance(rel, list) and rel:
            challenge_id = rel[0].get("id")

        enrollment_items.append({
            "enrollment_id": enrollment_id,
            "enrollment_name": enrollment_name,
            "status": status_name,
            "challenge_id": challenge_id,
            # today_checked بعداً ست میشه
            "today_checked": False,
            "today_daily_log_id": None,
        })

    # -------------------------
    # 3) Get today's daily logs for user (ONE query)
    # -------------------------
    t = today_iso()

    daily_payload = {
        "filter": {
            "and": [
                {"property": "Users", "relation": {"contains": user_id}},
                {"property": "Date", "date": {"equals": t}},
            ]
        },
        "page_size": 100
    }
    daily_res = notion.query_db(daily_db, daily_payload)
    logs_today = daily_res.get("results", [])

    # Map enrollment_id -> daily_log_id (از روی relation Enrollment)
    today_map = {}
    for log in logs_today:
        lprops = log.get("properties", {}) or {}
        rel = lprops.get("Enrollment", {}).get("relation", [])
        if isinstance(rel, list) and rel:
            eid = rel[0].get("id")
            if eid:
                today_map[eid] = log.get("id")

    # apply today_map to enrollment_items
    for item in enrollment_items:
        eid = item["enrollment_id"]
        if eid in today_map:
            item["today_checked"] = True
            item["today_daily_log_id"] = today_map[eid]

    return jsonify({
        "ok": True,
        "date": t,
        "user": {
            "user_id": user_id,
            "name": user_name,
            "stats": {
                "total_points": total_points,
                "current_streak": current_streak,
                "longest_streak": longest_streak
            }
        },
        "challenges": enrollment_items
    })

@app.get("/challenges")
def list_challenges():
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    ch_db = app.config.get(CHALLENGE_DB)
    if not ch_db:
        return jsonify({"ok": False, "error": f"{CHALLENGE_DB} missing in .env"}), 500

    enroll_db = app.config.get(ENROLL_DB)
    if not enroll_db:
        return jsonify({"ok": False, "error": f"{ENROLL_DB} missing in .env"}), 500

    daily_db = app.config.get("NOTION_DAILY_LOGS_DB_ID")
    if not daily_db:
        return jsonify({"ok": False, "error": "NOTION_DAILY_LOGS_DB_ID missing in .env"}), 500

    user_id = claims["user_id"]

    # ===== 1) my enrollments => is_joined + enrollment_id
    my_enroll_payload = {
        "filter": {
            "and": [
                {"property": "Users", "relation": {"contains": user_id}},
                {"property": "Status", "select": {"equals": "Active"}},
            ]
        },
        "page_size": 200
    }
    my_enroll_res = notion.query_db(enroll_db, my_enroll_payload)
    my_enrollments = my_enroll_res.get("results", []) or []

    joined_map = {}  # challenge_id -> enrollment_id
    for en in my_enrollments:
        en_id = en.get("id")
        props = en.get("properties", {}) or {}
        rel = (props.get("Challenges", {}) or {}).get("relation", []) or []
        for r in rel:
            cid = r.get("id")
            if cid:
                joined_map[cid] = en_id

    # ===== 2) members_count + members_preview (Active enrollments)
    all_enroll_payload = {
        "filter": {"property": "Status", "select": {"equals": "Active"}},
        "page_size": 200
    }
    all_enroll_res = notion.query_db(enroll_db, all_enroll_payload)
    all_enrollments = all_enroll_res.get("results", []) or []

    members_count = {}      # challenge_id -> count
    members_preview = {}    # challenge_id -> [name1, name2, name3]

    def _preview_add(map_obj, cid: str, label: str, maxn: int = 3):
        arr = map_obj.get(cid, [])
        if label and label not in arr and len(arr) < maxn:
            arr.append(label)
            map_obj[cid] = arr

    for en in all_enrollments:
        eprops = en.get("properties", {}) or {}
        title = notion_title(eprops, "Name") or ""
        label = title.split(" in ", 1)[0].strip() if " in " in title else title[:24].strip()

        rel = (eprops.get("Challenges", {}) or {}).get("relation", []) or []
        for r in rel:
            cid = r.get("id")
            if not cid:
                continue
            members_count[cid] = int(members_count.get(cid, 0)) + 1
            _preview_add(members_preview, cid, label, 3)

    # ===== 3) today activity from Daily Logs (single query, aggregate)
    DL_DATE_PROP = "Date"
    DL_CH_PROP = "Challenges"
    DL_COUNTED_PROP = "Is Counted"
    DL_STATUS_PROP = "Status"
    DL_NAME_PROP = "Name"

    today_str = dt.now(timezone.utc).date().isoformat()

    today_payload = {
        "filter": {
            "and": [
                {"property": DL_DATE_PROP, "date": {"equals": today_str}},
                {"property": DL_COUNTED_PROP, "checkbox": {"equals": True}},
                # اگر دوست داری فقط Done حساب بشه:
                {"property": DL_STATUS_PROP, "select": {"equals": "Done"}},
            ]
        },
        "page_size": 200
    }
    today_res = notion.query_db(daily_db, today_payload)
    today_logs = today_res.get("results", []) or []

    today_checkins = {}   # challenge_id -> count
    today_preview = {}    # challenge_id -> [name1,name2,name3]

    for log in today_logs:
        props = log.get("properties", {}) or {}
        who = notion_title(props, DL_NAME_PROP) or ""
        who = who.strip()[:24]

        rel = (props.get(DL_CH_PROP, {}) or {}).get("relation", []) or []
        for r in rel:
            cid = r.get("id")
            if not cid:
                continue
            today_checkins[cid] = int(today_checkins.get(cid, 0)) + 1
            _preview_add(today_preview, cid, who, 3)

    # ===== 4) list joinable challenges
    payload = {
        "filter": {
            "and": [
                {"property": CH_STATUS_PROP, "status": {"equals": "Active"}},
                {"property": CH_VISIBILITY_PROP, "select": {"does_not_equal": "Private"}},
            ]
        },
        "sorts": [{"property": CH_NAME_PROP, "direction": "ascending"}],
        "page_size": 100
    }

    res = notion.query_db(ch_db, payload)
    results = res.get("results", []) or []

    items = []
    for page in results:
        props = page.get("properties", {}) or {}

        challenge_id = page.get("id")
        visibility = notion_select(props, CH_VISIBILITY_PROP) or "Private"
        status = notion_status(props, CH_STATUS_PROP)
        name = notion_title(props, CH_NAME_PROP)
        desc = notion_rich_text(props, CH_DESC_PROP)
        duration_days = notion_number(props, CH_DURATION_PROP)

        enrollment_id = joined_map.get(challenge_id)
        is_joined = bool(enrollment_id)

        mc = int(members_count.get(challenge_id, 0))
        tc = int(today_checkins.get(challenge_id, 0))

        items.append({
            "challenge_id": challenge_id,
            "name": name,
            "status": status,
            "visibility": visibility,
            "description": desc,
            "duration_days": duration_days,
            "needs_code": (visibility == "Invite-only"),

            "is_joined": is_joined,
            "enrollment_id": enrollment_id,

            # social proof
            "members_count": mc,
            "members_preview": members_preview.get(challenge_id, []),

            # today activity
            "today_checkins": tc,
            "today_preview": today_preview.get(challenge_id, []),

            # simple badge
            "is_hot": (tc >= 3) or (mc >= 10),
        })

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

def notion_checkbox(props: dict, key: str) -> bool | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    val = obj.get("checkbox")
    if isinstance(val, bool):
        return val
    return None

def notion_number(props: dict, key: str) -> float | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    num = obj.get("number")
    if isinstance(num, (int, float)):
        return float(num)
    return None

def notion_status_name(props: dict, key: str) -> str | None:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return None
    st = obj.get("status")
    if isinstance(st, dict):
        return st.get("name")
    return None

def notion_relation_ids(props: dict, key: str) -> list[str]:
    obj = props.get(key, {})
    if not isinstance(obj, dict):
        return []
    rel = obj.get("relation", [])
    if not isinstance(rel, list):
        return []
    return [x.get("id") for x in rel if isinstance(x, dict) and x.get("id")]

@app.get("/challenges/<challenge_id>")
def challenge_detail(challenge_id):
    # Optional auth (فعلاً فقط برای آینده؛ الان لازم نیست)
    claims = require_auth(optional=True)
    user_id = claims.get("user_id") if claims else None
    registered = bool(claims.get("registered")) if claims else False

    ch_page = get_page(challenge_id)
    props = ch_page.get("properties", {}) or {}

    # مطابق schema واقعی Challenges شما
    name = notion_title_text(props, "Name")
    description = notion_rich_text(props, "Description")
    visibility = notion_select_name(props, "Visibility")
    status = notion_status_name(props, "Status")

    duration_days = notion_number(props, "Duration (days)")
    max_members = notion_number(props, "Max Members")

    requires_proof = notion_checkbox(props, "Requires Proof")
    checkin_method = notion_select_name(props, "Check-in Method")
    goal_type = notion_select_name(props, "Goal Type")

    tags = notion_multi_select(props, "Tags")

    # Members relation: فقط count (پردازش کم)
    member_ids = notion_relation_ids(props, "Members")
    members_count = len(member_ids)

    # Join Code: برای Public لازم نیست، برای Invite-only در UI ممکنه لازم باشه.
    # ولی امن‌تر/مینیمال‌تر: فقط یک flag بدیم که "join_code_required" هست یا نه
    join_code_raw = (notion_rich_text(props, "Join Code") or "").strip()
    join_code_required = (visibility == "Invite-only" and bool(join_code_raw))

    # Optional: اگر لاگین بود، is_joined را هم بدون query اضافه محاسبه نکنیم (سنگین میشه)
    # این را از /me/dashboard و /challenges (list) داریم. پس اینجا نمی‌زنیم.

    return jsonify({
        "ok": True,
        "challenge": {
            "challenge_id": challenge_id,
            "name": name,
            "description": description,
            "visibility": visibility,
            "status": status,
            "duration_days": duration_days,
            "max_members": max_members,
            "requires_proof": requires_proof,
            "checkin_method": checkin_method,
            "goal_type": goal_type,
            "tags": tags,
            "members_count": members_count,
            "join_code_required": join_code_required
        }
    })

def safe_int(x, default=0):
    try:
        return int(str(x).strip())
    except:
        return default

def safe_bool(val) -> bool:
    s = str(val or "").strip().lower()
    return s in ("1", "true", "yes", "on")

def notion_query_all(db_id: str, payload: dict):
    """Fetch all results from a Notion database query (handles pagination)."""
    out = []
    cursor = None
    while True:
        p = dict(payload)
        if cursor:
            p["start_cursor"] = cursor
        res = notion.query_db(db_id, p)
        out.extend(res.get("results", []) or [])
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
        if not cursor:
            break
    return out

def compute_enrollment_stats(enrollment_id: str, daily_db_id: str):
    """Recompute Total Check-ins + Current Streak from Daily Logs for THIS enrollment.

    Streak rule:
    - If today is checked → streak counts from today backward.
    - Else if yesterday is checked → streak counts from yesterday backward.
    - Else → streak = 0
    """
    payload = {
        "filter": {
            "and": [
                {"property": "Enrollment", "relation": {"contains": enrollment_id}},
                {"property": "Is Counted", "checkbox": {"equals": True}},
            ]
        },
        "page_size": 100
    }

    pages = notion_query_all(daily_db_id, payload)

    dates = set()
    for page in pages:
        props = page.get("properties", {}) or {}
        d = (props.get("Date", {}) or {}).get("date", {})
        d = d.get("start") if isinstance(d, dict) else None
        if d:
            dates.add(d)

    total_checkins = len(dates)

    today = dt.now(timezone.utc).date()
    today_iso = today.isoformat()
    yday_iso = (today - timedelta(days=1)).isoformat()

    # choose start date for streak
    if today_iso in dates:
        cur = today
    elif yday_iso in dates:
        cur = today - timedelta(days=1)
    else:
        return total_checkins, 0

    streak = 0
    while True:
        d = cur.isoformat()
        if d in dates:
            streak += 1
            cur = cur - timedelta(days=1)
        else:
            break

    return total_checkins, streak

def compute_user_streaks(user_id: str, daily_db_id: str):
    """
    Current streak + Longest streak برای کاربر از روی Daily Logs
    معیار: لاگ‌هایی که Is Counted = True و Users relation شامل user_id باشد.
    """
    payload = {
        "filter": {
            "and": [
                {"property": "Users", "relation": {"contains": user_id}},
                {"property": "Is Counted", "checkbox": {"equals": True}},
            ]
        },
        "page_size": 100
    }

    pages = notion_query_all(daily_db_id, payload)

    dates = set()
    for page in pages:
        props = page.get("properties", {}) or {}
        d = (props.get("Date", {}) or {}).get("date", {})
        d = d.get("start") if isinstance(d, dict) else None
        if d:
            dates.add(d)

    # Current streak از امروز به عقب (UTC)
    cur = dt.now(timezone.utc).date()
    current = 0
    while True:
        ds = cur.isoformat()
        if ds in dates:
            current += 1
            cur = cur - timedelta(days=1)
        else:
            break

    # Longest streak: با اسکن تاریخ‌های مرتب شده
    if not dates:
        return 0, 0

    sorted_days = sorted(dates)  # ISO => sortable
    longest = 1
    run = 1
    prev = dt.fromisoformat(sorted_days[0]).date()

    for s in sorted_days[1:]:
        d = dt.fromisoformat(s).date()
        if (d - prev).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1
        prev = d

    return current, longest


def sync_user_stats(user_id: str, daily_db_id: str):
    current, longest = compute_user_streaks(user_id, daily_db_id)
    notion_update_page(user_id, {
        "Current Streak": {"rich_text": [{"text": {"content": str(current)}}]},
        "Longest Streak": {"rich_text": [{"text": {"content": str(longest)}}]},
    })
    return current, longest

@app.get("/challenges/<challenge_id>/members")
def challenge_members(challenge_id):
    enroll_db = app.config.get("NOTION_ENROLLMENTS_DB_ID")
    if not enroll_db:
        return jsonify({"ok": False, "error": "NOTION_ENROLLMENTS_DB_ID missing in .env"}), 500

    limit = safe_int(request.args.get("limit"), 20)
    if limit < 1:
        limit = 1
    if limit > 50:
        limit = 50

    cursor = request.args.get("cursor")
    expand_user = safe_bool(request.args.get("expand_user"))

    payload = {
        "page_size": limit,
        "filter": {
            "property": "Challenges",
            "relation": {"contains": challenge_id}
        }
    }
    if cursor:
        payload["start_cursor"] = cursor

    res = notion.query_db(enroll_db, payload)
    results = res.get("results", []) or []

    items = []
    for e in results:
        eprops = e.get("properties", {}) or {}

        enrollment_id = e.get("id")
        enrollment_name = notion_title_text(eprops, "Name")
        enrollment_status = notion_select_name(eprops, "Status")

        users_rel = eprops.get("Users", {}).get("relation", [])
        user_id = users_rel[0].get("id") if isinstance(users_rel, list) and users_rel else None

        item = {
            "enrollment_id": enrollment_id,
            "enrollment_name": enrollment_name,
            "enrollment_status": enrollment_status,
            "user_id": user_id,
        }

        # Optional: enrich user (کمینه)
        if expand_user and user_id:
            u = get_page(user_id)
            uprops = u.get("properties", {}) or {}
            item["user_name"] = notion_title_text(uprops, "Name")
            item["telegram_username"] = (notion_rich_text(uprops, "Telegram Username") or "").strip() or None

        items.append(item)

    return jsonify({
        "ok": True,
        "challenge_id": challenge_id,
        "items": items,
        "next_cursor": res.get("next_cursor"),
        "has_more": bool(res.get("has_more"))
    })

def date_range_days(days: int):
    # returns list of iso dates from (today-days+1) ... today
    today = dt.now(timezone.utc).date()
    out = []
    for i in range(days):
        d = today - timedelta(days=(days - 1 - i))
        out.append(d.isoformat())
    return out

@app.get("/me/challenges/<enrollment_id>/history")
def enrollment_history(enrollment_id):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    user_id = claims["user_id"]

    # ✅ validate enrollment belongs to user
    if not enrollment_belongs_to_user(enrollment_id, user_id):
        return jsonify({"ok": False, "error": "forbidden_enrollment"}), 403

    daily_db = app.config.get("NOTION_DAILY_LOGS_DB_ID")
    if not daily_db:
        return jsonify({"ok": False, "error": "NOTION_DAILY_LOGS_DB_ID missing in .env"}), 500

    days = safe_int(request.args.get("days"), 30)
    if days < 1:
        days = 1
    if days > 120:
        days = 120

    # range
    end_date = dt.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days - 1)
    start_iso = start_date.isoformat()
    end_iso = end_date.isoformat()

    # 1 query فقط
    payload = {
        "filter": {
            "and": [
                {"property": "Enrollment", "relation": {"contains": enrollment_id}},
                {"property": "Users", "relation": {"contains": user_id}},
                {"property": "Date", "date": {"on_or_after": start_iso}},
                {"property": "Date", "date": {"on_or_before": end_iso}},
            ]
        },
        "page_size": 200
    }

    res = notion.query_db(daily_db, payload)
    results = res.get("results", []) or []

    by_date = {}
    for page in results:
        props = page.get("properties", {}) or {}

        # Date
        date_obj = props.get("Date", {}).get("date", {})
        d = date_obj.get("start") if isinstance(date_obj, dict) else None
        if not d:
            continue

        status = notion_select_name(props, "Status")

        # is_counted
        is_counted = None
        ic = props.get("Is Counted", {})
        if isinstance(ic, dict):
            v = ic.get("checkbox")
            if isinstance(v, bool):
                is_counted = v

        by_date[d] = {
            "date": d,
            "daily_log_id": page.get("id"),
            "status": status,
            "is_counted": is_counted
        }

    # timeline ثابت
    dates = date_range_days(days)
    timeline = []
    checked_days = 0

    for d in dates:
        row = by_date.get(d)
        if row:
            checked_days += 1
            timeline.append(row)
        else:
            timeline.append({
                "date": d,
                "daily_log_id": None,
                "status": None,
                "is_counted": None
            })

    total_days = len(dates)
    missed_days = total_days - checked_days

    return jsonify({
        "ok": True,
        "enrollment_id": enrollment_id,
        "range": {"start": start_iso, "end": end_iso, "days": total_days},
        "summary": {
            "checked_days": checked_days,
            "missed_days": missed_days,
            "total_days": total_days
        },
        "items": timeline
    })

@app.get("/me/enrollments/<enrollment_id>")
def me_enrollment_detail(enrollment_id):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    user_id = claims["user_id"]

    # ✅ validate belongs to user (تو پروژه‌ات قبلاً اینو داشتی)
    if not enrollment_belongs_to_user(enrollment_id, user_id):
        return jsonify({"ok": False, "error": "forbidden_enrollment"}), 403

    # --- load enrollment page
    enrollment_page = notion.retrieve_page(enrollment_id)
    eprops = enrollment_page.get("properties", {}) or {}

    enrollment_name = notion_title(eprops, "Name")
    enrollment_status = notion_select(eprops, "Status")

    # enrollment -> challenge relation
    ch_rel = (eprops.get("Challenges", {}) or {}).get("relation", []) or []
    challenge_id = ch_rel[0]["id"] if ch_rel else None

    challenge = None
    if challenge_id:
        ch_page = notion.retrieve_page(challenge_id)
        cprops = ch_page.get("properties", {}) or {}
        challenge = {
            "challenge_id": challenge_id,
            "name": notion_title(cprops, CH_NAME_PROP),
            "description": notion_rich_text(cprops, CH_DESC_PROP),
            "duration_days": notion_number(cprops, CH_DURATION_PROP),
            "visibility": notion_select(cprops, CH_VISIBILITY_PROP),
            "status": notion_status(cprops, CH_STATUS_PROP),
        }

    # --- recent logs (last 14)
    daily_db = app.config.get("NOTION_DAILY_LOGS_DB_ID")
    recent_logs = []
    today_checked = False

    if daily_db:

        DL_DATE_PROP = "Date"
        DL_ENROLL_PROP = "Enrollment"   # ✅ اسم درست طبق schema
        DL_STATUS_PROP = "Status"
        DL_SOURCE_PROP = "Source"
        DL_NOTES_PROP = "Notes"
        DL_PROOF_PROP = "Proof"
        DL_COUNTED_PROP = "Is Counted"

        logs_payload = {
            "filter": {
                "property": DL_ENROLL_PROP,
                "relation": {"contains": enrollment_id}
            },
            "sorts": [{"property": DL_DATE_PROP, "direction": "descending"}],
            "page_size": 14
        }
        logs_res = notion.query_db(daily_db, logs_payload)
        logs = logs_res.get("results", []) or []

        today_str = dt.now(timezone.utc).date().isoformat()

        for p in logs:
            pprops = p.get("properties", {}) or {}

            d = (pprops.get(DL_DATE_PROP, {}) or {}).get("date", {}) or {}
            date_str = d.get("start")

            recent_logs.append({
                "daily_log_id": p.get("id"),
                "date": date_str,
                "status": notion_select(pprops, DL_STATUS_PROP),
                "source": notion_select(pprops, DL_SOURCE_PROP),
                "notes": notion_rich_text(pprops, DL_NOTES_PROP),
                "proof": notion_rich_text(pprops, DL_PROOF_PROP),
                "is_counted": bool((pprops.get(DL_COUNTED_PROP, {}) or {}).get("checkbox", False)),
            })

            if date_str == today_str:
                today_checked = True

        # Try to read from enrollment properties (synced on checkin)
    raw_total = notion_rich_text(eprops, "Total Check-ins")
    raw_streak = notion_rich_text(eprops, "Current Streak in Challenge")

    def safe_int(x, default=0):
        try:
            return int(str(x).strip())
        except:
            return default

    total_checkins = safe_int(raw_total, None)
    current_streak = safe_int(raw_streak, None)
    

    # Fallback: if missing, compute on the fly
    if total_checkins is None or current_streak is None:
        daily_db = app.config.get("NOTION_DAILY_LOGS_DB_ID")
        if daily_db:
            tc, cs = compute_enrollment_stats(enrollment_id, daily_db)
            total_checkins = tc if total_checkins is None else total_checkins
            current_streak = cs if current_streak is None else current_streak


    return jsonify({
        "ok": True,
        "enrollment": {
            "enrollment_id": enrollment_id,
            "name": enrollment_name,
            "status": enrollment_status,
            "today_checked": today_checked,
            "total_checkins": total_checkins,
            "current_streak": current_streak,
        },
        "challenge": challenge,
        "recent_logs": recent_logs,
    })

@app.get("/me/enrollments/<enrollment_id>/leaderboard")
def enrollment_leaderboard(enrollment_id):
    claims = require_auth()
    if not claims:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if not claims.get("registered"):
        return jsonify({"ok": False, "error": "not_registered"}), 403

    enroll_db = app.config.get(ENROLL_DB)
    daily_db = app.config.get("NOTION_DAILY_LOGS_DB_ID")
    if not enroll_db or not daily_db:
        return jsonify({"ok": False, "error": "db_missing"}), 500

    # -------------------------------
    # 1) Find challenge_id of enrollment
    # -------------------------------
    enrollment_page = notion.retrieve_page(enrollment_id)
    eprops = enrollment_page.get("properties", {}) or {}

    challenge_rel = (eprops.get("Challenges", {}) or {}).get("relation", [])
    if not challenge_rel:
        return jsonify({"ok": False, "error": "challenge_not_found"}), 404

    challenge_id = challenge_rel[0]["id"]

    # -------------------------------
    # 2) Get all active enrollments for this challenge
    # -------------------------------
    payload = {
        "filter": {
            "and": [
                {"property": "Challenges", "relation": {"contains": challenge_id}},
                {"property": "Status", "select": {"equals": "Active"}},
            ]
        },
        "page_size": 100
    }
    res = notion.query_db(enroll_db, payload)
    enrollments = res.get("results", []) or []

    # Map enrollment_id -> name (and list of ids)
    enroll_name = {}
    enrollment_ids = []
    for en in enrollments:
        eid = en.get("id")
        props = en.get("properties", {}) or {}
        enroll_name[eid] = notion_title(props, "Name") or "—"
        enrollment_ids.append(eid)

    # -------------------------------
    # 3) Query ALL counted daily logs for this challenge (one time)
    # -------------------------------
    dl_payload = {
        "filter": {
            "and": [
                {"property": "Challenges", "relation": {"contains": challenge_id}},
                {"property": "Is Counted", "checkbox": {"equals": True}},
            ]
        },
        "page_size": 100
    }
    logs_pages = notion_query_all(daily_db, dl_payload)

    # Build: enrollment_id -> set(dates)
    dates_by_enrollment = {eid: set() for eid in enrollment_ids}

    for log in logs_pages:
        props = log.get("properties", {}) or {}

        # Date
        d = (props.get("Date", {}) or {}).get("date", {})
        d = d.get("start") if isinstance(d, dict) else None
        if not d:
            continue

        # Enrollment relation (Daily Logs باید Enrollment relation داشته باشد)
        rel = (props.get("Enrollment", {}) or {}).get("relation", [])
        if not rel:
            continue

        eid = rel[0].get("id")
        if eid in dates_by_enrollment:
            dates_by_enrollment[eid].add(d)

    # -------------------------------
    # 4) Compute total_checkins + current_streak with your rule
    # -------------------------------
    today = dt.now(timezone.utc).date()
    today_iso = today.isoformat()
    yday_iso = (today - timedelta(days=1)).isoformat()

    def compute_streak(dates_set):
        # Start: today if checked else yesterday if checked else 0
        if today_iso in dates_set:
            cur = today
        elif yday_iso in dates_set:
            cur = today - timedelta(days=1)
        else:
            return 0

        streak = 0
        while True:
            iso = cur.isoformat()
            if iso in dates_set:
                streak += 1
                cur = cur - timedelta(days=1)
            else:
                break
        return streak

    overall = []
    for eid in enrollment_ids:
        ds = dates_by_enrollment.get(eid, set())
        total_checkins = len(ds)
        current_streak = compute_streak(ds)

        overall.append({
            "enrollment_id": eid,
            "name": enroll_name.get(eid, "—"),
            "total_checkins": int(total_checkins),
            "current_streak": int(current_streak),
        })

    # Sort by streak first, then total
    overall.sort(key=lambda x: (x["current_streak"], x["total_checkins"]), reverse=True)
    overall = overall[:5]

    # -------------------------------
    # 5) Today leaderboard
    # -------------------------------
    today_map = {}
    for eid, ds in dates_by_enrollment.items():
        if today_iso in ds:
            today_map[eid] = today_map.get(eid, 0) + 1

    today_rows = [
        {"enrollment_id": eid, "name": enroll_name.get(eid, "—"), "checkins": cnt}
        for eid, cnt in today_map.items()
    ]
    today_rows.sort(key=lambda x: x["checkins"], reverse=True)
    today_rows = today_rows[:5]

    return jsonify({
        "ok": True,
        "overall": overall,
        "today": today_rows,
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
