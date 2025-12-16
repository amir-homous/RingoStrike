import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";

// 👇 این دو تا رو اضافه کن
import "./styles/tokens.css";
import "./styles/base.css";

createApp(App)
  .use(createPinia())
  .use(router)
  .mount("#app");
