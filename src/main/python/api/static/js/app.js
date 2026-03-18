const ALL_TAGS = [
  "讀書", "不限時", "外帶店", "wifi", "插座",
  "寵物友善", "甜點", "自家烘焙", "景觀", "咖啡好喝"
];

let activeTags = new Set();
let currentShops = [];

// ── Init ──────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  buildTagPills();
  loadDistricts();
});

// ── Districts ─────────────────────────────────────────
async function loadDistricts() {
  const sel = document.getElementById("district-select");
  try {
    const res = await fetch("/api/districts");
    const { districts } = await res.json();
    districts.forEach(d => {
      const opt = document.createElement("option");
      opt.value = opt.textContent = d;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error("Failed to load districts", e);
  }
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
  if (activeTags.has(tag)) {
    activeTags.delete(tag);
    pill.classList.remove("active");
  } else {
    activeTags.add(tag);
    pill.classList.add("active");
  }
}

// ── Search ────────────────────────────────────────────
async function searchShops() {
  const district = document.getElementById("district-select").value;
  if (!district) { alert("請選擇行政區"); return; }

  const btn = document.getElementById("search-btn");
  btn.disabled = true;
  btn.textContent = "搜尋中…";
  showLoading();

  const params = new URLSearchParams({ district });
  if (activeTags.size) params.set("tags", [...activeTags].join(","));

  try {
    const res = await fetch(`/api/shops?${params}`);
    if (!res.ok) { const e = await res.json(); throw new Error(e.error); }
    const data = await res.json();
    currentShops = data.shops;
    renderShops(data.shops, district);
    document.getElementById("result-count").textContent =
      `找到 ${data.count} 間咖啡廳`;
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "搜尋咖啡廳";
  }
}

// ── Render grid ───────────────────────────────────────
function renderShops(shops, district) {
  const main = document.getElementById("main-content");
  if (!shops.length) {
    main.innerHTML = `
      <div class="state-msg">
        <div class="icon">☕</div>
        <p>${district} 沒有符合條件的咖啡廳，試試看移除一些標籤篩選？</p>
      </div>`;
    return;
  }

  const grid = document.createElement("div");
  grid.className = "shop-grid";
  shops.forEach((shop, i) => {
    grid.appendChild(buildCard(shop, i));
  });
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

  const tags = (shop.tags || []).slice(0, 4)
    .map(t => `<span class="card-tag">${t}</span>`).join("");

  card.innerHTML = `
    ${photoHTML}
    <div class="card-body">
      <div class="card-name" title="${shop.name}">${shop.name}</div>
      <div class="card-rating">
        <span class="stars">${starsHTML(shop.rating)}</span>
        <span>${shop.rating} (${shop.total_ratings.toLocaleString()}則評論)</span>
      </div>
      <div class="card-tags">${tags}</div>
      <div class="card-address" title="${shop.address}">${shop.address}</div>
    </div>`;
  return card;
}

// ── Modal ─────────────────────────────────────────────
async function openModal(index) {
  const shop = currentShops[index];
  const overlay = document.getElementById("modal-overlay");
  const modal   = document.getElementById("modal");

  // Show modal immediately with basic info, then load articles
  renderModal(modal, shop, null);
  overlay.classList.add("open");

  // Fetch full details + articles from /api/shops/<place_id>
  try {
    const res = await fetch(`/api/shops/${shop.place_id}`);
    if (res.ok) {
      const full = await res.json();
      currentShops[index] = full;   // update cache
      renderModal(modal, full, full.articles);
    }
  } catch (_) { /* keep showing basic info */ }
}

function renderModal(modal, shop, articles) {

  const photoHTML = shop.photos?.[0]
    ? `<div class="modal-photo"><img src="${shop.photos[0]}" alt="${shop.name}" onerror="this.parentElement.innerHTML='☕'"></div>`
    : `<div class="modal-photo">☕</div>`;

  const tags = (shop.tags || [])
    .map(t => `<span class="modal-tag">${t}</span>`).join("");

  const hoursHTML = shop.opening_hours?.length
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
        <div class="modal-name">${shop.name}</div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-rating">
        <span class="stars">${starsHTML(shop.rating)}</span>
        <span>${shop.rating} (${shop.total_ratings.toLocaleString()}則評論)</span>
      </div>
      <div class="modal-tags">${tags}</div>
      <div class="modal-info"><strong>地址</strong>${shop.address}</div>
      ${shop.phone ? `<div class="modal-info"><strong>電話</strong>${shop.phone}</div>` : ""}
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

  overlay.classList.add("open");
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

// ── Helpers ───────────────────────────────────────────
function starsHTML(rating) {
  const full  = Math.floor(rating);
  const half  = rating - full >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
}

function showLoading() {
  document.getElementById("main-content").innerHTML = `
    <div class="state-msg">
      <div class="spinner"></div>
      <p>正在搜尋咖啡廳…</p>
    </div>`;
}

function showError(msg) {
  document.getElementById("main-content").innerHTML = `
    <div class="state-msg">
      <div class="icon">⚠️</div>
      <p>搜尋失敗：${msg}</p>
    </div>`;
}

// Close modal on overlay click
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("modal-overlay").addEventListener("click", e => {
    if (e.target === e.currentTarget) closeModal();
  });
});
