"""
Infers tags for a coffee shop based on its name, reviews, and opening hours.
Tags: 咖啡好喝、讀書、不限時、插座、有鹹食、外帶店、wifi、寵物友善、甜點、自家烘焙、景觀、深夜、早晨
"""
import re

KEYWORD_TAGS = {
    "讀書":    ["讀書", "念書", "自習", "安靜", "study", "quiet"],
    "不限時":  ["不限時", "unlimited", "不趕人", "不催位"],
    "外帶店":  ["外帶", "takeaway", "take out", "to go", "外帶專賣"],
    "wifi":    ["wifi", "wi-fi", "無線網路", "網路"],
    "插座":    ["插座", "充電", "outlet", "socket"],
    "寵物友善": ["寵物", "狗", "貓", "pet", "dog", "cat", "毛小孩"],
    "甜點":    ["甜點", "蛋糕", "dessert", "cake", "pastry", "可頌"],
    "自家烘焙": ["自家烘焙", "自烘", "single origin", "精品咖啡", "手沖"],
    "景觀":    ["景觀", "view", "夜景", "河景", "山景", "露天"],
    "咖啡好喝": ["咖啡好喝", "咖啡很好喝", "咖啡超好喝", "咖啡不錯", "咖啡很棒",
                 "咖啡讚", "好喝的咖啡", "咖啡香", "咖啡風味",
                 "great coffee", "good coffee", "amazing coffee", "best coffee"],
    "有鹹食":  ["鹹食", "輕食", "早午餐", "早餐", "brunch", "toast", "吐司",
                "三明治", "sandwich", "貝果", "bagel", "鬆餅", "waffle",
                "pasta", "義大利麵", "飯", "麵", "漢堡", "burger",
                "沙拉", "salad", "主食", "熱食", "餐點"],
}


def infer_tags(name: str, reviews: list, opening_hours: list,
               nomad: dict | None = None) -> list:
    """
    Infer tags from shop name, review texts, and opening hours.
    If a matching Café Nomad entry is supplied, its human ratings are used
    to confirm or add wifi / 插座 / 不限時 / 讀書 / 咖啡好喝 tags.
    """
    combined_text = name.lower()
    for r in reviews:
        text = r.text if isinstance(r, object) and hasattr(r, "text") else r.get("text", "")
        combined_text += " " + text.lower()

    found_tags = []
    for tag, keywords in KEYWORD_TAGS.items():
        if any(kw.lower() in combined_text for kw in keywords):
            found_tags.append(tag)

    # Hour-based tags
    if "不限時" not in found_tags and _hours_match(opening_hours, min_duration=480):
        found_tags.append("不限時")
    if _opens_before(opening_hours, before_minute=600):    # opens at or before 10:00
        found_tags.append("早晨")
    if _closes_after(opening_hours, after_minute=1350):    # closes at or after 22:30
        found_tags.append("深夜")

    # Café Nomad enhancement
    if nomad:
        def _score(key):
            try:
                return float(nomad.get(key) or 0)
            except (ValueError, TypeError):
                return 0.0

        if _score("wifi") >= 3 and "wifi" not in found_tags:
            found_tags.append("wifi")
        if nomad.get("socket") == "yes" and "插座" not in found_tags:
            found_tags.append("插座")
        if nomad.get("limited_time") == "no" and "不限時" not in found_tags:
            found_tags.append("不限時")
        if _score("quiet") >= 3 and "讀書" not in found_tags:
            found_tags.append("讀書")
        if _score("tasty") >= 3 and "咖啡好喝" not in found_tags:
            found_tags.append("咖啡好喝")

    return found_tags


# ── Hour helpers ──────────────────────────────────────

def _parse_times(opening_hours: list):
    """Yield (open_minutes, close_minutes) for each day in opening_hours."""
    for line in opening_hours:
        times = re.findall(r"(\d{1,2}):(\d{2})", line)
        if len(times) >= 2:
            open_m  = int(times[0][0]) * 60 + int(times[0][1])
            close_m = int(times[-1][0]) * 60 + int(times[-1][1])
            yield open_m, close_m


def _hours_match(opening_hours: list, min_duration: int) -> bool:
    """True if any day is open for at least min_duration minutes."""
    return any(c - o >= min_duration for o, c in _parse_times(opening_hours))


def _opens_before(opening_hours: list, before_minute: int) -> bool:
    """True if any day opens at or before before_minute (e.g. 600 = 10:00)."""
    return any(o <= before_minute for o, _ in _parse_times(opening_hours))


def _closes_after(opening_hours: list, after_minute: int) -> bool:
    """True if any day closes at or after after_minute (e.g. 1350 = 22:30)."""
    return any(c >= after_minute for _, c in _parse_times(opening_hours))
