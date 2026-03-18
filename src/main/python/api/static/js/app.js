const ALL_TAGS = [
  "咖啡好喝", "讀書", "不限時", "插座", "有鹹食",
  "外帶店", "wifi", "寵物友善", "甜點", "自家烘焙", "景觀", "深夜", "早晨"
];

let activeTags = new Set();
let currentShops = [];
let userLocation  = null;   // { lat, lng } — set by GPS search or on-demand

// ── Init ──────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  buildTagPills();
  loadCities();
  document.getElementById("modal-overlay").addEventListener("click", e => {
    if (e.target === e.currentTarget) closeModal();
  });
});

// ── Cities & Districts ────────────────────────────────
async function loadCities() {
  const sel = document.getElementById("city-select");
  try {
    const res = await fetch("/api/cities");
    const { cities } = await res.json();
    cities.forEach(c => {
      const opt = document.createElement("option");
      opt.value = opt.textContent = c;
      sel.appendChild(opt);
    });
  } catch (e) { console.error("Failed to load cities", e); }
}

async function onCityChange() {
  const city = document.getElementById("city-select").value;
  const distSel = document.getElementById("district-select");
  distSel.innerHTML = "<option value=''>— 選擇行政區 —</option>";
  distSel.disabled = !city;
  document.getElementById("result-count").textContent = "";
  if (!city) return;
  try {
    const res = await fetch(`/api/districts?city=${encodeURIComponent(city)}`);
    const { districts } = await res.json();
    districts.forEach(d => {
      const opt = document.createElement("option");
      opt.value = opt.textContent = d;
      distSel.appendChild(opt);
    });
  } catch (e) { console.error("Failed to load districts", e); }
}

// ── Tag pills ─────────────────────────────────────────
function buildTagPills() {
  const container = document.getElementById("tag-filters");
  ALL_TAGS.forEach(tag => {
    const pill = document.createElement("button");
    pill.className = "tag-pill";
    pill.textContent = tag;
    pill.addEventListener("click", () => toggleTag(tag, pill));
    container.appendChild(pill);
  });
}

function toggleTag(tag, pill) {
  if (activeTags.has(tag)) { activeTags.delete(tag); pill.classList.remove("active"); }
  else                      { activeTags.add(tag);    pill.classList.add("active"); }
}

// ── Search by district ────────────────────────────────
async function searchShops() {
  const city     = document.getElementById("city-select").value;
  const district = document.getElementById("district-select").value;
  if (!city)     { alert("請選擇縣市"); return; }
  if (!district) { alert("請選擇行政區"); return; }

  setLoading(true);
  const params = new URLSearchParams({ city, district });
  if (activeTags.size) params.set("tags", [...activeTags].join(","));

  try {
    const res = await fetch(`/api/shops?${params}`);
    if (!res.ok) { const e = await res.json(); throw new Error(e.error); }
    const data = await res.json();
    handleResults(data.shops, `${city} ${district}`);
  } catch (e) { showError(e.message); }
  finally     { setLoading(false); }
}

// ── Search by location ────────────────────────────────
async function searchByLocation() {
  if (!navigator.geolocation) { alert("您的瀏覽器不支援定位功能"); return; }

  const btn = document.getElementById("location-btn");
  btn.disabled = true;
  btn.textContent = "📍 定位中…";
  showLoading();

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const { latitude, longitude } = pos.coords;
      userLocation = { lat: latitude, lng: longitude };
      setLoading(true);
      const params = new URLSearchParams({ lat: latitude, lng: longitude });
      if (activeTags.size) params.set("tags", [...activeTags].join(","));
      try {
        const res = await fetch(`/api/shops/nearby?${params}`);
        if (!res.ok) { const e = await res.json(); throw new Error(e.error); }
        const data = await res.json();
        handleResults(data.shops, "目前位置附近");
      } catch (e) { showError(e.message); }
      finally {
        setLoading(false);
        btn.disabled = false;
        btn.textContent = "📍 使用目前位置";
      }
    },
    (err) => {
      alert("無法取得位置：" + err.message);
      btn.disabled = false;
      btn.textContent = "📍 使用目前位置";
    },
    { timeout: 10000 }
  );
}

// ── Handle results (sort + open-now filter + render) ──
async function handleResults(shops, label) {
  // Open-now filter
  const onlyOpen = document.getElementById("open-now-toggle").checked;
  if (onlyOpen) shops = shops.filter(s => s.is_open_now === true);

  // Sort
  const sort = document.getElementById("sort-select").value;
  if (sort === "rating_desc") {
    shops = [...shops].sort((a, b) => b.rating - a.rating);
  } else if (sort === "rating_asc") {
    shops = [...shops].sort((a, b) => a.rating - b.rating);
  } else if (sort === "distance") {
    // Request location if we don't have it yet
    if (!userLocation) {
      userLocation = await requestLocation();
    }
    if (userLocation) {
      shops = [...shops]
        .filter(s => s.lat && s.lng)
        .sort((a, b) => haversine(userLocation, a) - haversine(userLocation, b));
    }
  }

  currentShops = shops;
  renderShops(shops, label);
  document.getElementById("result-count").textContent =
    `找到 ${shops.length} 間咖啡廳${onlyOpen ? "（營業中）" : ""}`;
}

function requestLocation() {
  return new Promise(resolve => {
    if (!navigator.geolocation) { resolve(null); return; }
    navigator.geolocation.getCurrentPosition(
      pos => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      ()  => resolve(null),
      { timeout: 8000 }
    );
  });
}

// Haversine distance in km between userLocation and shop
function haversine(from, shop) {
  const R = 6371;
  const dLat = (shop.lat - from.lat) * Math.PI / 180;
  const dLng = (shop.lng - from.lng) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2 +
            Math.cos(from.lat * Math.PI/180) * Math.cos(shop.lat * Math.PI/180) *
            Math.sin(dLng/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

// ── Render grid ───────────────────────────────────────
function renderShops(shops, label) {
  const main = document.getElementById("main-content");
  if (!shops.length) {
    main.innerHTML = `<div class="state-msg"><div class="icon">☕</div><p>${label} 沒有符合條件的咖啡廳</p></div>`;
    return;
  }
  const grid = document.createElement("div");
  grid.className = "shop-grid";
  shops.forEach((shop, i) => grid.appendChild(buildCard(shop, i)));
  main.innerHTML = "";
  main.appendChild(grid);
}

function buildCard(shop, index) {
  const card = document.createElement("div");
  card.className = "shop-card";
  card.addEventListener("click", () => openModal(index));

  const photoHTML = shop.photos?.[0]
    ? `<div class="card-photo"><img src="${shop.photos[0]}" alt="${shop.name}" loading="lazy" onerror="this.parentElement.innerHTML='☕'"></div>`
    : `<div class="card-photo">☕</div>`;

  const openBadge = shop.is_open_now === true  ? `<span class="open-badge open">營業中</span>`
                  : shop.is_open_now === false ? `<span class="open-badge closed">已打烊</span>`
                  : "";

  const tags = (shop.tags || []).slice(0, 4).map(t => `<span class="card-tag">${t}</span>`).join("");

  const distHTML = (userLocation && shop.lat && shop.lng)
    ? `<span class="card-dist">📍 ${(haversine(userLocation, shop) * 1000).toFixed(0)} m</span>`
    : "";

  card.innerHTML = `
    ${photoHTML}
    <div class="card-body">
      <div class="card-name-row">
        <div class="card-name" title="${shop.name}">${shop.name}</div>
        ${openBadge}
      </div>
      <div class="card-rating">
        <span class="stars">${starsHTML(shop.rating)}</span>
        <span>${shop.rating} (${(shop.total_ratings||0).toLocaleString()}則評論)</span>
        ${distHTML}
      </div>
      <div class="card-tags">${tags}</div>
      <div class="card-address" title="${shop.address}">${shop.address}</div>
    </div>`;
  return card;
}

// ── Modal ─────────────────────────────────────────────
async function openModal(index) {
  const shop    = currentShops[index];
  const overlay = document.getElementById("modal-overlay");
  const modal   = document.getElementById("modal");
  renderModal(modal, shop, null);
  overlay.classList.add("open");
  try {
    const res = await fetch(`/api/shops/${shop.place_id}`);
    if (res.ok) {
      const full = await res.json();
      currentShops[index] = full;
      renderModal(modal, full, full.articles);
    }
  } catch (_) {}
}

function renderModal(modal, shop, articles) {
  const photoHTML = shop.photos?.[0]
    ? `<div class="modal-photo"><img src="${shop.photos[0]}" alt="${shop.name}" onerror="this.parentElement.innerHTML='☕'"></div>`
    : `<div class="modal-photo">☕</div>`;

  const openBadge = shop.is_open_now === true  ? `<span class="open-badge open">營業中</span>`
                  : shop.is_open_now === false ? `<span class="open-badge closed">已打烊</span>`
                  : "";

  const tags       = (shop.tags || []).map(t => `<span class="modal-tag">${t}</span>`).join("");
  const hoursHTML  = shop.opening_hours?.length
    ? shop.opening_hours.map(h => `<div class="modal-info"><strong></strong>${h}</div>`).join("")
    : `<div class="modal-info">營業時間未提供</div>`;
  const highReviews  = renderReviews(shop.high_reviews, "⭐ 好評");
  const lowReviews   = renderReviews(shop.low_reviews,  "💬 負評");
  const articlesHTML = renderArticles(articles);

  const mapURL = shop.lat
    ? `https://www.google.com/maps/search/?api=1&query=${shop.lat},${shop.lng}&query_place_id=${shop.place_id}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(shop.name + " " + shop.address)}`;

  modal.innerHTML = `
    ${photoHTML}
    <div class="modal-body">
      <div class="modal-header">
        <div class="modal-name">${shop.name} ${openBadge}</div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-rating">
        <span class="stars">${starsHTML(shop.rating)}</span>
        <span>${shop.rating} (${(shop.total_ratings||0).toLocaleString()}則評論)</span>
      </div>
      <div class="modal-tags">${tags}</div>
      <div class="modal-info"><strong>地址</strong>${shop.address}</div>
      ${shop.phone   ? `<div class="modal-info"><strong>電話</strong>${shop.phone}</div>` : ""}
      ${shop.website ? `<div class="modal-info"><strong>網站</strong><a href="${shop.website}" target="_blank">${shop.website}</a></div>` : ""}
      <hr class="divider">
      <div class="modal-info"><strong>營業時間</strong></div>
      ${hoursHTML}
      <hr class="divider">
      ${highReviews}
      ${lowReviews}
      ${articlesHTML}
      <a class="map-link" href="${mapURL}" target="_blank">🗺 在 Google Maps 查看</a>
    </div>`;
}

function closeModal() {
  document.getElementById("modal-overlay").classList.remove("open");
}

function renderReviews(reviews, title) {
  if (!reviews?.length) return "";
  const items = reviews.slice(0, 3).map(r => `
    <div class="review-block">
      <div class="review-header">
        <span class="review-author">${r.author}</span>
        <span class="stars">${starsHTML(r.rating)}</span>
        <span class="review-time">${r.time}</span>
      </div>
      <div class="review-text">${r.text || "（無文字評論）"}</div>
    </div>`).join("");
  return `<div class="reviews-section"><h3>${title}</h3>${items}</div>`;
}

function renderArticles(articles) {
  if (!articles) return `<hr class="divider"><div class="reviews-section"><h3>📰 相關文章</h3><div class="no-reviews">載入中…</div></div>`;
  if (!articles.length) return "";
  const items = articles.map(a => `
    <div class="article-item">
      <a href="${a.url}" target="_blank" rel="noopener">${a.title}</a>
      <span class="article-source">${a.source}</span>
    </div>`).join("");
  return `<hr class="divider"><div class="reviews-section"><h3>📰 相關文章</h3>${items}</div>`;
}

// ── Helpers ───────────────────────────────────────────
function starsHTML(rating) {
  const full  = Math.floor(rating || 0);
  const half  = (rating || 0) - full >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
}

function setLoading(on) {
  document.getElementById("search-btn").disabled = on;
  document.getElementById("search-btn").textContent = on ? "搜尋中…" : "搜尋咖啡廳";
  if (on) showLoading();
}

function showLoading() {
  document.getElementById("main-content").innerHTML = `
    <div class="state-msg"><div class="spinner"></div><p>正在搜尋咖啡廳…</p></div>`;
}

function showError(msg) {
  document.getElementById("main-content").innerHTML = `
    <div class="state-msg"><div class="icon">⚠️</div><p>搜尋失敗：${msg}</p></div>`;
}
