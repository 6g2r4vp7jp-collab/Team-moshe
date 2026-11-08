/* OR MOSHE BRAND dashboard. Read-only view of the repo's CSV/JSON data (see tools/build_dashboard.py). */
(function () {
  "use strict";
  var D = window.DASHBOARD_DATA;
  if (!D) {
    document.querySelector("main").innerHTML = '<div class="banner">אין נתונים. הרץ: python3 tools/build_dashboard.py</div>';
    return;
  }

  var TABS = [
    ["home", "🏠", "סקירה"], ["calendar", "🗓️", "לוח תוכן"], ["reels", "🎬", "רילס"],
    ["stats", "📊", "סטטיסטיקות"], ["sponsors", "🤝", "ספונסרים"], ["club", "🥊", "מכון"]
  ];
  var STATUS = {
    idea: ["רעיון", ""], draft: ["טיוטה", "warn"], ready: ["מוכן, ממתין לאישור", "gold"], approved: ["מאושר", "ok"],
    published: ["פורסם", "ok"], open: ["פתוח", "warn"], done: ["בוצע", "ok"],
    research: ["מחקר", ""], approved_to_send: ["אושר לשליחה", "gold"], sent: ["נשלח", "warn"],
    replied: ["ענו", "ok"], meeting: ["פגישה", "ok"], won: ["נסגר ✓", "ok"], lost: ["לא רלוונטי", "bad"], no_reply: ["אין מענה", "bad"],
    "new": ["חדש", "warn"], contacted: ["נוצר קשר", ""], trial_booked: ["נקבע ניסיון", "gold"], trial_done: ["היה בניסיון", "gold"],
    joined: ["הצטרף ✓", "ok"], not_now: ["לא עכשיו", ""]
  };
  var PILLAR = { fighter: "לוחם", coach: "מאמן", club: "Team Moshe", behind: "מאחורי הקלעים", cta: "הנעה לפעולה" };
  var FORMAT = { reel: "רילס", story: "סטורי", carousel: "קרוסלה", post: "פוסט" };
  var DAYS = ["א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳"];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function pill(st) { var s = STATUS[st] || [st || "—", ""]; return '<span class="pill ' + s[1] + '">' + esc(s[0]) + "</span>"; }
  function sampleTag(on) { return on ? '<span class="sample">דוגמה</span>' : ""; }
  function isSample(r) { return r.is_sample === "yes" || /\[דוגמה\]/.test(JSON.stringify(r)); }
  function dt(s) { var p = String(s).split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function when(s) {
    if (!s) return '<div class="when">—</div>';
    var d = dt(s);
    return '<div class="when">' + d.getDate() + "." + (d.getMonth() + 1) + "<b>" + DAYS[d.getDay()] + "</b></div>";
  }
  function num(v, dec) {
    if (v === null || v === undefined || v === "") return '<span class="muted">חסר</span>';
    return Number(v).toLocaleString("he-IL", { maximumFractionDigits: dec || 0 });
  }
  function empty(t) { return '<div class="empty">' + esc(t) + "</div>"; }

  /* ---------- tooltip (hover on desktop, tap on touch) ---------- */
  var tip = document.getElementById("tip");
  function showTip(el, x, y) {
    tip.innerHTML = el.getAttribute("data-tip");
    tip.style.display = "block";
    var w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.max(8, Math.min(window.innerWidth - w - 8, x - w / 2)) + "px";
    tip.style.top = Math.max(8, y - h - 14) + "px";
  }
  document.addEventListener("mousemove", function (e) {
    var el = e.target.closest && e.target.closest("[data-tip]");
    if (el) showTip(el, e.clientX, e.clientY); else tip.style.display = "none";
  });
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-tip]");
    if (el) { var r = el.getBoundingClientRect(); showTip(el, r.left + r.width / 2, r.top); } else tip.style.display = "none";
  });
  document.addEventListener("focusin", function (e) {
    var el = e.target.closest && e.target.closest("[data-tip]");
    if (el) { var r = el.getBoundingClientRect(); showTip(el, r.left + r.width / 2, r.top); }
  });

  /* Single-series horizontal bars: one hue (gold), label + value always printed so color never carries meaning alone. */
  function bars(items, valueKey, labelFn, tipFn, dec) {
    var max = 0;
    items.forEach(function (i) { if (+i[valueKey] > max) max = +i[valueKey]; });
    if (!items.length) return empty("אין נתונים");
    return '<div class="chart">' + items.map(function (i) {
      var v = i[valueKey], w = max && v != null && v !== "" ? Math.max(1, (+v / max) * 100) : 0;
      return '<div class="bar-row" tabindex="0" data-tip="' + esc(tipFn(i)) + '"><div class="lab">' + esc(labelFn(i)) +
        '</div><div class="bar-track"><div class="bar" style="width:' + w + '%"></div></div><div class="num">' + num(v, dec) + "</div></div>";
    }).join("") + "</div>";
  }

  function calItem(r, full) {
    var meta = [FORMAT[r.format] || r.format, PILLAR[r.pillar] || r.pillar, r.platform].filter(Boolean).join(" · ");
    var h = '<li>' + when(r.date) + '<div class="grow"><div class="t">' + esc(r.title) + " " + pill(r.status) + sampleTag(isSample(r)) +
      '</div><div class="s">' + esc(meta) + "</div>";
    if (r.hook) h += '<div class="s">🎯 הוק: ' + esc(r.hook) + "</div>";
    if (full) {
      var cap = r.caption_he || r.caption_en;
      if (cap) h += '<div class="cap">' + esc(r.caption_he) + (r.caption_he && r.caption_en ? "\n\n" : "") + esc(r.caption_en) +
        '</div><button class="copy" data-copy="' + esc(cap) + '">העתק כיתוב</button>';
      if (r.cta) h += '<div class="s">📣 ' + esc(r.cta) + "</div>";
      if (r.assets) h += '<div class="s">📁 ' + esc(r.assets) + "</div>";
      if (r.notes) h += '<div class="s">📝 ' + esc(r.notes) + "</div>";
    }
    return h + "</div></li>";
  }

  /* ---------- tabs ---------- */
  function home() {
    var rep = D.report, v = D.verification;
    var h = "<h2>השבוע</h2>";
    if (v.verified < v.total) h += '<div class="banner">⚠️ ' + (v.total - v.verified) + " מתוך " + v.total +
      " ההישגים עדיין לא אומתו (brand/achievements.json). אין לשלוח חומר חיצוני לפני אימות.</div>";
    var ready = D.ready.length, ideas = D.reel_ideas.length, open = D.tasks.filter(function (t) { return t.status !== "done"; }).length;
    var leadsOpen = D.leads.filter(function (l) { return ["new", "contacted", "trial_booked", "trial_done"].indexOf(l.status) >= 0; }).length;
    h += '<div class="grid">' +
      tile(ready, "מוכנים לפרסום", "ממתינים לאישור") + tile(ideas, "רעיונות לרילס", "בלוח התוכן") +
      tile(open, "משימות פתוחות", D.week_tasks.length + " השבוע") +
      tile(leadsOpen, "פניות פתוחות למכון", D.leads.some(isSample) ? "כולל דוגמה" : "") + "</div>";
    h += "<h2>משימות לשבוע הקרוב</h2><div class='card'><ul class='list'>" +
      (D.week_tasks.length ? D.week_tasks.map(function (t) {
        return "<li>" + when(t.due) + '<div class="grow"><div class="t">' + esc(t.task) + "</div><div class='s'>" + esc(t.owner) + " · " + esc(t.area) +
          (t.needs_approval === "yes" ? ' · <span class="pill gold">דורש אישור</span>' : "") + (t.notes ? " · " + esc(t.notes) : "") + "</div></div></li>";
      }).join("") : "<li>" + empty("אין משימות בשבוע הקרוב") + "</li>") + "</ul></div>";
    h += "<h2>מעקבים שמגיע זמנם</h2><div class='card'><ul class='list'>" +
      (D.followups.length ? D.followups.map(function (f) {
        return "<li>" + when(f.date) + '<div class="grow"><div class="t">' + esc(f.name) + sampleTag(f.is_sample) + "</div><div class='s'>" + esc(f.kind) + " · " + pill(f.status) +
          (f.overdue ? ' <span class="pill bad">באיחור</span>' : "") + "</div></div></li>";
      }).join("") : "<li>" + empty("אין מעקבים פתוחים") + "</li>") + "</ul></div>";
    h += "<h2>בלוח התוכן ב-7 הימים הקרובים</h2><div class='card'><ul class='list'>" +
      (D.week_calendar.length ? D.week_calendar.map(function (r) { return calItem(r, false); }).join("") : "<li>" + empty("אין פרסומים מתוכננים") + "</li>") + "</ul></div>";
    if (rep && rep.recommendations && rep.recommendations.length) {
      h += "<h2>המלצות מהדוח האחרון" + sampleTag(rep.is_sample) + "</h2><div class='card'><ol style='margin:0;padding-inline-start:20px'>" +
        rep.recommendations.map(function (r) { return "<li style='margin-bottom:6px'>" + esc(r) + "</li>"; }).join("") + "</ol></div>";
    }
    return h;
  }
  function tile(v, l, d) { return '<div class="card tile"><div class="v">' + esc(v) + '</div><div class="l">' + esc(l) + '</div><div class="d">' + esc(d || "") + "</div></div>"; }

  var calFilter = "all";
  function calendar() {
    var F = [["all", "הכל"], ["idea", "רעיונות"], ["draft", "טיוטות"], ["ready", "מוכן"], ["approved", "מאושר"], ["published", "פורסם"]];
    var rows = D.calendar.filter(function (r) { return calFilter === "all" || r.status === calFilter; });
    return "<h2>לוח תוכן: 30 יום</h2><div class='filters' role='group' aria-label='סינון לפי סטטוס'>" +
      F.map(function (f) { return '<button data-cal="' + f[0] + '" class="' + (calFilter === f[0] ? "on" : "") + '">' + f[1] + "</button>"; }).join("") +
      "</div><div class='card'><ul class='list'>" + (rows.length ? rows.map(function (r) { return calItem(r, true); }).join("") : "<li>" + empty("אין פריטים") + "</li>") + "</ul></div>";
  }

  function reels() {
    var h = "<h2>מוכנים לפרסום</h2><div class='banner'>שום דבר לא מתפרסם אוטומטית. כל פרסום רק אחרי אישור של אור.</div><div class='card'><ul class='list'>" +
      (D.ready.length ? D.ready.map(function (r) { return calItem(r, true); }).join("") : "<li>" + empty("אין עדיין") + "</li>") + "</ul></div>";
    if (D.rendered_files.length) h += "<h2>קבצים שנערכו (reels/out)</h2><div class='card'><ul class='list'>" +
      D.rendered_files.map(function (f) { return "<li><div class='grow s'>🎬 " + esc(f) + "</div></li>"; }).join("") + "</ul></div>";
    h += "<h2>רעיונות לרילס</h2><div class='cards'>" + D.reel_ideas.map(function (r) {
      return '<div class="card"><ul class="list">' + calItem(r, true) + "</ul></div>";
    }).join("") + "</div>";
    return h;
  }

  function stats() {
    var rep = D.report;
    if (!rep) return "<h2>סטטיסטיקות</h2><div class='banner'>אין עדיין דוח. הוסף ייצוא Insights ל-analytics/data והרץ python3 tools/weekly_report.py</div>";
    var h = "<h2>דוח שבועי מ-" + esc(rep.week_start.split("-").reverse().join(".")) + sampleTag(rep.is_sample) + "</h2>";
    if (rep.is_sample) h += "<div class='banner'>⚠️ <b>נתוני דוגמה</b> לבדיקת המערכת בלבד. המספרים האמיתיים יופיעו אחרי ייצוא Insights או חיבור API.</div>";
    h += '<div class="grid">' + rep.summary.map(function (s) {
      var ch = s.change_pct == null ? "" : (s.change_pct >= 0 ? "▲ " : "▼ ") + Math.abs(s.change_pct).toFixed(0) + "% משבוע קודם";
      return '<div class="card tile"><div class="v">' + num(s.current) + '</div><div class="l">' + esc(s.label) + '</div><div class="d">' + ch + "</div></div>";
    }).join("") + '<div class="card tile"><div class="v">' + (rep.avg_watch_time_sec == null ? '<span class="muted">—</span>' : num(rep.avg_watch_time_sec, 1)) +
      '</div><div class="l">זמן צפייה ממוצע (שנ׳)</div><div class="d">' + (rep.avg_watch_time_sec == null ? "לא זמין" : "רילס") + "</div></div></div>";
    var K = { followers_total: "סה״כ עוקבים", new_followers: "עוקבים חדשים", profile_visits: "כניסות לפרופיל", sponsor_inquiries: "פניות ספונסרים", club_inquiries: "פניות למכון", club_signups: "הרשמות למכון" };
    h += "<h2>חשבון ופניות</h2><div class='card scroll'><table class='tbl'><thead><tr><th>מדד</th><th>השבוע</th><th>שבוע קודם</th></tr></thead><tbody>" +
      Object.keys(K).map(function (k) { return "<tr><td>" + K[k] + "</td><td>" + num(rep.kpis[k]) + "</td><td>" + num((rep.kpis_prev || {})[k]) + "</td></tr>"; }).join("") + "</tbody></table></div>";
    h += "<h2>התכנים המובילים: ציון מעורבות</h2><div class='card'>" + bars(rep.top_posts.map(function (p) { p._s = p.score * 100; return p; }), "_s",
      function (p) { return p.title || p.post_id; },
      function (p) { return "<b>" + esc(p.title) + "</b><br>צפיות " + num(p.views) + " · חשיפה " + num(p.reach) + "<br>שיתופים " + num(p.shares) + " · שמירות " + num(p.saves) + " · מעקבים " + num(p.follows); }, 2) +
      "<div class='s' style='margin-top:6px'>ציון = (שיתופים×3 + שמירות×2 + תגובות + מעקבים×4) ÷ חשיפה × 100</div></div>";
    h += "<h2>לפי עמוד תוכן</h2><div class='card'>" + bars(rep.by_pillar.map(function (p) { p._s = p.avg_score == null ? null : p.avg_score * 100; return p; }), "_s",
      function (p) { return (PILLAR[p.key] || p.key || "לא מסווג") + " (" + p.posts + ")"; },
      function (p) { return "<b>" + esc(PILLAR[p.key] || p.key) + "</b><br>" + p.posts + " פוסטים · חשיפה " + num(p.reach) + " · צפיות " + num(p.views); }, 2) + "</div>";
    h += "<h2>המלצות</h2><div class='card'><ol style='margin:0;padding-inline-start:20px'>" + rep.recommendations.map(function (r) { return "<li style='margin-bottom:6px'>" + esc(r) + "</li>"; }).join("") + "</ol></div>";
    h += "<p class='s muted'>מקור: " + esc(rep.file) + "</p>";
    return h;
  }

  function crmTable(rows, cols) {
    if (!rows.length) return empty("אין רשומות");
    return "<div class='scroll'><table class='tbl'><thead><tr>" + cols.map(function (c) { return "<th>" + c[1] + "</th>"; }).join("") + "</tr></thead><tbody>" +
      rows.map(function (r) {
        return "<tr>" + cols.map(function (c, i) {
          var v = c[0] === "status" ? pill(r.status) : esc(r[c[0]] || "");
          return "<td>" + v + (i === 0 ? sampleTag(isSample(r)) : "") + "</td>";
        }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  }
  function sponsors() {
    return "<h2>ספונסרים</h2><div class='banner'>שום פנייה לא נשלחת בלי אישור מפורש של אור. ⚠️ לאמת תארים לפני שליחה.</div><div class='card'>" +
      crmTable(D.sponsors, [["company", "חברה"], ["category", "תחום"], ["status", "סטטוס"], ["package", "חבילה"], ["next_followup", "מעקב הבא"], ["notes", "הערות"]]) +
      "</div><h2>ארגונים ומאצ'מייקרים</h2><div class='card'>" +
      crmTable(D.promotions, [["organization", "ארגון"], ["country", "מדינה"], ["status", "סטטוס"], ["verified_contact", "ערוץ מאומת"], ["next_followup", "מעקב הבא"], ["notes", "הערות"]]) + "</div>";
  }
  function club() {
    var order = ["new", "contacted", "trial_booked", "trial_done", "joined", "not_now", "lost"];
    var funnel = order.filter(function (k) { return D.lead_funnel[k]; }).map(function (k) { return { k: k, n: D.lead_funnel[k] }; });
    return "<h2>משפך פניות למכון" + sampleTag(D.leads.some(isSample)) + "</h2><div class='card'>" +
      bars(funnel, "n", function (f) { return (STATUS[f.k] || [f.k])[0]; }, function (f) { return esc((STATUS[f.k] || [f.k])[0]) + ": " + f.n + " פניות"; }) +
      "</div><h2>מעקב פניות</h2><div class='card'>" +
      crmTable(D.leads, [["name", "שם"], ["date", "תאריך"], ["source", "מקור"], ["program", "תוכנית"], ["status", "סטטוס"], ["trial_date", "ניסיון"], ["next_followup", "מעקב"]]) +
      "</div><p class='s muted'>צילום ילדים רק עם הסכמה רשומה ב-crm/media_consents.csv</p>";
  }

  var R = { home: home, calendar: calendar, reels: reels, stats: stats, sponsors: sponsors, club: club };
  var cur = "home";
  try { cur = localStorage.getItem("omb_tab") || "home"; } catch (e) { /* storage may be blocked */ }
  if (!R[cur]) cur = "home";
  var nav = document.getElementById("nav");
  nav.innerHTML = TABS.map(function (t) {
    return '<button data-tab="' + t[0] + '" aria-label="' + t[2] + '"><span class="ic" aria-hidden="true">' + t[1] + "</span>" + t[2] + "</button>";
  }).join("");
  function render() {
    TABS.forEach(function (t) {
      var sec = document.getElementById("t-" + t[0]);
      sec.classList.toggle("on", t[0] === cur);
      if (t[0] === cur) sec.innerHTML = R[cur]();
    });
    [].forEach.call(nav.children, function (b) { b.classList.toggle("on", b.getAttribute("data-tab") === cur); b.setAttribute("aria-current", b.getAttribute("data-tab") === cur ? "page" : "false"); });
  }
  nav.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    cur = b.getAttribute("data-tab");
    try { localStorage.setItem("omb_tab", cur); } catch (err) { /* ignore */ }
    render(); window.scrollTo(0, 0);
  });
  document.addEventListener("click", function (e) {
    var c = e.target.closest("[data-cal]");
    if (c) { calFilter = c.getAttribute("data-cal"); render(); return; }
    var cp = e.target.closest("[data-copy]");
    if (cp && navigator.clipboard) {
      navigator.clipboard.writeText(cp.getAttribute("data-copy")).then(function () { cp.textContent = "הועתק ✓"; }, function () { cp.textContent = "ההעתקה נכשלה"; });
    }
  });
  document.getElementById("gen").textContent = "עודכן " + D.generated_at.replace("T", " ");
  render();
})();
