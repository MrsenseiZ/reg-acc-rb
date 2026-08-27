#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module sinh thông tin tài khoản Roblox tự nhiên (Username, Password, Birthday, Gender)
Hỗ trợ sinh ngày sinh ngẫu nhiên 18+ (18 - 28 tuổi) chống lọc bot, mở full tính năng chat.
"""

import random
import string
from datetime import datetime, timedelta

REAL_FIRST = [
    "Alex", "Jordan", "Ryan", "Liam", "Noah", "Lucas", "Oliver", "Ethan", "Daniel", "Mason",
    "Leo", "James", "Logan", "Max", "Dylan", "Sam", "Jack", "Kevin", "Tyler", "Brian",
    "Emma", "Ava", "Mia", "Chloe", "Ella", "Sophia", "Zoe", "Maya", "Nora", "Lily"
]

REAL_LAST = [
    "Miller", "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson",
    "White", "Harris", "Martin", "Clark", "Lewis", "Walker", "Hall", "Allen", "Young",
    "King", "Wright", "Scott", "Green", "Baker", "Adams", "Nelson", "Carter", "Mitchell"
]

ADJECTIVES = [
    "Silent", "Swift", "Chill", "Lucky", "Brave", "Crazy", "Sneaky", "Epic", "Wild", "Hyper",
    "Sunny", "Dark", "Golden", "Silver", "Iron", "Mystic", "Noble", "Retro", "Cosmic", "Turbo",
    "Frosty", "Cozy", "Fierce", "Savage", "Smooth", "Clever", "Loyal", "Sleepy", "Electric",
    "Shadow", "Crimson", "Blazing", "Frozen", "Starlight", "Solar", "Lunar", "Phantom", "Apex"
]

ANIMALS_NOUNS = [
    "Fox", "Wolf", "Panda", "Otter", "Hawk", "Falcon", "Tiger", "Bear", "Lion", "Eagle",
    "Kitsune", "Samurai", "Ninja", "Knight", "Wizard", "Dragon", "Phoenix", "Ronin", "Ranger",
    "Vortex", "Spark", "Echo", "Drift", "Pixel", "Pulse", "Comet", "Blaze", "Frost", "Blade",
    "Striker", "Hunter", "Viper", "Glacier", "Titan", "Specter", "Matrix", "Aero", "Nexus"
]

GAMER_PREFIX = ["Itz", "ImJust", "Real", "YoIts", "TheReal", "Not", "Just", "Only", "Truly", "Iam"]
GAMER_SUFFIX = ["Plays", "Gaming", "Playz", "Studio", "Dev", "Craft", "Pro", "V2", "Main", "RBLX", "Club", "Zone", "Core"]
CUTE_WORDS = ["Boba", "Mochi", "Matcha", "Choco", "Cookie", "Berry", "Fluffy", "Bunny", "Peach", "Mango", "Milky", "Puff"]

EN_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def generate_username() -> str:
    """Sinh username đa dạng 10 phong cách, chuẩn format Roblox (3-20 ký tự)."""
    mode = random.randint(1, 10)
    tag_2d = str(random.randint(10, 99))
    tag_3d = str(random.randint(100, 999))
    tag_year = str(random.randint(1998, 2012))
    tag_short_year = f"{random.randint(4, 12):02d}"

    if mode == 1:
        sep = "_" if random.random() < 0.25 else ""
        name = f"{random.choice(REAL_FIRST)}{sep}{random.choice(REAL_LAST)}{random.choice([tag_short_year, tag_year, tag_2d])}"
    elif mode == 2:
        extra_tag = tag_2d if random.random() < 0.4 else ""
        name = f"{random.choice(GAMER_PREFIX)}{random.choice(REAL_FIRST)}{random.choice(GAMER_SUFFIX)}{extra_tag}"
    elif mode == 3:
        sep = "_" if random.random() < 0.25 else ""
        name = f"{random.choice(ADJECTIVES)}{sep}{random.choice(ANIMALS_NOUNS)}{random.choice([tag_2d, tag_3d, tag_short_year])}"
    elif mode == 4:
        sep = "_" if random.random() < 0.3 else ""
        name = f"{random.choice(CUTE_WORDS)}{sep}{random.choice(CUTE_WORDS)}{random.choice([tag_2d, tag_3d])}"
    elif mode == 5:
        name = f"{random.choice(REAL_FIRST)}_{random.choice(GAMER_SUFFIX)}{random.choice([tag_2d, tag_short_year])}"
    elif mode == 6:
        mid = f"{random.choice(ADJECTIVES)}{random.choice(ANIMALS_NOUNS)}"
        style = random.choice([("xX_", "_Xx"), ("i_", "_i"), ("v_", "_v"), ("Real_", "")])
        extra_num = str(random.randint(1, 99)) if not style[1] else ""
        name = f"{style[0]}{mid[:12]}{style[1]}{extra_num}"
    elif mode == 7:
        sep = "_" if random.random() < 0.3 else ""
        name = f"{random.choice(ADJECTIVES)}{sep}{random.choice(ANIMALS_NOUNS)}{random.choice([tag_short_year, tag_year, tag_2d])}"
    elif mode == 8:
        sep = "_" if random.random() < 0.2 else ""
        name = f"{random.choice(GAMER_PREFIX)}{sep}{random.choice(REAL_FIRST)}{random.choice([tag_2d, tag_3d, tag_short_year])}"
    elif mode == 9:
        sep = "_" if random.random() < 0.3 else ""
        name = f"{random.choice(REAL_FIRST)}{sep}{random.choice(ANIMALS_NOUNS)}{random.choice([tag_2d, tag_3d])}"
    else:
        sep = "_" if random.random() < 0.25 else ""
        name = f"{random.choice(ANIMALS_NOUNS)}{sep}{random.choice(ANIMALS_NOUNS)}{random.choice([tag_2d, tag_3d])}"

    name = name.strip("_")
    while "__" in name:
        name = name.replace("__", "_")
    if len(name) < 3:
        name += str(random.randint(100, 999))
    return name[:20]


def generate_password(mode: str = "random", static_pass: str = "RezzPass2026!@", username: str = "") -> str:
    """Sinh mật khẩu theo mode: static, random, hoặc pattern."""
    if mode == "random":
        chars = (
            random.choices(string.ascii_uppercase, k=3) +
            random.choices(string.ascii_lowercase, k=5) +
            random.choices(string.digits, k=3) +
            random.choices("!@#$%^&*", k=2)
        )
        random.shuffle(chars)
        return "".join(chars)
    elif mode == "pattern":
        clean_u = username or "Rezz"
        return f"{clean_u}@2026!"
    else:
        return static_pass or "RezzPass2026!@"


def generate_birthday(age_mode: str = "18+", under13: bool = False) -> dict:
    """
    Sinh ngày sinh linh hoạt:
    - '18+' hoặc 'random_18+': Ngẫu nhiên tuổi từ 18 đến 28 tuổi (năm sinh 1996 - 2006).
    - '<13': Tuổi từ 10 đến 12 tuổi.
    - 'random_all': Tuổi ngẫu nhiên từ 13 đến 30 tuổi.
    """
    now = datetime.now()
    curr_year = now.year

    if under13 or age_mode == "<13":
        # Dưới 13 tuổi (10 - 12 tuổi)
        age = random.randint(10, 12)
    elif age_mode in ["18+", "random_18+", "over18"]:
        # Ngẫu nhiên trên 18 tuổi (từ 18 đến 28 tuổi) -> Luôn đảm bảo >= 18 tuổi
        age = random.randint(18, 28)
    else:
        # Ngẫu nhiên phổ thông (14 đến 25 tuổi)
        age = random.randint(14, 25)

    birth_year = curr_year - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28) # Luôn an toàn cho cả tháng 2

    target = datetime(birth_year, birth_month, birth_day)
    iso_str = target.strftime("%Y-%m-%dT00:00:00.000Z")

    return {
        "iso": iso_str,
        "year": birth_year,
        "month": birth_month,
        "day": birth_day,
        "age": age,
        "formatted": target.strftime("%d/%m/%Y"),
        "label": f"{age} tuổi ({target.strftime('%d/%m/%Y')})"
    }


def generate_gender() -> int:
    """1: Nữ (Female), 2: Nam (Male)"""
    return random.choice([1, 2])
