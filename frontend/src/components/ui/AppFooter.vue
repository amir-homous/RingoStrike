<template>
  
  <footer class="minimal-dark-footer">
    
    <div class="footer-inner">
      <div class="left">
        <span class="dot"></span>
        <router-link to="/" class="doc-link">
          RINGO STRIKE
        </router-link>
      </div>
      
      <div class="right">
        <!-- لینک کاملاً ساده و بدون کادر -->
        <router-link to="/docs" class="doc-link">
          API_REFERENCE
        </router-link>
        
      </div>
    </div>
  </footer>
</template>

<style scoped>
.minimal-dark-footer {
  width: 100%;
  background: #0a0a0a; /* مشکی خیلی تیره */
  padding: 12px 0;
  margin-top: auto;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 6px;
  height: 6px;
  background: #33ff00; /* نقطه سبز نئونی برای حس "سیستم فعال" */
  border-radius: 50%;
}

.brand {
  color: #666; /* خاکستری تیره */
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2px;
}

.doc-link {
  color: #999; /* خاکستری روشن‌تر */
  text-decoration: none;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 1px;
  transition: color 0.2s ease;
  position: relative;
}

/* افکت هاور بسیار ظریف */
.doc-link:hover {
  color: #fff;
}

/* یک خط زیرین خیلی نازک در هاور (اختیاری) */
.doc-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 1px;
  background: #33ff00;
  transition: width 0.2s ease;
}

.doc-link:hover::after {
  width: 100%;
}

@media (max-width: 480px) {
  .brand { display: none; } /* در موبایل فقط لینک بماند */
}
</style>
