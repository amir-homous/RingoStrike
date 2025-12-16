import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Dashboard from "../views/Dashboard.vue";
import Challenge from "../views/Challenge.vue";
import Challenges from "../views/Challenges.vue";
import AuthCallback from "../views/AuthCallback.vue";
import Enrollment from "../views/Enrollment.vue";
import api from "../lib/api";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/login", component: Login },
    { path: "/auth/callback", component: AuthCallback },
    { path: "/dashboard", component: Dashboard },
    { path: "/challenges", component: Challenge },
    { path: "/enrollment/:id", component: Enrollment, props: true },
    { path: "/", redirect: "/dashboard" },
    // (اختیاری) صفحه 404 واقعی بعداً می‌سازیم
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
  ],
});

router.beforeEach(async (to) => {
  // ✅ این صفحات نیاز به auth ندارند
  if (to.path === "/login" || to.path === "/auth/callback") return true;

  try {
    // ✅ اگر کوکی معتبر باشد 200 می‌دهد
    await api.get("/me");
    return true;
  } catch (e) {
    // ✅ اگر لاگین نیست، بفرست به login و مسیر مقصد را نگه دار
    return { path: "/login", query: { next: to.fullPath } };
  }
});

export default router;
