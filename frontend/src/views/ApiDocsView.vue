<template>
  <div class="docs-page">
    <header class="docs-header">
      <div class="header-content">
        <h1>🛠 RingoStrike API Explorer</h1>
        <p class="subtitle">Interactive API reference for the current Flask + SQLite backend</p>
      </div>
      <div class="env-badge">Backend: {{ API_BASE_LABEL }}</div>
    </header>

    <div class="docs-grid">
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
          <h3>User Endpoints</h3>
          <nav>
            <a v-for="api in userApis" :key="api.id" :href="'#' + api.id" class="nav-link">
              <span :class="['method-badge', api.method]">{{ api.method }}</span> {{ api.name }}
            </a>
          </nav>
        </div>

        <div class="nav-group">
          <h3>Debug</h3>
          <nav>
            <a v-for="api in debugApis" :key="api.id" :href="'#' + api.id" class="nav-link">
              <span :class="['method-badge', api.method]">{{ api.method }}</span> {{ api.name }}
            </a>
          </nav>
        </div>
      </aside>

      <main class="content">
        <section v-for="api in allApis" :key="api.id" :id="api.id" class="api-section">
          <div class="api-header">
            <div class="title-row">
              <h2>{{ api.name }}</h2>
              <span v-if="api.auth" class="auth-tag">Requires Auth</span>
              <span v-if="api.devOnly" class="dev-tag">Development Only</span>
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
              <div v-if="extractParams(api.path).length > 0" class="params-section">
                <label>URL Parameters:</label>
                <div v-for="param in extractParams(api.path)" :key="param" class="input-row">
                  <span>{{ param }}:</span>
                  <input v-model="testState[api.id].params[param]" placeholder="Value..." />
                </div>
              </div>

              <div v-if="['POST', 'PATCH', 'PUT'].includes(api.method)" class="body-section">
                <label>JSON Body:</label>
                <textarea v-model="testState[api.id].body" rows="5"></textarea>
              </div>

              <div class="schema-section">
                <label>Expected Response Shape:</label>
                <pre class="schema-code"><code>{{ formatJSON(api.structure) }}</code></pre>
              </div>

              <div class="actions">
                <button @click="runTest(api)" :disabled="testState[api.id].loading" class="test-btn">
                  {{ testState[api.id].loading ? '⌛ Requesting...' : '🚀 Execute' }}
                </button>
              </div>
            </div>

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
import { reactive } from 'vue';

import apiClient, { API_BASE_LABEL } from '@/lib/api';

const publicApis = [
  {
    id: 'health',
    name: 'Health Check',
    method: 'GET',
    path: '/health',
    auth: false,
    description: 'Checks whether the Flask backend is running.',
    structure: { ok: true },
  },
  {
    id: 'register',
    name: 'Register',
    method: 'POST',
    path: '/auth/register',
    auth: false,
    description: 'Creates a local username/password account and sets the HttpOnly auth cookie.',
    body: {
      username: 'player_name',
      password: 'secret123',
      name: 'Player Name',
      email: 'player@example.com',
    },
    structure: {
      ok: true,
      user_id: 1,
      username: 'player_name',
      access_token: 'jwt',
    },
  },
  {
    id: 'login',
    name: 'Login',
    method: 'POST',
    path: '/auth/login',
    auth: false,
    description: 'Logs in with username/password and sets the HttpOnly auth cookie.',
    body: {
      username: 'player_name',
      password: 'secret123',
    },
    structure: {
      ok: true,
      user_id: 1,
      username: 'player_name',
      access_token: 'jwt',
    },
  },
  {
    id: 'logout',
    name: 'Logout',
    method: 'POST',
    path: '/auth/logout',
    auth: false,
    description: 'Clears the auth cookie.',
    body: {},
    structure: { ok: true },
  },
  {
    id: 'public-challenges',
    name: 'Public Challenges',
    method: 'GET',
    path: '/challenges/public',
    auth: false,
    description: 'Lists active public challenges without requiring login.',
    structure: {
      ok: true,
      items: [
        {
          challenge_id: 1,
          name: 'Challenge',
          visibility: 'Public',
          status: 'Active',
          description: '...',
          duration_days: 30,
        },
      ],
    },
  },
  {
    id: 'challenge-detail',
    name: 'Challenge Detail',
    method: 'GET',
    path: '/challenges/:id',
    auth: false,
    description: 'Returns challenge details. This route is public in the current backend.',
    structure: {
      ok: true,
      item: {
        challenge_id: 1,
        name: 'Challenge',
        description: '...',
        visibility: 'Public',
        status: 'Active',
        duration_days: 30,
        members_count: 3,
        join_code_required: false,
      },
    },
  },
  {
    id: 'challenge-members',
    name: 'Challenge Members',
    method: 'GET',
    path: '/challenges/:id/members',
    auth: false,
    description: 'Returns active challenge members. This route is public in the current backend.',
    structure: {
      ok: true,
      challenge_id: 1,
      items: [
        {
          enrollment_id: 10,
          enrollment_status: 'Active',
          role: 'Member',
          user_id: 1,
          user_name: 'Alice',
          telegram_username: 'alice',
        },
      ],
      has_more: false,
    },
  },
  {
    id: 'public-profile',
    name: 'Public Profile',
    method: 'GET',
    path: '/api/public/profile/:username',
    auth: false,
    description: 'Returns public-safe profile data when profile visibility is public.',
    structure: {
      ok: true,
      profile: {
        id: 1,
        name: 'Alice',
        username: 'alice',
        avatar_url: '/avatars/avatar-1.png',
        bio: '...',
        profile_visibility: 'public',
        title: { key: 'beginner', label: 'Beginner' },
        stats: {},
      },
    },
  },
  {
    id: 'public-consistency',
    name: 'Public Consistency',
    method: 'GET',
    path: '/api/public/profile/:username/consistency',
    auth: false,
    description: 'Returns recent counted check-in dates for public profiles.',
    structure: {
      ok: true,
      days: [{ date: '2026-05-30', count: 1 }],
    },
  },
  {
    id: 'public-achievements',
    name: 'Public Achievements',
    method: 'GET',
    path: '/api/public/profile/:username/achievements',
    auth: false,
    description: 'Returns public unlocked achievements for public profiles.',
    structure: {
      ok: true,
      items: [
        {
          key: 'first_strike',
          title: 'First Strike',
          description: 'Complete your first check-in.',
          unlocked: true,
          unlocked_at: '2026-05-30',
        },
      ],
    },
  },
];

const userApis = [
  {
    id: 'get-me',
    name: 'Current User',
    method: 'GET',
    path: '/me',
    auth: true,
    description: 'Returns the authenticated user from cookie or Bearer token.',
    structure: {
      ok: true,
      user_id: 1,
      username: 'alice',
      name: 'Alice',
      email: 'alice@example.com',
      auth_method: 'local',
      registered: true,
    },
  },
  {
    id: 'list-challenges',
    name: 'Challenges',
    method: 'GET',
    path: '/challenges',
    auth: true,
    description: 'Returns public/invite-only challenges plus joined private challenges visible to the user.',
    structure: {
      ok: true,
      items: [
        {
          challenge_id: 1,
          name: 'Challenge',
          description: '...',
          visibility: 'public',
          status: 'active',
          duration_days: 30,
          members_count: 3,
          members_preview: ['Alice'],
          is_joined: true,
          enrollment_id: 10,
          needs_code: false,
        },
      ],
    },
  },
  {
    id: 'join-challenge',
    name: 'Join Challenge',
    method: 'POST',
    path: '/challenges/:id/join',
    auth: true,
    description: 'Joins a public challenge or an invite-only challenge with a join code.',
    body: { join_code: 'optional' },
    structure: {
      ok: true,
      mode: 'created',
      enrollment_id: 10,
      challenge_id: 1,
    },
  },
  {
    id: 'my-challenges',
    name: 'My Dashboard Challenges',
    method: 'GET',
    path: '/me/challenges',
    auth: true,
    description: 'Returns dashboard challenge list and today check-in state.',
    structure: {
      ok: true,
      date: '2026-05-30',
      user: {
        name: 'Alice',
        stats: {
          total_points: 100,
          current_streak: 3,
          longest_streak: 7,
        },
      },
      challenges: [
        {
          enrollment_id: 10,
          enrollment_name: 'Challenge',
          status: 'Active',
          challenge_id: 1,
          today_checked: false,
        },
      ],
    },
  },
  {
    id: 'enrollment-detail',
    name: 'Enrollment Detail',
    method: 'GET',
    path: '/me/enrollments/:id',
    auth: true,
    description: 'Returns enrollment summary, challenge details, recent logs, and today status.',
    structure: {
      ok: true,
      enrollment: {
        enrollment_id: 10,
        status: 'Active',
        challenge_id: 1,
        challenge_name: 'Challenge',
        today_checked: false,
        total_checkins: 12,
        current_streak: 4,
      },
    },
  },
  {
    id: 'checkin',
    name: 'Submit Check-in',
    method: 'POST',
    path: '/me/challenges/:id/checkin',
    auth: true,
    description: 'Creates or updates today’s check-in for an enrollment.',
    body: { notes: 'Optional note' },
    structure: {
      ok: true,
      message: 'Check-in recorded',
      rewards: {
        xp_total: 100,
        achievements: [],
        achievement_xp_reward: 0,
      },
    },
  },
  {
    id: 'history',
    name: 'Check-in History',
    method: 'GET',
    path: '/me/challenges/:id/history',
    auth: true,
    description: 'Returns recent daily check-in history for an enrollment.',
    structure: {
      ok: true,
      days: [
        {
          date: '2026-05-30',
          status: 'Done',
        },
      ],
    },
  },
  {
    id: 'leaderboard',
    name: 'Leaderboard',
    method: 'GET',
    path: '/me/enrollments/:id/leaderboard',
    auth: true,
    description: 'Returns leaderboard for the challenge connected to an enrollment.',
    structure: {
      ok: true,
      overall: [
        {
          name: 'Alice',
          username: 'alice',
          enrollment_id: 10,
          total_checkins: 12,
          current_streak: 4,
        },
      ],
      today: [],
    },
  },
  {
    id: 'stats',
    name: 'Stats',
    method: 'GET',
    path: '/me/stats',
    auth: true,
    description: 'Returns canonical user stats from stats service.',
    structure: {
      ok: true,
      user: { id: 1, name: 'Alice' },
      stats: {
        current_streak: 3,
        longest_streak: 7,
        total_checkins: 12,
        total_points: 120,
        xp: 120,
        level: 2,
        next_level_xp: 283,
        progress_percent: 14,
      },
    },
  },
  {
    id: 'activity',
    name: 'Activity Feed',
    method: 'GET',
    path: '/me/activity',
    auth: true,
    description: 'Returns derived activity events such as check-ins, streaks, level-ups, and achievements.',
    structure: {
      ok: true,
      items: [
        {
          type: 'checkin',
          title: 'Check-in completed',
          created_at: '2026-05-30T12:00:00',
        },
      ],
    },
  },
  {
    id: 'achievements',
    name: 'Achievements',
    method: 'GET',
    path: '/me/achievements',
    auth: true,
    description: 'Returns achievement definitions with unlock state for the current user.',
    structure: {
      ok: true,
      items: [
        {
          key: 'first_strike',
          title: 'First Strike',
          unlocked: true,
          unlocked_at: '2026-05-30',
        },
      ],
    },
  },
  {
    id: 'profile',
    name: 'Private Profile',
    method: 'GET',
    path: '/me/profile',
    auth: true,
    description: 'Returns private profile aggregate for the authenticated user.',
    structure: {
      ok: true,
      profile: {
        id: 1,
        name: 'Alice',
        username: 'alice',
        avatar_url: '/avatars/avatar-1.png',
        bio: '...',
        profile_visibility: 'public',
        title: { key: 'beginner', label: 'Beginner' },
        tagline: 'Building consistency one strike at a time.',
        stats: {},
      },
    },
  },
  {
    id: 'consistency',
    name: 'Consistency',
    method: 'GET',
    path: '/me/consistency',
    auth: true,
    description: 'Returns recent consistency heatmap data for the authenticated user.',
    structure: {
      ok: true,
      days: [{ date: '2026-05-30', count: 1 }],
    },
  },
  {
    id: 'profile-settings-get',
    name: 'Profile Settings',
    method: 'GET',
    path: '/api/me/profile/settings',
    auth: true,
    description: 'Returns editable profile settings.',
    structure: {
      ok: true,
      settings: {
        avatar_url: '/avatars/avatar-1.png',
        bio: 'Short bio',
        profile_visibility: 'public',
      },
    },
  },
  {
    id: 'profile-settings-patch',
    name: 'Update Profile Settings',
    method: 'PATCH',
    path: '/api/me/profile/settings',
    auth: true,
    description: 'Updates avatar, bio, and profile visibility.',
    body: {
      avatar_url: '/avatars/avatar-1.png',
      bio: 'Short bio',
      profile_visibility: 'public',
    },
    structure: {
      ok: true,
      settings: {
        avatar_url: '/avatars/avatar-1.png',
        bio: 'Short bio',
        profile_visibility: 'public',
      },
    },
  },
  {
    id: 'profile-visibility',
    name: 'Update Profile Visibility',
    method: 'PATCH',
    path: '/api/profile/visibility',
    auth: true,
    description: 'Updates public/private profile visibility.',
    body: { visibility: 'private' },
    structure: {
      ok: true,
      profile_visibility: 'private',
    },
  },
  {
    id: 'profile-update',
    name: 'Update Profile',
    method: 'PATCH',
    path: '/api/profile',
    auth: true,
    description: 'Updates editable profile identity fields.',
    body: {
      name: 'Alice',
      bio: 'Short bio',
      avatar_url: '/avatars/avatar-1.png',
    },
    structure: {
      ok: true,
      profile: {
        name: 'Alice',
        bio: 'Short bio',
        avatar_url: '/avatars/avatar-1.png',
      },
    },
  },
];

const debugApis = [
  {
    id: 'debug-schema',
    name: 'SQLite Schema',
    method: 'GET',
    path: '/debug/sqlite/schema/:table',
    auth: false,
    devOnly: true,
    description: 'Development-only endpoint for inspecting SQLite table schema.',
    structure: {
      ok: true,
      table: 'users',
      columns: [],
    },
  },
  {
    id: 'debug-counts',
    name: 'SQLite Counts',
    method: 'GET',
    path: '/debug/sqlite/counts',
    auth: false,
    devOnly: true,
    description: 'Development-only endpoint for checking table counts.',
    structure: {
      ok: true,
      counts: {
        users: 1,
        challenges: 1,
        enrollments: 1,
        checkins: 1,
        user_stats: 1,
      },
    },
  },
];

const allApis = [...publicApis, ...userApis, ...debugApis];

const testState = reactive(
  allApis.reduce((acc, api) => {
    acc[api.id] = {
      loading: false,
      response: null,
      error: false,
      status: null,
      params: {},
      body: api.body ? JSON.stringify(api.body, null, 2) : '{}',
    };
    return acc;
  }, {})
);

const extractParams = (path) => {
  const matches = path.match(/:[a-zA-Z0-9_]+/g);
  return matches ? matches.map((m) => m.replace(':', '')) : [];
};

const formatJSON = (val) => JSON.stringify(val, null, 2);

const runTest = async (api) => {
  const state = testState[api.id];
  state.loading = true;
  state.response = null;
  state.error = false;

  let finalPath = api.path;
  Object.keys(state.params).forEach((key) => {
    finalPath = finalPath.replace(`:${key}`, state.params[key]);
  });

  try {
    const config = {
      method: api.method,
      url: finalPath,
      withCredentials: true,
    };

    if (['POST', 'PATCH', 'PUT'].includes(api.method)) {
      config.data = JSON.parse(state.body || '{}');
    }

    const res = await apiClient.request(config);
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
.docs-page {
  padding: 40px;
  color: #e0e0e0;
  max-width: 1400px;
  margin: 0 auto;
  font-family: Inter, system-ui, sans-serif;
  text-align: left;
  direction: ltr;
  background: #050505;
}

.docs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #222;
  padding-bottom: 30px;
  margin-bottom: 40px;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
}

.env-badge {
  background: #1a1a1a;
  padding: 5px 15px;
  border-radius: 20px;
  border: 1px solid #333;
  font-family: monospace;
  color: #4ade80;
  font-size: 0.8rem;
}

.docs-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 40px;
}

.sidebar {
  position: sticky;
  top: 40px;
  height: calc(100vh - 80px);
  overflow-y: auto;
}

.nav-group h3 {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: #444;
  letter-spacing: 1px;
  margin: 20px 0 10px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  color: #888;
  text-decoration: none;
  font-size: 0.85rem;
  border-radius: 6px;
  transition: 0.2s;
}

.nav-link:hover {
  background: #111;
  color: #fff;
}

.api-section {
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 50px;
}

.api-header {
  margin-bottom: 20px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.auth-tag,
.dev-tag {
  font-size: 0.6rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.auth-tag {
  background: #332200;
  color: #ffcc00;
}

.dev-tag {
  background: #12243a;
  color: #81d4fa;
}

.endpoint-bar {
  background: #000;
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #222;
  display: flex;
  align-items: center;
  gap: 15px;
}

.method,
.method-badge {
  font-weight: 800;
  font-size: 0.7rem;
  padding: 4px 10px;
  border-radius: 4px;
  min-width: 50px;
  text-align: center;
}

.GET {
  background: #004d40;
  color: #4ade80;
}

.POST {
  background: #0d47a1;
  color: #64b5f6;
}

.PATCH {
  background: #3b2f00;
  color: #facc15;
}

.PUT {
  background: #3b2f00;
  color: #facc15;
}

.DELETE {
  background: #3a0d0d;
  color: #ff5252;
}

.path {
  font-family: 'Fira Code', monospace;
  color: #fff;
  font-size: 0.9rem;
}

.desc {
  color: #aaa;
  line-height: 1.6;
  margin-bottom: 25px;
  border-left: 3px solid #333;
  padding-left: 15px;
}

.playground-box {
  background: #000;
  border-radius: 8px;
  border: 1px solid #222;
  overflow: hidden;
}

.playground-header {
  background: #111;
  padding: 10px 15px;
  font-size: 0.75rem;
  color: #555;
  text-transform: uppercase;
  font-weight: bold;
  border-bottom: 1px solid #222;
}

.playground-body {
  padding: 20px;
}

.params-section,
.body-section,
.schema-section {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: 0.75rem;
  color: #555;
  margin-bottom: 8px;
  font-weight: bold;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.input-row span {
  font-size: 0.8rem;
  color: #888;
  width: 100px;
}

input,
textarea {
  background: #0a0a0a;
  border: 1px solid #333;
  color: #4ade80;
  padding: 8px;
  border-radius: 4px;
  width: 100%;
  font-family: monospace;
  font-size: 0.85rem;
}

.schema-code {
  background: #050505;
  padding: 15px;
  border-radius: 4px;
  border: 1px dashed #333;
  color: #666;
  font-size: 0.8rem;
  overflow-x: auto;
}

.test-btn {
  background: #4ade80;
  color: #000;
  border: none;
  padding: 10px 25px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}

.test-btn:hover {
  opacity: 0.8;
}

.result-section {
  border-top: 1px solid #222;
}

.result-header {
  padding: 10px 20px;
  font-size: 0.75rem;
  font-weight: bold;
}

.result-header.ok {
  background: #003311;
  color: #4ade80;
}

.result-header.err {
  background: #330000;
  color: #ff5252;
}

.result-code {
  padding: 20px;
  background: #000;
  color: #81d4fa;
  font-size: 0.85rem;
  max-height: 400px;
  overflow-y: auto;
}
</style>
