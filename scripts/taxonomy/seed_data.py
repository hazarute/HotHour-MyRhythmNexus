#!/usr/bin/env python3

DEFAULT_SECTORS = [
    {
        "name": "Wellness",
        "slug": "wellness",
        "description": "Pilates, yoga, nefes, esneme ve benzeri iyi yasam hizmetleri.",
    },
    {
        "name": "Fitness",
        "slug": "fitness",
        "description": "Kondisyon, kuvvet, HIIT, spinning ve grup antrenmanlari.",
    },
    {
        "name": "Dance",
        "slug": "dance",
        "description": "Dans dersleri, ritim calismalari ve koreografi odakli hizmetler.",
    },
    {
        "name": "Recovery",
        "slug": "recovery",
        "description": "Mobilite, toparlanma, terapi destekli ve dusuk yogunluklu hizmetler.",
    },
]

DEFAULT_SERVICE_CATEGORIES = [
    {
        "name": "Reformer Pilates",
        "slug": "reformer-pilates",
        "description": "Reformer ekipmani ile bireysel veya grup pilates seanslari.",
        "sector_slug": "wellness",
    },
    {
        "name": "Mat Pilates",
        "slug": "mat-pilates",
        "description": "Mat uzerinde temel veya ileri seviye pilates dersleri.",
        "sector_slug": "wellness",
    },
    {
        "name": "Yoga",
        "slug": "yoga",
        "description": "Akis, nefes ve esneklik odakli yoga dersleri.",
        "sector_slug": "wellness",
    },
    {
        "name": "Stretching",
        "slug": "stretching",
        "description": "Esneme, mobilite ve dusuk tempolu toparlanma dersleri.",
        "sector_slug": "recovery",
    },
    {
        "name": "HIIT",
        "slug": "hiit",
        "description": "Yuksek yogunluklu interval antrenmanlari.",
        "sector_slug": "fitness",
    },
    {
        "name": "Spinning",
        "slug": "spinning",
        "description": "Bisiklet temelli grup kardiyo dersleri.",
        "sector_slug": "fitness",
    },
    {
        "name": "Strength Training",
        "slug": "strength-training",
        "description": "Kuvvet ve direnç odakli antrenmanlar.",
        "sector_slug": "fitness",
    },
    {
        "name": "Dance Class",
        "slug": "dance-class",
        "description": "Ritim, koreografi ve dans egitimi odakli dersler.",
        "sector_slug": "dance",
    },
]

STUDIO_SECTOR_KEYWORDS = {
    "wellness": ["pilates", "yoga", "zen", "wellness", "nefes", "reformer"],
    "fitness": ["fit", "fitness", "hiit", "cardio", "spinning", "academy", "power", "strength"],
    "dance": ["dans", "dance", "ritim", "koreografi"],
    "recovery": ["stretch", "recovery", "mobilite", "terapi"],
}

AUCTION_CATEGORY_KEYWORDS = {
    "reformer-pilates": ["reformer"],
    "mat-pilates": ["mat pilates", "pilates"],
    "yoga": ["yoga"],
    "stretching": ["stretch", "esneme", "mobilite"],
    "hiit": ["hiit"],
    "spinning": ["spinning", "bike"],
    "strength-training": ["strength", "kuvvet", "total body"],
    "dance-class": ["dance", "dans", "ritim", "piloxing"],
}