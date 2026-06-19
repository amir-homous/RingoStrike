import { getMissionDisplayCopy } from "@/lib/missionDisplayCopy";

const FA_PATHS = {
  fitness: {
    title: "تناسب و انرژی",
    description: "با مأموریت‌های کوچک حرکتی، انرژی بدن و ریتم روزانه‌ات را بساز.",
  },
  learning: {
    title: "یادگیری",
    description: "کنجکاوی‌ات را به پیشرفت روزانه و قابل دیدن تبدیل کن.",
  },
  career: {
    title: "مسیر شغلی",
    description: "با بردهای کوچک روزانه، تمرکز و پیشرفت کاری‌ات را حفظ کن.",
  },
  creativity: {
    title: "خلاقیت",
    description: "با آیین‌های کوچک ساختن، هویت خلاقانه‌ات را زنده نگه دار.",
  },
  sleep: {
    title: "آرامش و خواب",
    description: "با ریست‌های کوچک، شب‌های آرام‌تر و بازیابی بهتر بساز.",
  },
};

const FA_CHALLENGES = {
  "Move Your Body": {
    name: "بدنت را حرکت بده",
    description: "با یک پیاده‌روی، تمرین، کشش یا حرکت ساده روزانه، بدن را وارد ریتم کن.",
    ringo_intro: "کوچک شروع کن. یک جلسه حرکت برای حفظ ریتم امروز کافی است.",
  },
  "Strength Starter": {
    name: "شروع قدرت",
    description: "با چند حرکت سبک وزن بدن، یک ریتم ساده قدرتی بساز.",
    ringo_intro: "لازم نیست قهرمانانه تمرین کنی. چند تکرار واقعی هم حساب می‌شود.",
  },
  "Mobility Reset": {
    name: "ریست انعطاف",
    description: "با یک مکث کوتاه روزانه، بدنت را آزادتر و نرم‌تر نگه دار.",
    ringo_intro: "بدن منعطف از یک ریست آرام شروع می‌شود.",
  },
  "Learn One Thing": {
    name: "یک چیز یاد بگیر",
    description: "هر روز یک چیز مفید بخوان، ببین، تمرین کن یا ثبت کن.",
    ringo_intro: "یک چیز مفید برای امروز کافی است تا هویت یادگیری‌ات زنده بماند.",
  },
  "Read Five Pages": {
    name: "پنج صفحه بخوان",
    description: "با هدف کوچک پنج صفحه در روز، یک ریتم آرام مطالعه بساز.",
    ringo_intro: "پنج صفحه می‌تواند حال‌وهوای یک روز را عوض کند.",
  },
  "Practice Skill": {
    name: "تمرین مهارت",
    description: "با یک بلوک تمرین متمرکز، رشد مهارتت را قابل دیدن کن.",
    ringo_intro: "تمرین وقتی تبدیل به هویت می‌شود که از روزهای معمولی هم عبور کند.",
  },
  "Deep Work Sprint": {
    name: "اسپرینت کار عمیق",
    description: "زمان تمرکزت را محافظت کن و هر روز یک جلسه کار عمیق معنادار انجام بده.",
    ringo_intro: "مسیر کاری تو با یک بلوک تمرکز محافظت‌شده شروع می‌شود.",
  },
  "Portfolio Pulse": {
    name: "نبض پورتفولیو",
    description: "هر روز یک دارایی حرفه‌ای مثل رزومه، پروفایل یا نمونه‌کار را کمی جلو ببر.",
    ringo_intro: "هویت کاری قابل دیدن، با یک مدرک کوچک در هر نوبت ساخته می‌شود.",
  },
  "Network Signal": {
    name: "سیگنال ارتباطی",
    description: "یک ارتباط یا نشانه حرفه‌ای کوچک بساز.",
    ringo_intro: "ارتباط لازم نیست سنگین باشد. یک سیگنال محترمانه کافی است.",
  },
  "Creative Spark": {
    name: "جرقه خلاقیت",
    description: "هر روز یک ایده کوچک خلاقانه بساز یا ثبت کن.",
    ringo_intro: "خلاقیت یک درِ کم‌فشار را دوست دارد.",
  },
  "Publish Tiny": {
    name: "انتشار کوچک",
    description: "به اشتراک گذاشتن یک خروجی خلاقانه کوچک را تمرین کن.",
    ringo_intro: "اشتراک‌گذاری می‌تواند آرام باشد. انتشار کوچک هم حساب می‌شود.",
  },
  "Idea Remix": {
    name: "ریمیکس ایده",
    description: "با بازآفرینی یک ایده موجود، دامنه خلاقیتت را تمرین بده.",
    ringo_intro: "ریمیکس یک راه امن برای شروع حرکت است.",
  },
  "Mind Reset": {
    name: "ریست ذهن",
    description: "برای نفس کشیدن، نوشتن، بازتاب یا شفافیت ذهنی یک مکث کوتاه روزانه داشته باش.",
    ringo_intro: "شب آرام‌تر قبل از لحظه خواب شروع می‌شود.",
  },
  "Sleep Wind Down": {
    name: "آرام‌سازی قبل خواب",
    description: "یک آیین ساده شبانه برای کم کردن سرعت روز بساز.",
    ringo_intro: "خود آرام‌سازی مأموریت است. خواب می‌تواند بعدش بیاید.",
  },
  "Morning Recovery": {
    name: "بازیابی صبحگاهی",
    description: "روز را با یک سیگنال کوچک و مهربان برای بازیابی شروع کن.",
    ringo_intro: "بازیابی در اولین دقیقه‌های صبح هم ادامه دارد.",
  },
};

const FA_MISSIONS = {
  "move-10": ["ده دقیقه حرکت کن", "ده دقیقه راه برو، کشش انجام بده یا یک تمرین سبک برو."],
  "drink-water": ["آب بنوش", "قبل یا بعد از حرکتت یک بار آب بنوش."],
  "energy-note": ["انرژی بدنت را یادداشت کن", "یک جمله کوتاه درباره حس بدنت امروز بنویس."],
  "bodyweight-set": ["یک ست وزن بدن انجام بده", "یک ست ساده اسکوات، شنا یا تمرین مرکزی بدن انجام بده."],
  "warm-up": ["آرام گرم کن", "دو دقیقه بدن را برای حرکت آماده کن."],
  "cool-down": ["آرام سرد کن", "یک دقیقه نفس بکش و بدنت را ریست کن."],
  "stretch-focus": ["یک نقطه گرفته را کشش بده", "یک بخش گرفته بدن را انتخاب کن و آرام کشش بده."],
  "posture-check": ["حالت بدنت را چک کن", "یک بار در طول روز وضعیت نشستن یا ایستادنت را ریست کن."],
  "mobility-note": ["یادداشت انعطاف بنویس", "یک جمله درباره چیزی که بهتر شد ثبت کن."],
  "learn-one-thing": ["یک چیز مفید یاد بگیر", "یک ایده مفید بخوان، ببین، تمرین کن یا ثبت کن."],
  "capture-note": ["یک یادداشت ثبت کن", "ایده را با کلمات خودت بنویس."],
  "apply-small": ["یک بار به کارش ببر", "اگر شد، ایده را در یک اقدام خیلی کوچک استفاده کن."],
  "read-five-pages": ["پنج صفحه بخوان", "پنج صفحه از یک کتاب یا مقاله مفید بخوان."],
  "highlight-one": ["یک ایده را نگه دار", "یک جمله یا ایده ارزشمند برای نگه داشتن انتخاب کن."],
  "share-insight": ["برداشتت را توضیح بده", "ایده را کوتاه برای خودت یا یک نفر دیگر توضیح بده."],
  "practice-15": ["پانزده دقیقه تمرین کن", "پانزده دقیقه متمرکز روی یک مهارت وقت بگذار."],
  "choose-drill": ["یک تمرین کوچک انتخاب کن", "به جای تمرین همه چیز، فقط یک تمرین کوچک انتخاب کن."],
  "review-progress": ["یک بهبود را مرور کن", "نام ببر چه چیزی نسبت به قبل بهتر حس شد."],
  "deep-work-block": ["یک بلوک تمرکز کامل کن", "یک بازه متمرکز بدون عوض کردن کار انجام بده."],
  "define-output": ["خروجی را مشخص کن", "قبل از شروع بنویس تمام شدن یعنی چه."],
  "close-loop": ["حلقه را ببند", "بعد از جلسه، نتیجه یا قدم بعدی را ثبت کن."],
  "improve-asset": ["یک دارایی کاری را بهتر کن", "یک مورد از پورتفولیو، رزومه، کیس‌استادی یا پروفایلت را بهتر کن."],
  "collect-proof": ["یک مدرک جمع کن", "یک اسکرین‌شات، عدد، یادداشت یا نمونه ذخیره کن."],
  "next-edit": ["ویرایش بعدی را نام ببر", "قدم کوچک بعدی برای بهتر کردنش را بنویس."],
  "send-signal": ["یک سیگنال بفرست", "به یک نفر پیام بده، تشکر کن، کامنت بگذار یا پیگیری کن."],
  "update-context": ["زمینه را ثبت کن", "یک یادداشت درباره این ارتباط یا فرصت بنویس."],
  "next-contact": ["ارتباط بعدی را انتخاب کن", "انتخاب کن دفعه بعد شاید با چه کسی ارتباط بگیری."],
  "capture-idea": ["یک ایده ثبت کن", "یک طرح، جمله، ملودی، تصویر یا مفهوم ذخیره کن."],
  "make-small": ["یک چیز کوچک بساز", "ایده را به یک خروجی خیلی کوچک تبدیل کن."],
  "archive-spark": ["جرقه را آرشیو کن", "ایده امروز را جایی بگذار که بعداً پیدایش کنی."],
  "draft-small": ["یک پیش‌نویس کوچک بساز", "یک پیش‌نویس کوچک قابل انتشار آماده کن."],
  "polish-one-pass": ["یک دور بهترش کن", "فقط یک دور بهترش کن و بعد توقف کن."],
  "share-or-save": ["منتشر یا ذخیره‌اش کن", "آن را منتشر کن یا در پوشه آماده انتشار ذخیره کن."],
  "choose-source": ["یک منبع انتخاب کن", "یک ایده، مرجع یا پرامپت برای ریمیکس انتخاب کن."],
  "remix-it": ["ریمیکسش کن", "فرمت، مخاطب، حال‌وهوا یا محدودیتش را عوض کن."],
  "save-version": ["نسخه را ذخیره کن", "ریمیکس را به عنوان مدرک تمرین نگه دار."],
  "mind-reset": ["یک لحظه ریست کن", "برای نفس کشیدن، نوشتن یا فکر آرام مکث کن."],
  "clear-one-thing": ["یک گره ذهنی را خالی کن", "یک نگرانی یا قدم بعدی را بنویس تا همراهت نیاید."],
  "soft-close": ["روز را نرم ببند", "یک کار کوچک انجام بده که به روزت بگوید می‌تواند تمام شود."],
  "dim-inputs": ["ورودی‌ها را کم کن", "قبل خواب یک منبع تحریک را کمتر کن."],
  "prepare-room": ["اتاق را آماده کن", "یک تغییر کوچک بده که خواب راحت‌تر حس شود."],
  "sleep-note": ["یادداشت خواب بنویس", "ثبت کن امشب چه چیزی کمک کرد یا مزاحم شد."],
  "morning-light": ["نور صبح بگیر", "کمی کنار نور یا بیرون برو تا بدنت ریست شود."],
  "no-rush-start": ["با عجله شروع نکن", "قبل از شیرجه زدن در کارها، یک دقیقه آرام بمان."],
  "energy-check": ["انرژی‌ات را چک کن", "سطح انرژی‌ات را بدون قضاوت ببین."],
};

const FA_RINGO_ACTIONS = {
  "Choose a path": "انتخاب مسیر",
  "View dashboard": "دیدن داشبورد",
  "Find a challenge": "پیدا کردن چالش",
  "View paths": "دیدن مسیرها",
  "Go to challenges": "رفتن به چالش‌ها",
  "Done for today": "امروز کافیه",
  "Preview next path": "دیدن مسیر بعدی",
  "Explore another path": "دیدن یک مسیر دیگر",
  "Do it now": "همین حالا انجام بده",
  "Complete anyway": "با این حال کاملش کن",
  "Finish": "کامل کن",
  "Start": "شروع کن",
  "Secure": "ثبت کن",
  "Remind me later": "بعداً یادم بنداز",
  "Choose another path": "انتخاب مسیر دیگر",
  "View path details": "دیدن جزئیات مسیر",
};

const FA_PATH_TITLES = Object.entries(FA_PATHS).reduce((items, [, value]) => {
  items[value.title] = value.title;
  return items;
}, {
  Fitness: FA_PATHS.fitness.title,
  Learning: FA_PATHS.learning.title,
  Career: FA_PATHS.career.title,
  Creativity: FA_PATHS.creativity.title,
  Sleep: FA_PATHS.sleep.title,
});

function shouldLocalize(locale) {
  return String(locale || "").toLowerCase().startsWith("fa");
}

export function localizePath(item, locale) {
  if (!item || !shouldLocalize(locale)) return item;
  const copy = FA_PATHS[item.key];
  return copy ? { ...item, ...copy } : item;
}

export function localizeChallenge(item, locale) {
  if (!item || !shouldLocalize(locale)) return item;
  const copy = FA_CHALLENGES[item.name];
  const missions = Array.isArray(item.missions)
    ? item.missions.map((mission) => localizeMission(mission, locale))
    : item.missions;

  return copy ? { ...item, ...copy, missions } : { ...item, missions };
}

export function localizeMission(item, locale) {
  if (!item || !shouldLocalize(locale)) return item;
  const displayCopy = getMissionDisplayCopy(item, locale);
  const fallbackCopy = FA_MISSIONS[item.key];
  if (!displayCopy.found && !fallbackCopy) return item;

  const [fallbackTitle, fallbackDescription] = fallbackCopy || [];
  const title = displayCopy.found ? displayCopy.title : fallbackTitle;
  const description = displayCopy.found ? displayCopy.description : fallbackDescription;
  const challenge = item.challenge_name
    ? localizeChallenge({ name: item.challenge_name }, locale)
    : null;

  return {
    ...item,
    title,
    description,
    challenge_name: challenge?.name || item.challenge_name,
    path_title: FA_PATH_TITLES[item.path_title] || item.path_title,
    ringo_message: `رینگو می‌گه: «${title}» برای مأموریت امروز کافیه.`,
  };
}

export function localizeMissionList(items, locale) {
  return Array.isArray(items) ? items.map((item) => localizeMission(item, locale)) : [];
}

export function localizeRingoAction(action, locale) {
  if (!action || !shouldLocalize(locale)) return action;

  const [prefix, title] = String(action.label || "").split(": ");
  const translatedPrefix = FA_RINGO_ACTIONS[prefix] || prefix;
  return {
    ...action,
    label: title ? `${translatedPrefix}: ${title}` : translatedPrefix,
  };
}

export function localizeRingoState(ringo, missions, locale) {
  if (!ringo || !shouldLocalize(locale)) return ringo;

  const missionById = new Map((missions || []).map((mission) => [mission.mission_id, mission]));
  const firstMission = missions?.[0];
  const primaryMission = missionById.get(ringo.primary_action?.mission_id) || firstMission;
  const missionTitle = primaryMission?.title || "یک مأموریت کوچک";
  const actionWithMissionTitle = (action) => {
    const localized = localizeRingoAction(action, locale);
    if (!localized?.mission_id) return localized;

    const mission = missionById.get(localized.mission_id);
    if (!mission?.title) return localized;

    const [prefix] = String(action?.label || "").split(": ");
    const translatedPrefix = FA_RINGO_ACTIONS[prefix] || prefix;
    return {
      ...localized,
      label: `${translatedPrefix}: ${mission.title}`,
    };
  };

  const messages = {
    new_user_no_path: "اول یک مسیر رشد انتخاب کن. من مأموریت امروزت را کوچک و روشن نگه می‌دارم.",
    path_selected_no_challenge: "مسیرت انتخاب شده. یک چالش مرتبط شروع کن تا مأموریت امروزت را راهنمایی کنم.",
    no_mission_today: "فعلاً مأموریتی برای امروز آماده نیست. چک‌این چالش فعلی هنوز مثل قبل کار می‌کند.",
    today_completed: "امروز ثبت شد. می‌تونی همین‌جا توقف کنی. اگر انرژی بیشتری داری، مسیر بعدی را فقط بررسی کن؛ لازم نیست بیشتر انجام بدهی.",
    today_reminded: `${missionTitle} برای بعداً ذخیره شده. می‌تونی مکثش را نگه داری، همین حالا انجامش بدهی، یا بدون فشار یک مسیر دیگر ببینی.`,
    today_skipped: `${missionTitle} رد شده. امروز هنوز کامل ثبت نشده، اما اگر خواستی هنوز می‌تونی انجامش بدهی.`,
    today_in_progress: `خوبه. مأموریت بعدی: ${missionTitle}. هر وقت آماده بودی کاملش کن.`,
    returning_after_break: `بعد از یک وقفه برگشتی. آرام با ${missionTitle} شروع کن و ریتمت را دوباره بساز.`,
    streak_at_risk: `ریتمت هنوز تازه است. امروز با ${missionTitle} ازش محافظت کن.`,
    today_not_started: `مأموریت امروز آماده است: ${missionTitle}. انجامش بده و بعد ثبتش کن.`,
  };

  return {
    ...ringo,
    message: messages[ringo.state] || ringo.message,
    primary_action: actionWithMissionTitle(ringo.primary_action),
    secondary_action: actionWithMissionTitle(ringo.secondary_action),
  };
}
