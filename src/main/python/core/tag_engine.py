"""
Infers tags for a coffee shop based on its name, reviews, and opening hours.
Tags: 讀書、不限時、外帶店、wifi、插座、寵物友善、甜點、自家烘焙、景觀
"""

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
}


def infer_tags(name: str, reviews: list, opening_hours: list) -> list:
    """Infer tags from shop name, review texts, and opening hours."""
    combined_text = name.lower()
    for r in reviews:
        combined_text += " " + r.text.lower()

    found_tags = []
    for tag, keywords in KEYWORD_TAGS.items():
        if any(kw.lower() in combined_text for kw in keywords):
            found_tags.append(tag)

    # Infer 不限時 from opening hours (open > 8 hours)
    if "不限時" not in found_tags and _is_long_hours(opening_hours):
        found_tags.append("不限時")

    return found_tags


def _is_long_hours(opening_hours: list) -> bool:
    """Return True if any day has >= 8 hours open."""
    import re
    for line in opening_hours:
        times = re.findall(r"(\d{1,2}):(\d{2})", line)
        if len(times) >= 2:
            open_h = int(times[0][0]) * 60 + int(times[0][1])
            close_h = int(times[-1][0]) * 60 + int(times[-1][1])
            if close_h - open_h >= 480:  # 8 hours
                return True
    return False
