# ☕ Coffee Map — 台灣咖啡廳探索地圖

> 用技術找到你的下一個咖啡角落

---

## 一、網站網址

**正式網址：** https://coffee-map.onrender.com

| 項目 | 說明 |
|---|---|
| Render 冷啟動 | 15 分鐘無人使用後進入休眠，第一位訪客需等約 30 秒 |
| Google Maps 免費額度 | $200 / 月，約可搜尋 **256 次**（每次 ~$0.78） |
| 超出額度 | Google 會發信通知，不會自動扣款（需手動設定上限） |

---

## 二、網站功能

### 1. 雙模式搜尋
- **選擇區域**：依縣市 → 行政區搜尋（目前支援台北市 12 區、新北市 29 區）
- **目前位置**：透過瀏覽器 GPS 自動搜尋 1.5 公里內咖啡廳

### 2. 最多 30 間結果
每次搜尋最多回傳 30 間，Google Places API 分頁機制（每頁 20 間），不超過 2 頁。

### 3. 智慧標籤系統（13 個 tag）
根據 Google 評論文字與營業時間**自動推斷**，非店家手填：

| Tag | 判斷方式 |
|---|---|
| 咖啡好喝 | 評論含「咖啡好喝、great coffee」等 |
| 讀書 | 評論含「讀書、自習、安靜、study」等 |
| 不限時 | 評論含「不限時」或營業時間 ≥ 8 小時 |
| 插座 | 評論含「插座、充電、outlet」等 |
| 有鹹食 | 評論含「早午餐、三明治、pasta」等 |
| 外帶店 | 評論含「外帶、takeaway」等 |
| wifi | 評論含「wifi、無線網路」等 |
| 寵物友善 | 評論含「寵物、狗、貓、pet」等 |
| 甜點 | 評論含「甜點、蛋糕、dessert」等 |
| 自家烘焙 | 評論含「自家烘焙、手沖、精品咖啡」等 |
| 景觀 | 評論含「景觀、夜景、露天、view」等 |
| 深夜 | 任一天營業到 22:30 以後 |
| 早晨 | 任一天 10:00 以前開門 |

### 4. 多條件 AND 篩選
可同時選多個 tag，**全部符合才顯示**（非 OR 邏輯）。

### 5. 排序功能
- 預設（Google 推薦順序）
- 評分高 → 低
- 評分低 → 高
- 距離近 → 遠（需授權 GPS）

### 6. 僅顯示營業中
勾選後自動過濾目前已打烊的店家，資料來自 Google 即時 `open_now` 欄位。

### 7. 店家詳細資訊（點卡片後載入）
- 地址、電話、官網
- 每天完整營業時間
- 全部 tag
- ⭐ 好評（4-5 星）節錄
- 💬 負評（1-2 星）節錄
- Google Maps 導航連結

### 8. 相關文章連結
點開店家後，自動搜尋 DuckDuckGo，從 ifoodie.tw、tripadvisor、trip.com 等平台抓取評測文章連結。

### 9. 距離顯示
有 GPS 位置時，每張卡片顯示與你的距離（公尺）。

---

## 三、使用工具與技術

### 後端
| 工具 | 用途 |
|---|---|
| **Python 3.9** | 主要程式語言 |
| **Flask** | Web framework，提供 API endpoints 與頁面渲染 |
| **Gunicorn** | 生產環境 WSGI server |
| **requests** | 呼叫 Google Maps API、DuckDuckGo 搜尋 |
| **BeautifulSoup4** | 解析 DuckDuckGo HTML 抓取文章連結 |
| **python-dotenv** | 從 `.env` 載入 API key |

### 外部 API
| API | 用途 | 費用 |
|---|---|---|
| Google Places Text Search | 依關鍵字搜尋咖啡廳 | $32 / 1,000 次 |
| Google Places Nearby Search | 依 GPS 座標搜尋 | $32 / 1,000 次 |
| Google Places Details | 取得電話、營業時間、評論 | $17 / 1,000 次 |
| Google Places Photos | 店家照片 | $7 / 1,000 次 |
| DuckDuckGo HTML | 搜尋相關文章 | 免費 |

### 資料庫
**無資料庫。** 所有資料即時從 Google Maps API 取得，不儲存任何店家資料。

### 前端
| 工具 | 用途 |
|---|---|
| **HTML5 / CSS3** | 頁面結構與樣式 |
| **Vanilla JavaScript** | 互動邏輯、API 呼叫、排序篩選 |
| **Jinja2** | Flask 模板引擎 |
| **Geolocation API** | 瀏覽器原生 GPS 定位 |
| **Haversine 公式** | 計算兩點之間的球面距離 |

### 部署
| 工具 | 用途 |
|---|---|
| **Render** | 免費雲端部署平台 |
| **GitHub** | 版本控制，連接 Render 後自動部署 |
| **Git post-commit hook** | 每次 commit 自動 push 到 GitHub |

---

## 四、GitHub 檔案結構

```
coffee-map/
├── wsgi.py                      # Gunicorn 入口，設定 Python 路徑
├── render.yaml                  # Render 部署設定
├── requirements.txt             # Python 套件清單
│
└── src/main/python/
    ├── models/
    │   └── coffee_shop.py       # CoffeeShop、Review 資料結構
    │
    ├── services/
    │   ├── google_maps.py       # Google Maps API 封裝（搜尋、詳細、分頁）
    │   └── article_scraper.py   # DuckDuckGo 文章爬蟲
    │
    ├── core/
    │   └── tag_engine.py        # 從評論與營業時間自動推斷 tag
    │
    └── api/
        ├── app.py               # Flask 主程式，所有 API endpoints
        ├── templates/
        │   └── index.html       # 前端頁面（Jinja2 模板）
        └── static/
            ├── css/style.css    # 全站樣式（咖啡棕色主題）
            └── js/app.js        # 前端互動邏輯
```

### 各檔案職責

| 檔案 | 職責 |
|---|---|
| `coffee_shop.py` | 定義 `CoffeeShop`、`Review` dataclass，`to_dict()` 轉 JSON |
| `google_maps.py` | 封裝 Places API；`search_coffee_shops`、`search_nearby`、`get_shop_details` |
| `article_scraper.py` | 搜尋 DuckDuckGo，過濾可信來源（ifoodie、tripadvisor 等），回傳文章標題 + 連結 |
| `tag_engine.py` | 關鍵字比對評論文字、解析營業時間，輸出 tag 清單 |
| `app.py` | 6 個 endpoints：`/`、`/api/cities`、`/api/districts`、`/api/shops`、`/api/shops/nearby`、`/api/shops/<place_id>` |
| `index.html` | 雙模式搜尋 UI、tab 切換、篩選欄、卡片格、Modal |
| `style.css` | 咖啡棕色主題、RWD、卡片 hover、Modal 動畫、tag pill 樣式 |
| `app.js` | 城市/行政區載入、搜尋、GPS 定位、排序、篩選、Modal、Haversine 距離 |

---

## 五、未來開發方向

### 🔥 高優先（功能缺口）

**快取機制**
目前每次搜尋都呼叫 Google API，相同條件重複搜尋會一直計費。可用 Redis 或 SQLite 快取結果（有效期 6 小時），大幅降低成本。

**資料庫**
目前無持久化儲存。加入 PostgreSQL 後可存使用者收藏、自訂 tag、搜尋紀錄，也讓快取更穩定。

**更多縣市**
現在只有台北市、新北市。台灣有 22 個縣市，只需在 `CITY_DISTRICTS` 字典新增即可，程式架構已支援。

### 🛠 中優先（體驗優化）

**地圖視覺化**
加入 Google Maps JavaScript API，在頁面上顯示地圖和店家圖釘，讓使用者直接點地圖選店。

**搜尋速度**
每次搜尋需等 30 間店逐一抓 Details（約 20-30 秒）。改進方式：
- 平行呼叫 API（`asyncio` + `aiohttp`）
- 改成「先顯示基本資料，背景補 tag」漸進式載入

**Tag 準確度提升**
目前只分析 Google 給的 5 則評論。若能串接更多評論來源或分析店家描述，tag 會更準確。

**使用者自訂 tag**
讓使用者對店家手動加 tag，建立社群驗證機制。

### 💡 低優先（進階功能）

**收藏清單** — 登入後可收藏咖啡廳、建立自己的「口袋名單」

**開放評論** — 讓使用者留下簡短心得，補充 Google 評論的不足

**Café Nomad 資料整合** — 整合 cafenomad.tw 的 wifi 速度、插座數量評分

**通知功能** — 追蹤特定咖啡廳，營業時間變更時發通知

**iOS / Android App** — 用 React Native 或 Flutter 包裝成原生 App

---

## 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定 API key
cp src/main/resources/config/.env.example src/main/resources/config/.env
# 編輯 .env，填入 GOOGLE_MAPS_API_KEY

# 啟動開發伺服器
python src/main/python/api/app.py
# 開啟 http://localhost:5001
```
