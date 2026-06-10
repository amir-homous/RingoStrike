import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Challenges from "../views/Challenges.vue";
import AuthCallback from "../views/AuthCallback.vue";
import Enrollment from "../views/Enrollment.vue";
import Leaderboard from "../views/Leaderboard.vue"
import Onboarding from "../views/Onboarding.vue";
import api from "../lib/api";
import AuthForm from '../components/AuthForm.vue'
import { createAuthGuard } from "./authGuard";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;

    if (to.hash) {
      return {
        el: to.hash,
        top: 108,
        behavior: "smooth",
      };
    }

    return { top: 0 };
  },
  routes: [
    { path: "/login", component: AuthForm,meta: { requiresAuth: false } },
    { path: "/auth/callback", component: AuthCallback },
    { path: "/onboarding", component: Onboarding, meta: { requiresAuth: true } },
    { path: "/dashboard", component: Dashboard ,meta: { requiresAuth: true }},
    { path: "/paths", component: () => import("../views/Paths.vue"), meta: { requiresAuth: true } },
    { path: "/challenges", component: Challenges },
    { path: "/profile", component: () => import("../views/Profile.vue"), meta: { requiresAuth: true } },
    { path: "/enrollment/:id", component: Enrollment, props: true },
    { path: "/enrollment/:id/leaderboard", component: Leaderboard, props: true },
    { path: "/u/:username",component: () => import("../views/PublicProfile.vue"),meta: { requiresAuth: false },},
    
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



router.beforeEach(createAuthGuard(api));

export default router;
