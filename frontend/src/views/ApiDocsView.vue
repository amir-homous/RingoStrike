<template>
  <div class="docs-page">
    <header class="docs-header">
      <div class="header-content">
        <h1>🛠 RingoStrike API Explorer</h1>
        <p class="subtitle">مستندات تعاملی متصل به پورت 5005 (SQLite Backend)</p>
      </div>
      <div class="env-badge">Backend: {{ API_BASE }}</div>
    </header>

    <div class="docs-grid">
      <!-- Sidebar Navigation -->
      <aside class="sidebar">
        <div class="nav-group">
          <h3>Public Endpoints</h3>
          <nav>
            <a v-for="api in publicApis" :key="api.id" :href="'#' + api.id" class="nav-link">
              <span :class="['method-badge', api.method]">{{ api.method }}</span> {{ api.name }}
            </a>
          </nav>
        </div>
        <div class="nav-group">
          <h3>User (Auth Required)</h3>
          <nav>
            <a v-for="api in userApis" :key="api.id" :href="'#' + api.id" class="nav-link">
              <span :class="['method-badge', api.method]">{{ api.method }}</span> {{ api.name }}
            </a>
          </nav>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="content">
        <section v-for="api in allApis" :key="api.id" :id="api.id" class="api-section">
          <div class="api-header">
            <div class="title-row">
              <h2>{{ api.name }}</h2>
              <span v-if="api.auth" class="auth-tag">Requires Auth</span>
            </div>
            <div class="endpoint-bar">
              <span :class="['method', api.method]">{{ api.method }}</span>
              <code class="path">{{ api.path }}</code>
            </div>
          </div>
          
          <p class="desc">{{ api.description }}</p>

          <div class="playground-box">
            <div class="playground-header">Playground & Schema</div>
            
            <div class="playground-body">
              <!-- Parameters Input -->
              <div v-if="extractParams(api.path).length > 0" class="params-section">
                <label>URL Parameters:</label>
                <div v-for="param in extractParams(api.path)" :key="param" class="input-row">
                  <span>{{ param }}:</span>
                  <input v-model="testState[api.id].params[param]" placeholder="Value..." />
                </div>
              </div>

              <!-- POST Body Input -->
              <div v-if="api.method === 'POST'" class="body-section">
                <label>JSON Body:</label>
                <textarea v-model="testState[api.id].body" rows="3"></textarea>
              </div>

              <!-- Response Structure Info -->
              <div class="schema-section">
                <label>Expected Item Structure:</label>
                <pre class="schema-code"><code>{{ formatJSON(api.structure) }}</code></pre>
              </div>

              <div class="actions">
                <button @click="runTest(api)" :disabled="testState[api.id].loading" class="test-btn">
                  {{ testState[api.id].loading ? '⌛ Requesting...' : '🚀 Execute' }}
                </button>
              </div>
            </div>

            <!-- Live Result Result -->
            <div v-if="testState[api.id].response" class="result-section">
              <div :class="['result-header', testState[api.id].error ? 'err' : 'ok']">
                Response Status: {{ testState[api.id].status }}
              </div>
              <pre class="result-code"><code>{{ formatJSON(testState[api.id].response) }}</code></pre>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import axios from 'axios';

// استفاده از .env که گفتی
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5005';

const publicApis = [
  {
    id: 'health',
    name: 'Health Check',
    method: 'GET',
    path: '/health',
    auth: false,
    description: 'بررسی زنده بودن سرور Flask.',
    structure: { ok: true }
  },
  {
    id: 'public-challenges',
    name: 'Public Challenges',
    method: 'GET',
    path: '/challenges/public',
    auth: false,
    description: 'دریافت چالش‌های عمومی بدون نیاز به لاگین.',
    structure: { 
      ok: true, 
      items: [{ challenge_id: 1, name: "Name", visibility: "Public", status: "Active", description: "...", duration_days: 30 }] 
    }
  }
];

const userApis = [
  {
    id: 'get-me',
    name: 'Current User (Me)',
    method: 'GET',
    path: '/me',
    auth: true,
    description: 'دریافت پروفایل کاربر لاگین شده (Local یا Telegram).',
    structure: { ok: true, user_id: 1, username: "amir", name: "Amir", email: "...", auth_method: "local", registered: true }
  },
  {
    id: 'list-challenges',
    name: 'Full Challenges List',
    method: 'GET',
    path: '/challenges',
    auth: true,
    description: 'لیست چالش‌ها با تمام جزئیات عضویت و وضعیت کد.',
    structure: { 
      "items": [
        {
          "challenge_id": 1,
          "description": "drink daily water",
          "duration_days": 100,
          "enrollment_id": 1,
          "is_joined": true,
          "members_count": 1,
          "name": "drink daily 1litr water",
          "needs_code": false,
          "status": "active",
          "visibility": "public"
        }
      ]
    }
  },
  {
    id: 'challenge-detail',
    name: 'Challenge Detail',
    method: 'GET',
    path: '/challenges/:id',
    auth: true,
    description: 'جزئیات کامل فنی یک چالش از دیتابیس.',
    structure: { 
      "ok": true,
      "item": {
        "challenge_id": 2,
        "checkin_method": "Photo",
        "description": "...",
        "duration_days": 30,
        "goal_type": "Daily",
        "join_code_required": false,
        "max_members": 50,
        "members_count": 1,
        "name": "Drink Water",
        "requires_proof": true,
        "status": "Active",
        "tags": ["سلامتی", "نظم"],
        "visibility": "Public"
      }
    }
  },
  {
    id: 'my-challenges',
    name: 'My Enrolled Challenges',
    method: 'GET',
    path: '/me/challenges',
    auth: true,
    description: 'چالش‌هایی که کاربر در آن‌ها Active است.',
    structure: { 
      "ok": true,
      "items": [
        { "enrollment_id": 5, "enrollment_name": "Name", "status": "Active", "challenge_id": 1, "today_checked": false }
      ] 
    }
  },
  {
    id: 'leaderboard',
    name: 'Leaderboard',
    method: 'GET',
    path: '/me/enrollments/:id/leaderboard',
    auth: true,
    description: 'رتبه‌بندی اعضای چالش بر اساس دیتای واقعی سشن کاربر.',
    structure: {
      "ok": true,
      "overall": [
        {
          "current_streak": 1,
          "enrollment_id": 2,
          "name": "Amir hossein",
          "total_checkins": 1,
          "username": "Admin"
        }
      ],
      "today": []
    }
  },
    {
    id: 'join-challenge',
    name: 'Join Challenge',
    method: 'POST',
    path: '/challenges/:id/join',
    auth: true,
    description: 'عضویت در یک چالش. اگر چالش Invite-only باشد، فرستادن join_code الزامی است.',
    body: { join_code: "12345" }, // این در پلی‌گراند نمایش داده می‌شود
    structure: { 
      "ok": true, 
      "mode": "created", // یا "reactivated" یا "existing"
      "enrollment_id": 10, 
      "challenge_id": 2 
    }
  },
  {
    id: 'checkin',
    name: 'Submit Check-in',
    method: 'POST',
    path: '/me/challenges/:id/checkin',
    auth: true,
    description: 'ثبت تیک روزانه برای یک عضویت خاص.',
    body: { note: "Optional" },
    structure: { "ok": true, "message": "Check-in recorded" }
  }
];

const allApis = [...publicApis, ...userApis];

// State Management
const testState = reactive(
  allApis.reduce((acc, api) => {
    acc[api.id] = {
      loading: false,
      response: null,
      error: false,
      status: null,
      params: {},
      body: api.body ? JSON.stringify(api.body, null, 2) : '{}'
    };
    return acc;
  }, {})
);

const extractParams = (path) => {
  const matches = path.match(/:[a-zA-Z0-9]+/g);
  return matches ? matches.map(m => m.replace(':', '')) : [];
};

const formatJSON = (val) => JSON.stringify(val, null, 2);

const runTest = async (api) => {
  const state = testState[api.id];
  state.loading = true;
  state.response = null;
  state.error = false;

  let finalPath = api.path;
  Object.keys(state.params).forEach(key => {
    finalPath = finalPath.replace(`:${key}`, state.params[key]);
  });

  try {
    const config = {
      method: api.method,
      url: `${API_BASE}${finalPath}`,
      withCredentials: true
    };
    if (api.method === 'POST') config.data = JSON.parse(state.body);

    const res = await axios(config);
    state.response = res.data;
    state.status = res.status;
  } catch (err) {
    state.error = true;
    state.response = err.response ? err.response.data : { message: err.message };
    state.status = err.response ? err.response.status : 'ERR';
  } finally {
    state.loading = false;
  }
};
</script>

<style scoped>
.docs-page { padding: 40px; color: #e0e0e0; max-width: 1400px; margin: 0 auto; font-family: 'Inter', sans-serif; text-align: left; direction: ltr; background: #050505; }
.docs-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; padding-bottom: 30px; margin-bottom: 40px; }
.subtitle { color: #666; font-size: 0.9rem; }
.env-badge { background: #1a1a1a; padding: 5px 15px; border-radius: 20px; border: 1px solid #333; font-family: monospace; color: #4ade80; font-size: 0.8rem; }

.docs-grid { display: grid; grid-template-columns: 280px 1fr; gap: 40px; }
.sidebar { position: sticky; top: 40px; height: calc(100vh - 80px); overflow-y: auto; }
.nav-group h3 { font-size: 0.7rem; text-transform: uppercase; color: #444; letter-spacing: 1px; margin: 20px 0 10px; }
.nav-link { display: flex; align-items: center; gap: 8px; padding: 8px; color: #888; text-decoration: none; font-size: 0.85rem; border-radius: 6px; transition: 0.2s; }
.nav-link:hover { background: #111; color: #fff; }

.api-section { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 12px; padding: 30px; margin-bottom: 50px; }
.api-header { margin-bottom: 20px; }
.title-row { display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }
.auth-tag { font-size: 0.6rem; background: #332200; color: #ffcc00; padding: 2px 8px; border-radius: 4px; }
.endpoint-bar { background: #000; padding: 10px 15px; border-radius: 6px; border: 1px solid #222; display: flex; align-items: center; gap: 15px; }
.method { font-weight: 800; font-size: 0.7rem; padding: 4px 10px; border-radius: 4px; min-width: 50px; text-align: center; }
.GET { background: #004d40; color: #4ade80; }
.POST { background: #0d47a1; color: #64b5f6; }
.path { font-family: 'Fira Code', monospace; color: #fff; font-size: 0.9rem; }

.desc { color: #aaa; line-height: 1.6; margin-bottom: 25px; border-left: 3px solid #333; padding-left: 15px; }

.playground-box { background: #000; border-radius: 8px; border: 1px solid #222; overflow: hidden; }
.playground-header { background: #111; padding: 10px 15px; font-size: 0.75rem; color: #555; text-transform: uppercase; font-weight: bold; border-bottom: 1px solid #222; }
.playground-body { padding: 20px; }

.params-section, .body-section, .schema-section { margin-bottom: 20px; }
label { display: block; font-size: 0.75rem; color: #555; margin-bottom: 8px; font-weight: bold; }
.input-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.input-row span { font-size: 0.8rem; color: #888; width: 100px; }
input, textarea { background: #0a0a0a; border: 1px solid #333; color: #4ade80; padding: 8px; border-radius: 4px; width: 100%; font-family: monospace; font-size: 0.85rem; }

.schema-code { background: #050505; padding: 15px; border-radius: 4px; border: 1px dashed #333; color: #666; font-size: 0.8rem; }
.test-btn { background: #4ade80; color: #000; border: none; padding: 10px 25px; border-radius: 6px; font-weight: bold; cursor: pointer; }
.test-btn:hover { opacity: 0.8; }

.result-section { border-top: 1px solid #222; }
.result-header { padding: 10px 20px; font-size: 0.75rem; font-weight: bold; }
.result-header.ok { background: #003311; color: #4ade80; }
.result-header.err { background: #330000; color: #ff5252; }
.result-code { padding: 20px; background: #000; color: #81d4fa; font-size: 0.85rem; max-height: 400px; overflow-y: auto; }
</style>
