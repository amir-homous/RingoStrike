import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Dashboard from "../views/Dashboard.vue";
import Challenges from "../views/Challenges.vue";
import AuthCallback from "../views/AuthCallback.vue";
import Enrollment from "../views/Enrollment.vue";
import Leaderboard from "../views/Leaderboard.vue"
import api from "../lib/api";
import AuthForm from '../components/AuthForm.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/login", component: AuthForm,meta: { requiresAuth: false } },
    { path: "/auth/callback", component: AuthCallback },
    { path: "/dashboard", component: Dashboard ,meta: { requiresAuth: true }},
    { path: "/challenges", component: Challenges },
    { path: "/enrollment/:id", component: Enrollment, props: true },
    { path: "/enrollment/:id/leaderboard", component: Leaderboard, props: true },
    { path: "/", redirect: "/dashboard" },
    // (اختیاری) صفحه 404 واقعی بعداً می‌سازیم
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
    // اضافه کردن صفحه داکیومنت (بدون نیاز به لاگین برای راحتی خودت)
    { 
      path: '/docs', 
      name: 'ApiDocs', 
      component: () => import('../views/ApiDocsView.vue'),
      meta: { requiresAuth: false } 
    },
  ],
});



router.beforeEach(async (to) => {
  // 1. اگر مسیر صراحتاً گفته نیاز به لاگین ندارد، اجازه عبور بده
  // این شامل /login, /auth/callback و /docs می‌شود
  if (to.meta.requiresAuth === false) {
    return true;
  }

  try {
    // 2. برای بقیه مسیرها (که یا true هستند یا تعریف نشده‌اند) لاگین را چک کن
    await api.get("/me");
    return true;
  } catch (e) {
    // 3. اگر لاگین نبود، بفرست به صفحه لاگین
    return { path: "/login", query: { next: to.fullPath } };
  }
});

export default router;
