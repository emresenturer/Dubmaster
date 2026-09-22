# -*- coding: utf-8 -*-
"""
ULTRADUB
Your voice, in every language.

Version 5.0 - Simple upload flow
(c) 2026 Ultradub

Flow:
  1. Visitor uploads a video they recorded
  2. Picks the language they speak and up to 3 languages to dub into
  3. Chooses a standard AI voice or their own voice (+$3.99), and optional lip sync
  4. Gets a free 15-second preview and an exact price
  5. Pays once and downloads every version plus subtitles

Configuration comes only from Streamlit secrets / environment variables:
  Required: GOOGLE_API_KEY, STRIPE_SECRET_KEY, APP_URL
  Optional: ELEVENLABS_API_KEY (own-voice option), SYNCLABS_API_KEY (lip sync),
            SUPPORT_EMAIL (shown in the footer)
Demo videos: put demo/original.mp4 and demo/dubbed.mp4 in the repo,
or set DEMO_ORIGINAL_URL and DEMO_DUBBED_URL.
"""

import base64
import html
import os
import re
import shutil
import subprocess
import tempfile
import time
import traceback
import uuid
from pathlib import Path

import requests
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Ultradub - Your voice, in every language",
    page_icon="🎙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --blue:      #1A73E8;
    --blue-dark: #1557B0;
    --blue-soft: #E8F0FE;
    --ink:       #202124;
    --ink-2:     #5F6368;
    --ink-3:     #80868B;
    --line:      #DADCE0;
    --paper:     #FFFFFF;
    --paper-2:   #F8F9FA;
    --green:     #188038;
    --font:      'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--font) !important;
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
}
#MainMenu, footer, header, [data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }
.block-container { max-width: 760px !important; padding-top: 1.25rem !important; }

/* Wordmark */
.ud-top { display: flex; align-items: baseline; justify-content: space-between;
          padding: .25rem 0 1.5rem; border-bottom: 1px solid var(--line); }
.ud-wordmark { font-size: 1.35rem; font-weight: 800; letter-spacing: -.4px; color: var(--ink); }
.ud-wordmark span { color: var(--blue); }
.ud-top-note { font-size: .82rem; color: var(--ink-3); }

/* Hero */
.ud-hero { padding: 2.25rem 0 1.25rem; }
.ud-hero h1 { font-size: clamp(2rem, 5vw, 2.9rem); line-height: 1.08; font-weight: 800;
              letter-spacing: -1.2px; margin: 0 0 .9rem; color: var(--ink); }
.ud-hero p { font-size: 1.05rem; line-height: 1.6; color: var(--ink-2); margin: 0; max-width: 34em; }

/* Demo */
.ud-demo-head { margin: 1.5rem 0 .5rem; font-weight: 700; font-size: 1.05rem; }
.ud-demo-cap { font-size: .9rem; color: var(--ink-2); margin: -.25rem 0 .75rem; }
.ud-clip-label { font-size: .85rem; font-weight: 600; color: var(--ink-2); margin-bottom: .35rem; }
.ud-clip-label.dubbed { color: var(--blue); }

/* Form */
.ud-form-head { margin: 2.25rem 0 .25rem; font-weight: 800; font-size: 1.35rem; letter-spacing: -.4px; }
.ud-form-sub { color: var(--ink-2); font-size: .92rem; margin-bottom: 1rem; }
.ud-meta { font-size: .88rem; color: var(--ink-2); margin: -.25rem 0 .75rem; }

/* Price line */
.ud-price { display: flex; justify-content: space-between; align-items: baseline;
            border-top: 1px solid var(--line); margin-top: 1rem; padding: 1rem 0 .75rem; }
.ud-price-label { font-size: .95rem; color: var(--ink-2); }
.ud-price-value { font-size: 1.8rem; font-weight: 800; letter-spacing: -.6px; color: var(--ink); }
.ud-price-value.muted { font-size: 1rem; font-weight: 500; color: var(--ink-3); letter-spacing: 0; }
.ud-price-lines { font-size: .85rem; color: var(--ink-2); line-height: 1.7; margin: -.25rem 0 .75rem; }

/* Buttons */
div.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: var(--blue) !important; border: none !important; color: #fff !important;
    border-radius: 999px !important; font-weight: 700 !important;
    padding: .7rem 1.4rem !important; font-size: 1rem !important;
}
div.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover { background: var(--blue-dark) !important; }
div.stButton > button[kind="primary"]:disabled,
button[data-testid="stBaseButton-primary"]:disabled { background: var(--line) !important; color: var(--ink-3) !important; }

.ud-pay-btn { display: block; text-align: center; background: var(--blue); color: #fff !important;
              text-decoration: none !important; font-weight: 700; font-size: 1.05rem;
              border-radius: 999px; padding: .9rem 1.4rem; margin: 1rem 0 .5rem; }
.ud-pay-btn:hover { background: var(--blue-dark); }
.ud-pay-btn:focus-visible { outline: 3px solid var(--blue-soft); outline-offset: 2px; }
.ud-pay-note { text-align: center; font-size: .82rem; color: var(--ink-3); }

/* Progress */
.ud-steps { border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; margin: 1rem 0; }
.ud-steps-title { font-weight: 700; margin-bottom: .6rem; display: flex; justify-content: space-between; }
.ud-steps-title small { font-weight: 500; color: var(--ink-3); }
.ud-step { display: flex; gap: .7rem; padding: .3rem 0; font-size: .92rem; color: var(--ink-3); }
.ud-step.active { color: var(--ink); font-weight: 600; }
.ud-step.done { color: var(--ink-2); }
.ud-step .ic { width: 1.1rem; text-align: center; }
.ud-step.done .ic { color: var(--green); }
.ud-step.active .ic { color: var(--blue); }

/* Result */
.ud-result-head { margin: 2rem 0 .25rem; font-weight: 800; font-size: 1.35rem; letter-spacing: -.4px; }
.ud-quote { border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; margin: 1rem 0 0; }
.ud-qline { display: flex; justify-content: space-between; font-size: .92rem; padding: .25rem 0; color: var(--ink-2); }
.ud-qline.total { border-top: 1px solid var(--line); margin-top: .4rem; padding-top: .6rem;
                  color: var(--ink); font-weight: 800; font-size: 1.1rem; }

/* Delivery */
.ud-done { background: var(--paper-2); border: 1px solid var(--line); border-radius: 12px;
           padding: 1.25rem 1.2rem; margin: 1.5rem 0 1rem; }
.ud-done h2 { margin: 0 0 .3rem; font-size: 1.35rem; font-weight: 800; letter-spacing: -.4px; }
.ud-done p { margin: 0; color: var(--ink-2); }

/* Footer */
.ud-foot { border-top: 1px solid var(--line); margin-top: 3rem; padding: 1.25rem 0 2rem;
           font-size: .82rem; color: var(--ink-3); display: flex; justify-content: space-between;
           flex-wrap: wrap; gap: .5rem; }
.ud-foot a { color: var(--ink-2); }

@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LANGUAGE REGISTRY
# All entries confirmed: Google STT + Google Translate + Google TTS Wavenet/Neural2
# ══════════════════════════════════════════════════════════════════════════════
# fmt: off
LANG_REGISTRY = {
    # key: display label
    # stt:   Google STT BCP-47 code
    # tr:    Google Translate ISO-639 code
    # tts:   Google TTS language code
    # voice: Google TTS voice name (Neural2 > Wavenet > Standard)

    "auto":     {"label": "🔍 Auto-detect",          "stt": "auto",       "tr": "auto", "tts": None,        "voice": None},

    # English variants
    "en-US":    {"label": "🇺🇸 English (US)",         "stt": "en-US",      "tr": "en",   "tts": "en-US",     "voice": "en-US-Neural2-D"},
    "en-GB":    {"label": "🇬🇧 English (UK)",         "stt": "en-GB",      "tr": "en",   "tts": "en-GB",     "voice": "en-GB-Neural2-B"},
    "en-AU":    {"label": "🇦🇺 English (Australia)",  "stt": "en-AU",      "tr": "en",   "tts": "en-AU",     "voice": "en-AU-Neural2-B"},
    "en-IN":    {"label": "🇮🇳 English (India)",      "stt": "en-IN",      "tr": "en",   "tts": "en-IN",     "voice": "en-IN-Neural2-B"},

    # Spanish
    "es-US":    {"label": "🇺🇸 Spanish (US)",         "stt": "es-US",      "tr": "es",   "tts": "es-US",     "voice": "es-US-Neural2-B"},
    "es-ES":    {"label": "🇪🇸 Spanish (Spain)",      "stt": "es-ES",      "tr": "es",   "tts": "es-ES",     "voice": "es-ES-Neural2-B"},

    # French
    "fr-FR":    {"label": "🇫🇷 French",               "stt": "fr-FR",      "tr": "fr",   "tts": "fr-FR",     "voice": "fr-FR-Neural2-B"},
    "fr-CA":    {"label": "🇨🇦 French (Canada)",      "stt": "fr-CA",      "tr": "fr",   "tts": "fr-CA",     "voice": "fr-CA-Neural2-B"},

    # German
    "de-DE":    {"label": "🇩🇪 German",               "stt": "de-DE",      "tr": "de",   "tts": "de-DE",     "voice": "de-DE-Neural2-B"},

    # Italian
    "it-IT":    {"label": "🇮🇹 Italian",              "stt": "it-IT",      "tr": "it",   "tts": "it-IT",     "voice": "it-IT-Neural2-C"},

    # Portuguese
    "pt-BR":    {"label": "🇧🇷 Portuguese (Brazil)",  "stt": "pt-BR",      "tr": "pt",   "tts": "pt-BR",     "voice": "pt-BR-Neural2-B"},
    "pt-PT":    {"label": "🇵🇹 Portuguese (Portugal)","stt": "pt-PT",      "tr": "pt",   "tts": "pt-PT",     "voice": "pt-PT-Wavenet-A"},

    # Russian
    "ru-RU":    {"label": "🇷🇺 Russian",              "stt": "ru-RU",      "tr": "ru",   "tts": "ru-RU",     "voice": "ru-RU-Wavenet-D"},

    # Japanese
    "ja-JP":    {"label": "🇯🇵 Japanese",             "stt": "ja-JP",      "tr": "ja",   "tts": "ja-JP",     "voice": "ja-JP-Neural2-C"},

    # Chinese
    "cmn-CN":   {"label": "🇨🇳 Chinese (Mandarin)",   "stt": "cmn-Hans-CN","tr": "zh",   "tts": "cmn-CN",    "voice": "cmn-CN-Wavenet-B"},
    "yue-HK":   {"label": "🇭🇰 Chinese (Cantonese)",  "stt": "yue-Hant-HK","tr": "zh-TW","tts": "yue-HK",    "voice": "yue-HK-Standard-A"},

    # Korean
    "ko-KR":    {"label": "🇰🇷 Korean",               "stt": "ko-KR",      "tr": "ko",   "tts": "ko-KR",     "voice": "ko-KR-Neural2-C"},

    # Arabic
    "ar-XA":    {"label": "🇸🇦 Arabic",               "stt": "ar-EG",      "tr": "ar",   "tts": "ar-XA",     "voice": "ar-XA-Wavenet-B"},

    # Hindi
    "hi-IN":    {"label": "🇮🇳 Hindi",                "stt": "hi-IN",      "tr": "hi",   "tts": "hi-IN",     "voice": "hi-IN-Neural2-B"},

    # Turkish
    "tr-TR":    {"label": "🇹🇷 Turkish",              "stt": "tr-TR",      "tr": "tr",   "tts": "tr-TR",     "voice": "tr-TR-Wavenet-B"},

    # Dutch
    "nl-NL":    {"label": "🇳🇱 Dutch",                "stt": "nl-NL",      "tr": "nl",   "tts": "nl-NL",     "voice": "nl-NL-Neural2-B"},

    # Polish
    "pl-PL":    {"label": "🇵🇱 Polish",               "stt": "pl-PL",      "tr": "pl",   "tts": "pl-PL",     "voice": "pl-PL-Wavenet-B"},

    # Ukrainian
    "uk-UA":    {"label": "🇺🇦 Ukrainian",            "stt": "uk-UA",      "tr": "uk",   "tts": "uk-UA",     "voice": "uk-UA-Wavenet-A"},

    # Swedish
    "sv-SE":    {"label": "🇸🇪 Swedish",              "stt": "sv-SE",      "tr": "sv",   "tts": "sv-SE",     "voice": "sv-SE-Neural2-B"},

    # Danish
    "da-DK":    {"label": "🇩🇰 Danish",               "stt": "da-DK",      "tr": "da",   "tts": "da-DK",     "voice": "da-DK-Neural2-D"},

    # Norwegian
    "nb-NO":    {"label": "🇳🇴 Norwegian",            "stt": "nb-NO",      "tr": "no",   "tts": "nb-NO",     "voice": "nb-NO-Wavenet-D"},

    # Finnish
    "fi-FI":    {"label": "🇫🇮 Finnish",              "stt": "fi-FI",      "tr": "fi",   "tts": "fi-FI",     "voice": "fi-FI-Wavenet-A"},

    # Czech
    "cs-CZ":    {"label": "🇨🇿 Czech",                "stt": "cs-CZ",      "tr": "cs",   "tts": "cs-CZ",     "voice": "cs-CZ-Wavenet-A"},

    # Greek
    "el-GR":    {"label": "🇬🇷 Greek",                "stt": "el-GR",      "tr": "el",   "tts": "el-GR",     "voice": "el-GR-Wavenet-A"},

    # Hungarian
    "hu-HU":    {"label": "🇭🇺 Hungarian",            "stt": "hu-HU",      "tr": "hu",   "tts": "hu-HU",     "voice": "hu-HU-Wavenet-A"},

    # Romanian
    "ro-RO":    {"label": "🇷🇴 Romanian",             "stt": "ro-RO",      "tr": "ro",   "tts": "ro-RO",     "voice": "ro-RO-Wavenet-A"},

    # Vietnamese
    "vi-VN":    {"label": "🇻🇳 Vietnamese",           "stt": "vi-VN",      "tr": "vi",   "tts": "vi-VN",     "voice": "vi-VN-Wavenet-B"},

    # Indonesian
    "id-ID":    {"label": "🇮🇩 Indonesian",           "stt": "id-ID",      "tr": "id",   "tts": "id-ID",     "voice": "id-ID-Wavenet-B"},

    # Thai
    "th-TH":    {"label": "🇹🇭 Thai",                 "stt": "th-TH",      "tr": "th",   "tts": "th-TH",     "voice": "th-TH-Neural2-C"},

    # Filipino
    "fil-PH":   {"label": "🇵🇭 Filipino",             "stt": "fil-PH",     "tr": "tl",   "tts": "fil-PH",    "voice": "fil-PH-Wavenet-B"},

    # Malay
    "ms-MY":    {"label": "🇲🇾 Malay",                "stt": "ms-MY",      "tr": "ms",   "tts": "ms-MY",     "voice": "ms-MY-Wavenet-B"},

    # Bengali
    "bn-IN":    {"label": "🇧🇩 Bengali",              "stt": "bn-IN",      "tr": "bn",   "tts": "bn-IN",     "voice": "bn-IN-Wavenet-B"},

    # Tamil
    "ta-IN":    {"label": "🇮🇳 Tamil",                "stt": "ta-IN",      "tr": "ta",   "tts": "ta-IN",     "voice": "ta-IN-Wavenet-C"},

    # Telugu
    "te-IN":    {"label": "🇮🇳 Telugu",               "stt": "te-IN",      "tr": "te",   "tts": "te-IN",     "voice": "te-IN-Wavenet-B"},

    # Kannada
    "kn-IN":    {"label": "🇮🇳 Kannada",              "stt": "kn-IN",      "tr": "kn",   "tts": "kn-IN",     "voice": "kn-IN-Wavenet-B"},

    # Malayalam
    "ml-IN":    {"label": "🇮🇳 Malayalam",            "stt": "ml-IN",      "tr": "ml",   "tts": "ml-IN",     "voice": "ml-IN-Wavenet-B"},

    # Gujarati
    "gu-IN":    {"label": "🇮🇳 Gujarati",             "stt": "gu-IN",      "tr": "gu",   "tts": "gu-IN",     "voice": "gu-IN-Wavenet-B"},

    # Marathi
    "mr-IN":    {"label": "🇮🇳 Marathi",              "stt": "mr-IN",      "tr": "mr",   "tts": "mr-IN",     "voice": "mr-IN-Wavenet-C"},

    # Punjabi
    "pa-IN":    {"label": "🇮🇳 Punjabi",              "stt": "pa-IN",      "tr": "pa",   "tts": "pa-IN",     "voice": "pa-IN-Wavenet-A"},

    # Urdu
    "ur-IN":    {"label": "🇵🇰 Urdu",                 "stt": "ur-IN",      "tr": "ur",   "tts": "ur-IN",     "voice": "ur-IN-Wavenet-A"},

    # Hebrew
    "he-IL":    {"label": "🇮🇱 Hebrew",               "stt": "he-IL",      "tr": "iw",   "tts": "he-IL",     "voice": "he-IL-Wavenet-B"},

    # Slovak
    "sk-SK":    {"label": "🇸🇰 Slovak",               "stt": "sk-SK",      "tr": "sk",   "tts": "sk-SK",     "voice": "sk-SK-Wavenet-A"},

    # Afrikaans
    "af-ZA":    {"label": "🇿🇦 Afrikaans",            "stt": "af-ZA",      "tr": "af",   "tts": "af-ZA",     "voice": "af-ZA-Standard-A"},
}
# fmt: on

# Convenience lookups
LANG_LABELS    = {k: v["label"] for k, v in LANG_REGISTRY.items()}
INPUT_LANGS    = list(LANG_REGISTRY.keys())  # all including auto
OUTPUT_LANGS   = [k for k in LANG_REGISTRY if k != "auto"]
DETECT_ORDER   = [
    "ru-RU", "es-US", "fr-FR", "de-DE", "pt-BR", "cmn-Hans-CN",
    "ja-JP", "ko-KR", "ar-EG", "hi-IN", "tr-TR", "nl-NL",
    "pl-PL", "uk-UA", "en-US",
]


# ══════════════════════════════════════════════════════════════════════════════
# LANGUAGES OFFERED ON THE SITE
# The 20 most spoken languages that Google speech, translation and voices support.
# (Nigerian Pidgin and Hausa rank in the top 20 but have no voice support, so
#  Tamil, Korean and Filipino take their places.)
# ══════════════════════════════════════════════════════════════════════════════
SITE_LANGS = [
    ("en-US",  "English"),
    ("cmn-CN", "Chinese (Mandarin)"),
    ("hi-IN",  "Hindi"),
    ("es-US",  "Spanish"),
    ("ar-XA",  "Arabic"),
    ("fr-FR",  "French"),
    ("bn-IN",  "Bengali"),
    ("pt-BR",  "Portuguese"),
    ("ru-RU",  "Russian"),
    ("id-ID",  "Indonesian"),
    ("ur-IN",  "Urdu"),
    ("de-DE",  "German"),
    ("ja-JP",  "Japanese"),
    ("mr-IN",  "Marathi"),
    ("vi-VN",  "Vietnamese"),
    ("te-IN",  "Telugu"),
    ("tr-TR",  "Turkish"),
    ("ta-IN",  "Tamil"),
    ("ko-KR",  "Korean"),
    ("fil-PH", "Filipino"),
]
SITE_KEYS  = [k for k, _ in SITE_LANGS]
SITE_NAMES = {k: n for k, n in SITE_LANGS}
NAME_TO_KEY = {n: k for k, n in SITE_LANGS}

# Languages the own-voice model (ElevenLabs eleven_multilingual_v2) can speak.
CLONE_OK = {
    "en-US", "cmn-CN", "hi-IN", "es-US", "ar-XA", "fr-FR", "pt-BR", "ru-RU",
    "id-ID", "de-DE", "ja-JP", "tr-TR", "ta-IN", "ko-KR", "fil-PH",
}
MAX_TARGETS = 3

# Demo clips shown at the top of the page (original vs dubbed).
DEMO_ORIGINAL = "demo/original.mp4"
DEMO_DUBBED   = "demo/dubbed.mp4"
DEMO_CAPTION  = "Recorded on a phone in English. Dubbed into Spanish in the same voice."

# ══════════════════════════════════════════════════════════════════════════════
# PRICING ENGINE
# ══════════════════════════════════════════════════════════════════════════════
TIERS = [
    {"name": "Short",  "emoji": "⚡", "max_min": 5,  "price": 4.99},
    {"name": "Medium", "emoji": "🎬", "max_min": 15, "price": 9.99},
    {"name": "Long",   "emoji": "🎞️", "max_min": 30, "price": 19.99},
    {"name": "Ultra",  "emoji": "🏆", "max_min": 60, "price": 34.99},
]
LIPSYNC_ADDON  = {"Short": 5.00, "Medium": 12.00, "Long": 25.00, "Ultra": 45.00}
CLONE_ADDON    = 3.99
EXTRA_LANG_ADD = 3.99   # per extra language (lang 2 & 3 are discounted - 3rd is free)
GTTS_MAX_CHARS = 4800

VIDEO_STORE     = "/tmp/ultradub_store"
PREVIEW_SECONDS = 15
os.makedirs(VIDEO_STORE, exist_ok=True)


def get_tier(duration_sec: float) -> dict:
    for t in TIERS:
        if duration_sec / 60 <= t["max_min"]:
            return t
    return TIERS[-1]


def compute_quote(duration_sec: float, lang_keys: list[str],
                  lipsync: bool, clone: bool) -> dict:
    tier     = get_tier(duration_sec)
    n        = len(lang_keys)
    base     = tier["price"]
    # bundle: 3 langs for price of 2 - third language is free
    if n == 1:   lang_price = base
    elif n == 2: lang_price = base * 2
    else:        lang_price = base * 2          # 3 for price of 2
    savings  = base if n >= 3 else 0
    ls       = LIPSYNC_ADDON[tier["name"]] if lipsync else 0
    cl       = CLONE_ADDON if clone else 0
    return {
        "tier":       tier["name"],
        "emoji":      tier["emoji"],
        "dur":        round(duration_sec / 60, 1),
        "n_langs":    n,
        "lang_price": lang_price,
        "savings":    savings,
        "ls":         ls,
        "clone":      cl,
        "total":      round(lang_price + ls + cl, 2),
    }


def estimate_eta(duration_min: float, n_langs: int,
                 has_clone: bool, has_lipsync: bool,
                 has_music: bool) -> dict[str, int]:
    """Estimate step durations in seconds."""
    d = duration_min
    return {
        "download":   45,
        "music_sep":  int(d * 90) if has_music else 0,
        "transcribe": max(60, int(d * 12)),
        "translate":  15,
        "clone":      75 if has_clone else 0,
        "synthesise": max(90, int(d * 14)) * n_langs,
        "merge":      max(45, int(d * 5)) * n_langs,
        "lipsync":    int(d * 60) if has_lipsync else 0,
        "preview":    20,
    }

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _run(cmd: list, **kw) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "").strip()
                           or f"Command failed: {cmd[0]}")
    return r

def ffmpeg_ok() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

def get_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:    return float(r.stdout.strip())
    except: return 300.0

def cfg(key: str) -> str:
    """Read a setting from environment variables, then Streamlit secrets."""
    val = os.environ.get(key, "")
    if val:
        return val
    try:
        return str(st.secrets.get(key, "") or "")
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# SRT SUBTITLE GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def _srt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(segments: list[dict], text_key: str = "translated") -> str:
    lines, idx = [], 1
    for seg in segments:
        text = seg.get(text_key, seg.get("text", "")).strip()
        if not text:
            continue
        lines.append(
            f"{idx}\n"
            f"{_srt_ts(seg['start'])} --> {_srt_ts(seg['end'])}\n"
            f"{text}\n"
        )
        idx += 1
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# BACKGROUND MUSIC SEPARATION (audio-separator - ONNX, lightweight)
# ══════════════════════════════════════════════════════════════════════════════
def _is_mono(audio_path: str) -> bool:
    """Return True if audio file has only 1 channel."""
    r = subprocess.run(
        ["ffprobe", "-v", "error",
         "-select_streams", "a:0",
         "-show_entries", "stream=channels",
         "-of", "default=noprint_wrappers=1:nokey=1",
         audio_path],
        capture_output=True, text=True)
    try:    return int(r.stdout.strip()) == 1
    except: return True  # assume mono if uncertain


def separate_music(audio_path: str, work_dir: str) -> tuple[str, str]:
    """
    Separate vocals from background music.
    Returns (vocals_path, no_vocals_path).

    For mono audio (phone recordings) the stereo centre-channel trick
    produces silence, so we skip it and return the original audio as vocals.
    """
    # Try audio-separator first (requires package installed)
    try:
        from audio_separator.separator import Separator
        sep = Separator(output_dir=work_dir, output_format="wav",
                        log_level=40)
        sep.load_model("UVR-MDX-NET-Inst_HQ_3.onnx")
        result = sep.separate(audio_path)
        vocals    = next((p for p in result if "Vocals"   in p or "vocals"   in p), result[0])
        no_vocals = next((p for p in result if "Instrum"  in p or "no_vocal" in p), result[-1])
        return vocals, no_vocals
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: only works reliably on stereo audio
    # For mono (most phone videos) the c0-c1 trick = silence, so skip it
    vocals_path    = os.path.join(work_dir, "vocals_approx.mp3")
    no_vocals_path = os.path.join(work_dir, "no_vocals_approx.mp3")

    if _is_mono(audio_path):
        # Mono audio: cannot do centre-channel separation.
        # Return original audio as vocals, silence as no_vocals.
        # Music preservation will be skipped gracefully in step_merge.
        import shutil as _sh
        _sh.copy2(audio_path, vocals_path)
        # Create a short silence file as placeholder
        make_silence(0.1, no_vocals_path)
        return vocals_path, no_vocals_path

    # Stereo audio: rough centre-channel extraction
    _run(["ffmpeg", "-y", "-i", audio_path,
          "-af", "pan=stereo|c0=c0-c1|c1=c1-c0,highpass=f=200,loudnorm",
          "-ar", "22050", "-ac", "2",
          vocals_path])

    _run(["ffmpeg", "-y", "-i", audio_path,
          "-af", "pan=stereo|c0=c1|c1=c0,lowpass=f=4000,loudnorm",
          "-ar", "22050", "-ac", "2",
          no_vocals_path])

    return vocals_path, no_vocals_path

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE CLOUD - STT
# ══════════════════════════════════════════════════════════════════════════════
def _stt_request(audio_b64: str, lang_code: str, api_key: str) -> list[dict]:
    r = requests.post(
        f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}",
        json={
            "config": {
                "encoding": "MP3",
                "languageCode": lang_code,
                "enableWordTimeOffsets": True,
                "model": "latest_long",
            },
            "audio": {"content": audio_b64},
        }, timeout=120)
    r.raise_for_status()

    segs, cursor = [], 0.0
    for result in r.json().get("results", []):
        alt   = result["alternatives"][0]
        words = alt.get("words", [])
        if words:
            for gi in range(0, len(words), 7):
                grp   = words[gi: gi + 7]
                start = float(grp[0]["startTime"].rstrip("s"))
                end   = float(grp[-1]["endTime"].rstrip("s"))
                segs.append({"start": start, "end": end,
                             "text": " ".join(w["word"] for w in grp)})
                cursor = end
        else:
            text = alt.get("transcript", "").strip()
            if text:
                dur = len(text) / 15
                segs.append({"start": cursor, "end": cursor + dur, "text": text})
                cursor += dur
    return segs


def detect_language(audio_path: str, api_key: str) -> str:
    sample = tempfile.mktemp(suffix=".mp3")
    try:
        _run(["ffmpeg", "-y", "-i", audio_path, "-t", "20",
              "-ar", "16000", "-ac", "1",
              "-c:a", "libmp3lame", "-q:a", "5", sample])
        with open(sample, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    finally:
        if os.path.exists(sample): os.remove(sample)

    best, best_n = "ru-RU", 0
    for lc in DETECT_ORDER:
        try:
            n = sum(len(s["text"].split())
                    for s in _stt_request(b64, lc, api_key))
            if n > best_n: best_n, best = n, lc
            if n > 10: break
        except Exception:
            continue
    return best


def transcribe_audio(audio_path: str, src_key: str,
                     api_key: str) -> tuple[list[dict], str]:
    """Transcribe full audio. Returns (segments, detected_lang_key)."""
    if src_key == "auto":
        bcp47 = detect_language(audio_path, api_key)
    else:
        bcp47 = LANG_REGISTRY[src_key]["stt"]

    total     = get_duration(audio_path)
    chunk_dir = tempfile.mkdtemp(prefix="ud_chunks_")
    all_segs  = []

    try:
        start, idx = 0.0, 0
        while start < total:
            cp = os.path.join(chunk_dir, f"c{idx:03d}.mp3")
            _run(["ffmpeg", "-y", "-i", audio_path,
                  "-ss", str(start), "-t", "55",
                  "-ar", "16000", "-ac", "1",
                  "-c:a", "libmp3lame", "-q:a", "5", cp])
            with open(cp, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            for s in _stt_request(b64, bcp47, api_key):
                all_segs.append({
                    "start": round(s["start"] + start, 3),
                    "end":   round(s["end"]   + start, 3),
                    "text":  s["text"],
                })
            start += 55; idx += 1
    finally:
        shutil.rmtree(chunk_dir, ignore_errors=True)

    # Map detected BCP-47 back to our lang key
    detected_key = bcp47.split("-")[0].lower()
    if detected_key == "cmn": detected_key = "cmn-CN"
    # find matching key in registry
    detected = next(
        (k for k, v in LANG_REGISTRY.items()
         if v["stt"] == bcp47 or v["stt"].startswith(detected_key)),
        "ru-RU")
    return all_segs, detected

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE CLOUD - TRANSLATE
# ══════════════════════════════════════════════════════════════════════════════
def translate_batch(texts: list[str], tgt_lang_key: str,
                    api_key: str) -> list[str]:
    if not texts: return []
    tgt = LANG_REGISTRY[tgt_lang_key]["tr"]
    out = []
    for i in range(0, len(texts), 100):
        r = requests.post(
            f"https://translation.googleapis.com/language/translate/v2?key={api_key}",
            json={"q": texts[i:i+100], "target": tgt, "format": "text"},
            timeout=60)
        r.raise_for_status()
        out += [t["translatedText"] for t in r.json()["data"]["translations"]]
    return out

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE CLOUD - TTS
# ══════════════════════════════════════════════════════════════════════════════
def synthesize_text(text: str, lang_key: str, api_key: str) -> bytes:
    text = text.strip()[:GTTS_MAX_CHARS]
    if not text: return b""
    lc = LANG_REGISTRY[lang_key]["tts"]
    vn = LANG_REGISTRY[lang_key]["voice"]
    r = requests.post(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}",
        json={
            "input":       {"text": text},
            "voice":       {"languageCode": lc, "name": vn},
            "audioConfig": {"audioEncoding": "MP3", "speakingRate": 1.0},
        }, timeout=30)
    r.raise_for_status()
    return base64.b64decode(r.json()["audioContent"])

# ══════════════════════════════════════════════════════════════════════════════
# ELEVENLABS - VOICE CLONING
# ══════════════════════════════════════════════════════════════════════════════

def _identify_primary_speaker_segments(
    audio_path: str,
    lang_code: str,
    api_key: str,
) -> list[dict]:
    """
    Use Google STT speaker diarization to identify which speaker
    talks the most, and return their time segments.

    This prevents cloning the WRONG speaker (e.g. a male narrator
    when the main speaker is a woman or child).

    Returns list of {start_sec, end_sec} for the dominant speaker.
    Falls back to empty list on any error.
    """
    try:
        # Use a 55-second sample: synchronous recognition accepts at most 60 seconds
        sample = tempfile.mktemp(suffix=".mp3")
        _run(["ffmpeg", "-y", "-i", audio_path,
              "-t", "55",
              "-ar", "16000", "-ac", "1",
              "-c:a", "libmp3lame", "-q:a", "5", sample])

        with open(sample, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        os.remove(sample)

        payload = {
            "config": {
                "encoding":                  "MP3",
                "languageCode":              lang_code,
                "enableWordTimeOffsets":     True,
                "enableSpeakerDiarization":  True,   # key flag
                "diarizationConfig": {
                    "enableSpeakerDiarization": True,
                    "minSpeakerCount": 1,
                    "maxSpeakerCount": 6,
                },
                "model": "latest_long",
            },
            "audio": {"content": audio_b64},
        }
        r = requests.post(
            f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}",
            json=payload, timeout=120)
        r.raise_for_status()

        # Diarization results come in the LAST result block
        results = r.json().get("results", [])
        if not results:
            return []

        # Last result has the speaker-tagged word list
        words = results[-1]["alternatives"][0].get("words", [])
        if not words:
            return []

        # Count total speech time per speaker tag
        speaker_time: dict[int, float] = {}
        speaker_segs: dict[int, list[tuple[float, float]]] = {}

        for w in words:
            tag   = w.get("speakerTag", 1)
            start = float(w["startTime"].rstrip("s"))
            end   = float(w["endTime"].rstrip("s"))
            speaker_time[tag] = speaker_time.get(tag, 0) + (end - start)
            speaker_segs.setdefault(tag, []).append((start, end))

        if not speaker_time:
            return []

        # Pick the speaker with the most total speech time
        primary_tag = max(speaker_time, key=speaker_time.__getitem__)

        # Merge consecutive word timestamps into segments
        raw_segs = sorted(speaker_segs[primary_tag])
        merged   = []
        for start, end in raw_segs:
            if merged and start - merged[-1][1] < 0.4:
                merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))

        return [{"start": s, "end": e} for s, e in merged]

    except Exception:
        return []


def extract_voice_sample(
    audio_path: str,
    work_dir:   str,
    lang_code:  str = "ru-RU",
    api_key:    str = "",
) -> bytes:
    """
    Extract a clean voice sample from the DOMINANT SPEAKER in the video.

    Strategy (in order of quality):
      1. Use Google STT speaker diarization to identify who speaks most,
         then extract and concatenate ONLY their audio segments.
         This is the only reliable way to avoid cloning the wrong speaker.
      2. If diarization fails or returns too little audio (<15s), fall back
         to a high-pass filtered 45-second clip from mid-video
         (avoids intros which often have male narrators).

    Key differences from the old approach:
      - Does NOT blindly grab the first 45 seconds
      - Does NOT use silenceremove (strips children's quieter voices)
      - Identifies the primary speaker by total speech time
      - Works for all voice types: male, female, children, elderly
    """
    out = os.path.join(work_dir, "voice_sample_clone.mp3")

    # ── Step 1: Diarization-based extraction ─────────────────────────────
    if api_key:
        segments = _identify_primary_speaker_segments(
            audio_path, lang_code, api_key)

        if segments:
            # Calculate total available speech from primary speaker
            total_speech = sum(s["end"] - s["start"] for s in segments)

            if total_speech >= 15:  # ElevenLabs needs at least 15s
                # Build ffmpeg concat filter to stitch only primary speaker
                # segments together
                concat_dir = tempfile.mkdtemp(prefix="ud_concat_")
                clip_paths = []

                for i, seg in enumerate(segments):
                    dur = seg["end"] - seg["start"]
                    if dur < 0.5:
                        continue  # skip very short words
                    clip = os.path.join(concat_dir, f"clip_{i:04d}.mp3")
                    try:
                        _run(["ffmpeg", "-y",
                              "-i", audio_path,
                              "-ss", str(seg["start"]),
                              "-t",  str(dur),
                              "-ar", "22050",
                              "-ac", "1",
                              "-c:a", "libmp3lame",
                              "-q:a", "3",
                              clip])
                        clip_paths.append(clip)
                    except Exception:
                        continue

                    # Stop once we have 45 seconds of speech
                    if sum(
                        get_duration(p) for p in clip_paths
                        if os.path.exists(p)
                    ) >= 45:
                        break

                if clip_paths:
                    try:
                        # Write ffmpeg concat list
                        list_file = os.path.join(concat_dir, "list.txt")
                        with open(list_file, "w") as lf:
                            for cp in clip_paths:
                                lf.write(f"file '{cp}'\n")

                        # Concatenate clips → apply loudnorm
                        _run(["ffmpeg", "-y",
                              "-f", "concat",
                              "-safe", "0",
                              "-i", list_file,
                              "-af", "loudnorm",
                              "-ar", "22050",
                              "-ac", "1",
                              "-c:a", "libmp3lame",
                              "-q:a", "3",
                              out])

                        shutil.rmtree(concat_dir, ignore_errors=True)

                        with open(out, "rb") as f:
                            return f.read()
                    except Exception:
                        pass

                shutil.rmtree(concat_dir, ignore_errors=True)

    # ── Step 2: Fallback - skip intro, grab from mid-video ───────────────
    # Skip the first 15% of the video (often intro/music with wrong speaker)
    # and grab 45s from there. Do NOT use silenceremove - it strips
    # children's quieter voices.
    total_dur  = get_duration(audio_path)
    skip_secs  = max(5.0, total_dur * 0.15)  # skip first 15%

    _run(["ffmpeg", "-y",
          "-i", audio_path,
          "-ss", str(skip_secs),
          "-t",  "45",
          "-af", "highpass=f=60,lowpass=f=10000,loudnorm",
          "-ar", "22050",
          "-ac", "1",
          "-c:a", "libmp3lame",
          "-q:a", "3",
          out])

    with open(out, "rb") as f:
        return f.read()


def el_clone_voice(name: str, sample: bytes, api_key: str) -> str:
    r = requests.post(
        "https://api.elevenlabs.io/v1/voices/add",
        headers={"xi-api-key": api_key},
        data={"name": name, "description": "Ultradub auto-clone"},
        files={"files": ("sample.mp3", sample, "audio/mpeg")},
        timeout=60)
    r.raise_for_status()
    return r.json()["voice_id"]


def el_synthesize(text: str, voice_id: str, api_key: str) -> bytes:
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text":     text[:GTTS_MAX_CHARS],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability":        0.75,   # higher = more consistent tone
                "similarity_boost": 0.90,   # higher = closer to cloned voice
                "style":            0.0,    # 0 = preserve original style
                "use_speaker_boost": True,  # better for non-standard voices
            },
        }, timeout=60)
    r.raise_for_status()
    return r.content


def el_delete_voice(voice_id: str, api_key: str) -> None:
    try:
        requests.delete(f"https://api.elevenlabs.io/v1/voices/{voice_id}",
                        headers={"xi-api-key": api_key}, timeout=15)
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# SYNCLABS - LIP SYNC
# ══════════════════════════════════════════════════════════════════════════════
def _upload_for_sync(path: str, api_key: str) -> str:
    """Upload a file to the lip-sync provider and return its URL.
    Customer videos are never sent to public file hosts; if the provider
    upload fails, lip sync is skipped and the customer is not charged for it."""
    with open(path, "rb") as f:
        r = requests.post("https://api.sync.so/v2/upload",
                          headers={"x-api-key": api_key},
                          files={"file": f}, timeout=180)
    r.raise_for_status()
    url = r.json().get("url") or r.json().get("fileUrl")
    if not url:
        raise RuntimeError("Lip-sync upload returned no file URL.")
    return url


def run_lipsync(video: str, audio: str, api_key: str, stat_ph) -> str:
    stat_ph.info("Uploading for lip-sync processing…")
    vu = _upload_for_sync(video, api_key)
    au = _upload_for_sync(audio, api_key)
    stat_ph.info("Lip-sync job submitted - processing…")
    r = requests.post("https://api.sync.so/v2/generate",
                      headers={"x-api-key": api_key,
                               "Content-Type": "application/json"},
                      json={"videoUrl": vu, "audioUrl": au,
                            "synergize": True, "maxCredits": 1000},
                      timeout=30)
    r.raise_for_status()
    jid = r.json()["id"]
    for tick in range(180):
        time.sleep(5)
        p = requests.get(f"https://api.sync.so/v2/generate/{jid}",
                         headers={"x-api-key": api_key}, timeout=15).json()
        stat_ph.info(f"Lip-sync: {p.get('status','processing')} ({tick*5}s)…")
        if p.get("status") == "completed":
            out = tempfile.mktemp(suffix="_ls.mp4")
            with open(out, "wb") as f:
                f.write(requests.get(p["outputUrl"], timeout=180).content)
            return out
        if p.get("status") == "failed":
            raise RuntimeError(f"Lip-sync failed: {p.get('error','unknown')}")
    raise TimeoutError("Lip-sync timed out after 15 minutes.")

# ══════════════════════════════════════════════════════════════════════════════
# CORE PIPELINE STEPS
# ══════════════════════════════════════════════════════════════════════════════
UPLOAD_DIR = os.path.join(VIDEO_STORE, "uploads")


def save_upload_once(f) -> tuple[str, float]:
    """Save an uploaded file to disk once per upload and return (path, duration)."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    token = str(getattr(f, "file_id", "") or f"{f.name}-{f.size}")
    cache = st.session_state.setdefault("upload_cache", {})
    hit = cache.get(token)
    if hit and os.path.exists(hit["path"]):
        return hit["path"], hit["duration"]
    ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else "mp4"
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}.{ext}")
    with open(path, "wb") as out:
        out.write(f.getbuffer())
    duration = get_duration(path)
    cache[token] = {"path": path, "duration": duration}
    return path, duration


def step_prepare_video(raw: str, work_dir: str) -> str:
    """Copy the upload into the work folder, converting to MP4 when needed."""
    ext = raw.rsplit(".", 1)[-1].lower()
    if ext == "mp4":
        dst = os.path.join(work_dir, "source.mp4")
        shutil.copy2(raw, dst)
        return dst
    mp4 = os.path.join(work_dir, "source.mp4")
    _run(["ffmpeg", "-y", "-i", raw,
          "-c:v", "libx264", "-c:a", "aac",
          "-movflags", "+faststart", mp4])
    return mp4


def step_extract_audio(video: str, out: str) -> None:
    """
    Extract audio from video and re-encode to 16kHz mono MP3.
    Explicit re-encoding is critical for phone-recorded videos
    (iPhone MOV, Android MP4) which use AAC/HEVC codecs that
    Google STT rejects when stream-copied. We force:
      - 16kHz sample rate (Google STT optimal)
      - mono channel (removes stereo phase issues)
      - libmp3lame encoding (universal compatibility)
    """
    _run(["ffmpeg", "-y", "-i", video,
          "-vn",
          "-ar", "16000",
          "-ac", "1",
          "-acodec", "libmp3lame",
          "-q:a", "3",
          out])


def make_silence(dur: float, out: str) -> None:
    _run(["ffmpeg", "-y", "-f", "lavfi",
          "-i", "anullsrc=r=24000:cl=mono",
          "-t", str(max(dur, 0.1)), "-q:a", "9", out])


def step_synthesise_lang(segs: list[dict], lang_key: str, work_dir: str,
                          gkey: str, use_clone: bool = False,
                          clone_id: str = "", el_key: str = "") -> list[dict]:
    """Synthesise one language pass. Returns segments with tts_path added."""
    out   = []
    ldir  = os.path.join(work_dir, f"tts_{lang_key}")
    os.makedirs(ldir, exist_ok=True)

    for i, seg in enumerate(segs):
        text = seg.get(f"translated_{lang_key}", seg.get("translated", "")).strip()
        path = os.path.join(ldir, f"tts_{i:04d}.mp3")
        if text:
            try:
                data = (el_synthesize(text, clone_id, el_key)
                        if use_clone and clone_id and el_key
                        else synthesize_text(text, lang_key, gkey))
                if data:
                    with open(path, "wb") as f:
                        f.write(data)
                else:
                    make_silence(seg["end"] - seg["start"], path)
            except Exception:
                make_silence(seg["end"] - seg["start"], path)
        else:
            make_silence(seg["end"] - seg["start"], path)
        out.append({**seg, "tts_path": path})
    return out


def step_merge(video: str, segs: list[dict],
               duration: float, work_dir: str,
               no_vocals_path: str | None = None,
               suffix: str = "") -> str:
    """Build dubbed audio track and mux onto video. Optionally blend music."""
    sil = os.path.join(work_dir, f"silence{suffix}.mp3")
    make_silence(duration + 2, sil)

    inputs, delays, filters = ["-i", sil], ["[0:a]"], []
    for i, seg in enumerate(segs):
        inputs += ["-i", seg["tts_path"]]
        ms      = int(seg["start"] * 1000)
        lbl     = f"[d{i}]"
        filters.append(f"[{i+1}:a]adelay={ms}|{ms}{lbl}")
        delays.append(lbl)

    mix = "".join(delays)
    filters.append(f"{mix}amix=inputs={len(delays)}:normalize=0[dubbed]")

    dubbed_mp3 = os.path.join(work_dir, f"dubbed{suffix}.mp3")

    if no_vocals_path and os.path.exists(no_vocals_path):
        # Blend dubbed voice + original music.
        # music_in = number of inputs already added before no_vocals.
        # inputs has: ["-i", sil] + ["-i", tts] * len(segs) = 1 + len(segs) inputs.
        # Each input is 2 list items, so actual input count = len(inputs) // 2.
        music_in = len(inputs) // 2  # correct 0-based index for no_vocals
        inputs  += ["-i", no_vocals_path]
        filters.append(f"[dubbed][{music_in}:a]amix=inputs=2:weights=1 0.6:normalize=0[aout]")
    else:
        filters[-1] = filters[-1].replace("[dubbed]", "[aout]")

    _run(["ffmpeg", "-y"] + inputs + [
        "-filter_complex", ";".join(filters),
        "-map", "[aout]", "-t", str(duration), dubbed_mp3])

    final = os.path.join(work_dir, f"final{suffix}.mp4")
    _run(["ffmpeg", "-y",
          "-i", video, "-i", dubbed_mp3,
          "-map", "0:v", "-map", "1:a",
          "-c:v", "copy", "-c:a", "aac", "-shortest", final])
    return final


def make_preview(full: str, out: str) -> str:
    wm = "PREVIEW ONLY  *  ULTRADUB  *  Purchase to unlock the full video"
    _run(["ffmpeg", "-y", "-i", full, "-t", str(PREVIEW_SECONDS),
          "-vf", (f"drawtext=text='{wm}':"
                  "fontcolor=white@0.9:fontsize=13:"
                  "box=1:boxcolor=black@0.65:boxborderw=10:"
                  "x=(w-text_w)/2:y=h-th-22"),
          "-c:a", "copy", out])
    return out

# ══════════════════════════════════════════════════════════════════════════════
# STRIPE
# ══════════════════════════════════════════════════════════════════════════════
def stripe_create(amount: float, vk: str, sk: str, app_url: str,
                  description: str) -> str:
    import stripe as _s
    _s.api_key = sk
    base = app_url.rstrip("/")
    s = _s.checkout.Session.create(
        # No payment_method_types: Stripe shows whatever is enabled in the
        # dashboard (cards, Apple Pay, Google Pay, Link).
        line_items=[{"price_data": {
            "currency": "usd",
            "product_data": {"name": "Ultradub dubbed video",
                             "description": description},
            "unit_amount": int(round(amount * 100)),
        }, "quantity": 1}],
        mode="payment",
        success_url=(f"{base}?payment=success"
                     f"&session_id={{CHECKOUT_SESSION_ID}}"),
        cancel_url=f"{base}?payment=cancelled",
        metadata={"video_key": vk},
    )
    return s.url


def stripe_paid_session(sid: str, sk: str):
    """Return the Checkout Session if it is paid, otherwise None."""
    import stripe as _s
    _s.api_key = sk
    try:
        s = _s.checkout.Session.retrieve(sid)
        if s.payment_status == "paid":
            return s
    except Exception:
        traceback.print_exc()
    return None


def stripe_refund(session, sk: str) -> bool:
    """Refund a paid session in full. Safe to call more than once."""
    import stripe as _s
    _s.api_key = sk
    try:
        _s.Refund.create(payment_intent=session.payment_intent,
                         idempotency_key=f"ultradub-refund-{session.id}")
        return True
    except Exception:
        traceback.print_exc()
        return False


# ══════════════════════════════════════════════════════════════════════════════
# STORAGE CLEANUP - finished videos are kept for 24 hours
# ══════════════════════════════════════════════════════════════════════════════
KEEP_HOURS = 24


@st.cache_resource(ttl=3600)
def sweep_store() -> bool:
    cutoff = time.time() - KEEP_HOURS * 3600
    for p in Path(VIDEO_STORE).rglob("*"):
        try:
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
        except Exception:
            pass
    return True


# ══════════════════════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════════════════════
class UserFacingError(Exception):
    """An error whose message is safe and useful to show the customer."""


sweep_store()

GKEY  = cfg("GOOGLE_API_KEY")
SKEY  = cfg("STRIPE_SECRET_KEY")
AURL  = cfg("APP_URL")
ELKEY = cfg("ELEVENLABS_API_KEY")
SLKEY = cfg("SYNCLABS_API_KEY")
SUPPORT_EMAIL = cfg("SUPPORT_EMAIL")

CONFIG_MISSING = [k for k, v in [("GOOGLE_API_KEY", GKEY),
                                 ("STRIPE_SECRET_KEY", SKEY),
                                 ("APP_URL", AURL)] if not v]
if CONFIG_MISSING:
    print(f"[ultradub] Missing settings: {', '.join(CONFIG_MISSING)}")

APP_DIR = Path(__file__).resolve().parent

DEFAULTS: dict = {
    "done":          False,
    "preview_bytes": None,
    "quote":         None,
    "checkout_url":  None,
    "result_langs":  [],
    "result_voice":  False,
    "result_lips":   False,
    "notes":         [],
}


def reset_results() -> None:
    for k, v in DEFAULTS.items():
        st.session_state[k] = list(v) if isinstance(v, list) else v


for k in DEFAULTS:
    if k not in st.session_state:
        reset_results()
        break


# ── Small helpers ─────────────────────────────────────────────────────────────
def lang_name(key: str) -> str:
    return SITE_NAMES.get(key) or LANG_LABELS.get(key, key)


def join_names(names: list[str]) -> str:
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def fmt_len(sec: float) -> str:
    sec = int(round(sec))
    if sec < 60:
        return f"{sec} second"
    m, s = divmod(sec, 60)
    return f"{m} min {s} s" if s else f"{m} min"


def demo_source(local: str, url_key: str):
    url = cfg(url_key)
    if url:
        return url
    p = APP_DIR / local
    return str(p) if p.exists() else None


def render_top() -> None:
    st.markdown(
        '<div class="ud-top"><div class="ud-wordmark">Ultra<span>dub</span></div>'
        '<div class="ud-top-note">No account needed</div></div>',
        unsafe_allow_html=True)


def render_footer() -> None:
    contact = ""
    if SUPPORT_EMAIL:
        e = html.escape(SUPPORT_EMAIL)
        contact = f'Questions? <a href="mailto:{e}">{e}</a>'
    st.markdown(
        f'<div class="ud-foot"><div>© 2026 Ultradub</div><div>{contact}</div></div>',
        unsafe_allow_html=True)


def render_progress(ph, steps: list[tuple[str, str]], current: str,
                    done_ids: set, note: str) -> None:
    rows = ""
    for sid, name in steps:
        if sid in done_ids:
            cls, ic = "done", "✓"
        elif sid == current:
            cls, ic = "active", "●"
        else:
            cls, ic = "", "○"
        rows += (f'<div class="ud-step {cls}"><span class="ic">{ic}</span>'
                 f'<span>{html.escape(name)}</span></div>')
    ph.markdown(
        f'<div class="ud-steps"><div class="ud-steps-title">Working on your video'
        f'<small>{html.escape(note)}</small></div>{rows}</div>',
        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AFTER PAYMENT - DELIVERY PAGE
# ══════════════════════════════════════════════════════════════════════════════
params   = st.query_params
p_status = params.get("payment", "")
p_sid    = params.get("session_id", "")


def render_delivery(sid: str) -> None:
    key = f"delivery_{sid}"
    if key not in st.session_state:
        sess = stripe_paid_session(sid, SKEY) if SKEY else None
        if not sess:
            st.session_state[key] = {"status": "unpaid"}
        else:
            md = getattr(sess, "metadata", None)
            vk = md["video_key"] if md is not None and "video_key" in md else ""
            valid = bool(re.fullmatch(r"[0-9a-f]{32}", vk or ""))
            vids = sorted(Path(VIDEO_STORE).glob(f"{vk}_*.mp4")) if valid else []
            if vids:
                st.session_state[key] = {"status": "ok", "vk": vk}
            else:
                refunded = stripe_refund(sess, SKEY)
                st.session_state[key] = {"status": "missing", "refunded": refunded}

    info = st.session_state[key]

    if info["status"] == "ok":
        vk = info["vk"]
        vids = sorted(Path(VIDEO_STORE).glob(f"{vk}_*.mp4"))
        st.markdown(
            '<div class="ud-done"><h2>Payment confirmed</h2>'
            '<p>Your videos are ready. These download links stay active for 24 hours.</p></div>',
            unsafe_allow_html=True)
        if not vids:
            st.warning("These files have expired. "
                       + (f"Email {SUPPORT_EMAIL} and we'll sort it out."
                          if SUPPORT_EMAIL else "Contact us and we'll sort it out."))
        for fp in vids:
            lk = fp.stem[len(vk) + 1:]
            name = lang_name(lk)
            data = fp.read_bytes()
            st.markdown(f"**{name}**")
            st.video(data)
            st.download_button(f"Download {name} video", data=data,
                               file_name=f"ultradub_{lk}.mp4", mime="video/mp4",
                               use_container_width=True, key=f"dl_{fp.name}")
            srt = fp.with_suffix(".srt")
            if srt.exists():
                st.download_button(f"Download {name} subtitles",
                                   data=srt.read_text(encoding="utf-8"),
                                   file_name=f"ultradub_{lk}.srt", mime="text/plain",
                                   use_container_width=True, key=f"dls_{fp.name}")

    elif info["status"] == "missing":
        if info.get("refunded"):
            st.error("Your payment went through, but the finished video was lost when "
                     "our server restarted. We've refunded you in full. The refund "
                     "usually shows on your statement within 5 to 10 business days.")
        else:
            st.error("Your payment went through, but the finished video was lost when "
                     "our server restarted. "
                     + (f"Email {SUPPORT_EMAIL} and we'll refund you right away."
                        if SUPPORT_EMAIL else "Contact us and we'll refund you right away."))
    else:
        st.warning("We couldn't confirm this payment. If you were charged, contact us "
                   "and we'll fix it.")

    if st.button("Dub another video", use_container_width=True, key="again"):
        st.query_params.clear()
        st.rerun()


if p_status == "success" and p_sid:
    render_top()
    render_delivery(p_sid)
    render_footer()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
render_top()

if p_status == "cancelled":
    st.info("Payment cancelled. You weren't charged.")
    st.query_params.clear()

st.markdown(
    '<div class="ud-hero"><h1>Speak once. Be heard in 20 languages.</h1>'
    '<p>Upload a video you recorded. Ultradub translates what you say, dubs it in a '
    'natural voice or your own, and keeps your background sound. Watch a free '
    '15-second preview before you pay.</p></div>',
    unsafe_allow_html=True)

# ── Demo: original vs dubbed ─────────────────────────────────────────────────
demo_orig = demo_source(DEMO_ORIGINAL, "DEMO_ORIGINAL_URL")
demo_dub  = demo_source(DEMO_DUBBED, "DEMO_DUBBED_URL")
if demo_orig and demo_dub:
    caption = cfg("DEMO_CAPTION") or DEMO_CAPTION
    st.markdown(
        '<div class="ud-demo-head">Hear the difference</div>'
        f'<div class="ud-demo-cap">{html.escape(caption)}</div>',
        unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown('<div class="ud-clip-label">Original</div>', unsafe_allow_html=True)
        st.video(demo_orig)
    with dc2:
        st.markdown('<div class="ud-clip-label dubbed">Dubbed by Ultradub</div>',
                    unsafe_allow_html=True)
        st.video(demo_dub)

# ── Form ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ud-form-head">Dub your video</div>'
    '<div class="ud-form-sub">A video you recorded on your phone or camera. '
    'MP4 or MOV, up to 200 MB and 60 minutes.</div>',
    unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Your video", type=["mp4", "mov", "m4v", "webm", "mkv", "avi"],
    label_visibility="collapsed")

video_path, duration = None, 0.0
if uploaded is not None:
    try:
        video_path, duration = save_upload_once(uploaded)
        if duration > TIERS[-1]["max_min"] * 60:
            st.error(f"This video is {duration / 60:.0f} minutes long. "
                     f"The limit is {TIERS[-1]['max_min']} minutes.")
            video_path = None
        else:
            st.markdown(f'<div class="ud-meta">{fmt_len(duration)} video</div>',
                        unsafe_allow_html=True)
    except Exception:
        traceback.print_exc()
        st.error("We couldn't read this file. Try exporting it again as an MP4.")
        video_path = None

c1, c2 = st.columns(2)
with c1:
    src_name = st.selectbox("Language you speak in the video",
                            [n for _, n in SITE_LANGS], index=0)
    src_key = NAME_TO_KEY[src_name]
with c2:
    tgt_names = st.multiselect(
        "Dub it into",
        [n for k, n in SITE_LANGS if k != src_key],
        max_selections=MAX_TARGETS,
        placeholder="Choose up to 3")
tgt_keys = [NAME_TO_KEY[n] for n in tgt_names]
st.caption("Pick up to 3 languages. The third one is free.")

own_voice = False
if ELKEY:
    unsupported = [SITE_NAMES[k] for k in tgt_keys if k not in CLONE_OK]
    choice = st.radio(
        "Voice",
        ["Natural AI voice", f"My own voice (+${CLONE_ADDON:.2f})"],
        horizontal=True, disabled=bool(unsupported))
    own_voice = choice.startswith("My own") and not unsupported
    if unsupported:
        st.caption(f"Your own voice isn't available in {join_names(unsupported)} yet. "
                   "Remove it to use your own voice.")

lipsync = False
if SLKEY:
    if duration:
        ls_label = f"Match lip movements (+${LIPSYNC_ADDON[get_tier(duration)['name']]:.2f})"
    else:
        ls_label = "Match lip movements (from +$5.00)"
    lipsync = st.checkbox(
        ls_label,
        help="Adjusts mouth movements to fit the new language. "
             "Adds several minutes of processing.")

# ── Live price ───────────────────────────────────────────────────────────────
if video_path and tgt_keys:
    q = compute_quote(duration, tgt_keys, lipsync, own_voice)
    parts = [f"Dubbing, {q['n_langs']} language{'s' if q['n_langs'] > 1 else ''}: "
             f"${q['lang_price']:.2f}"]
    if q["savings"]:
        parts.append("Third language: free")
    if q["clone"]:
        parts.append(f"Your own voice: ${q['clone']:.2f}")
    if q["ls"]:
        parts.append(f"Lip matching: ${q['ls']:.2f}")
    st.markdown(
        '<div class="ud-price"><span class="ud-price-label">Your price</span>'
        f'<span class="ud-price-value">${q["total"]:.2f}</span></div>'
        f'<div class="ud-price-lines">{"<br>".join(parts)}</div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="ud-price"><span class="ud-price-label">Your price</span>'
        '<span class="ud-price-value muted">Upload a video and pick a language</span></div>',
        unsafe_allow_html=True)

if CONFIG_MISSING:
    st.warning("Dubbing is temporarily unavailable. Please check back soon.")

ready = bool(video_path and tgt_keys and not CONFIG_MISSING)
run_btn = st.button("Make my free preview", type="primary",
                    use_container_width=True, disabled=not ready)

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if run_btn and ready:
    reset_results()
    prog_ph = st.empty()
    note_ph = st.empty()

    steps = [("prepare",    "Reading your video"),
             ("separate",   "Separating your voice from background sound"),
             ("transcribe", "Transcribing what you say"),
             ("translate",  "Translating")]
    if own_voice:
        steps.append(("clone", "Learning your voice"))
    steps.append(("dub", "Recording the dub"))
    if lipsync:
        steps.append(("lipsync", "Matching lip movements"))
    steps.append(("preview", "Making your preview"))

    eta = estimate_eta(duration / 60, len(tgt_keys), own_voice, lipsync, False)
    eta_total = sum(v for k, v in eta.items() if k != "download")
    eta_note = f"About {max(1, round(eta_total / 60))} min. Keep this tab open."

    done_ids: set = set()
    work_dir = tempfile.mkdtemp(prefix="ultradub_")
    clone_id, clone_done, lips_done = "", False, False
    notes: list[str] = []

    def at(sid: str) -> None:
        render_progress(prog_ph, steps, sid, done_ids, eta_note)

    try:
        at("prepare")
        src_video = step_prepare_video(video_path, work_dir)
        audio_path = os.path.join(work_dir, "audio.mp3")
        step_extract_audio(src_video, audio_path)
        done_ids.add("prepare")

        at("separate")
        no_vocals_path = None
        audio_for_stt = audio_path
        try:
            vocals_path, no_vocals_path = separate_music(audio_path, work_dir)
            audio_for_stt = vocals_path
        except Exception:
            traceback.print_exc()
        done_ids.add("separate")

        at("transcribe")
        segs, _ = transcribe_audio(audio_for_stt, src_key, GKEY)
        if not segs and audio_for_stt != audio_path:
            segs, _ = transcribe_audio(audio_path, src_key, GKEY)
        if not segs:
            raise UserFacingError(
                f"We couldn't hear any {lang_name(src_key)} speech in this video. "
                "Check that you picked the language you speak and that your voice "
                "is clear. You haven't been charged.")
        done_ids.add("transcribe")

        at("translate")
        texts = [s["text"] for s in segs]
        srts: dict[str, str] = {}
        for lk in tgt_keys:
            translated = translate_batch(texts, lk, GKEY)
            for seg, tr in zip(segs, translated):
                seg[f"translated_{lk}"] = tr
            srts[lk] = generate_srt(segs, f"translated_{lk}")
        done_ids.add("translate")

        if own_voice:
            at("clone")
            try:
                sample = extract_voice_sample(
                    audio_for_stt, work_dir,
                    lang_code=LANG_REGISTRY[src_key]["stt"], api_key=GKEY)
                clone_id = el_clone_voice(f"ud_{uuid.uuid4().hex[:8]}", sample, ELKEY)
                clone_done = True
            except Exception:
                traceback.print_exc()
                notes.append("We couldn't learn your voice from this recording, so "
                             "the dub uses a natural AI voice. You won't be charged "
                             "for your own voice.")
            done_ids.add("clone")

        at("dub")
        vk = uuid.uuid4().hex
        finals: dict[str, str] = {}
        for lk in tgt_keys:
            lsegs = step_synthesise_lang(segs, lk, work_dir, GKEY,
                                         use_clone=clone_done,
                                         clone_id=clone_id, el_key=ELKEY)
            finals[lk] = step_merge(src_video, lsegs, duration, work_dir,
                                    no_vocals_path=no_vocals_path,
                                    suffix=f"_{lk}")
        done_ids.add("dub")

        if lipsync:
            at("lipsync")
            try:
                synced: dict[str, str] = {}
                for lk in tgt_keys:
                    dub_audio = os.path.join(work_dir, f"lipsync_audio_{lk}.mp3")
                    step_extract_audio(finals[lk], dub_audio)
                    synced[lk] = run_lipsync(src_video, dub_audio, SLKEY, note_ph)
                finals.update(synced)
                lips_done = True
            except Exception:
                traceback.print_exc()
                notes.append("Lip matching didn't work for this video, so it isn't "
                             "included and you won't be charged for it.")
            note_ph.empty()
            done_ids.add("lipsync")

        at("preview")
        os.makedirs(VIDEO_STORE, exist_ok=True)
        for lk, fp in finals.items():
            shutil.copy2(fp, os.path.join(VIDEO_STORE, f"{vk}_{lk}.mp4"))
            with open(os.path.join(VIDEO_STORE, f"{vk}_{lk}.srt"), "w",
                      encoding="utf-8") as f:
                f.write(srts.get(lk, ""))
        preview_path = os.path.join(work_dir, "preview.mp4")
        make_preview(os.path.join(VIDEO_STORE, f"{vk}_{tgt_keys[0]}.mp4"), preview_path)
        preview_bytes = Path(preview_path).read_bytes()

        # Charge only for what was actually delivered.
        quote = compute_quote(duration, tgt_keys, lips_done, clone_done)
        desc = (f"{quote['dur']} min video dubbed into "
                f"{join_names([lang_name(k) for k in tgt_keys])}")
        checkout_url = stripe_create(quote["total"], vk, SKEY, AURL, desc)
        done_ids.add("preview")
        render_progress(prog_ph, steps, "", done_ids, "Done")

        st.session_state.update(
            done=True, preview_bytes=preview_bytes, quote=quote,
            checkout_url=checkout_url, result_langs=list(tgt_keys),
            result_voice=clone_done, result_lips=lips_done, notes=notes)

    except UserFacingError as e:
        prog_ph.empty()
        st.error(str(e))
    except Exception:
        traceback.print_exc()
        prog_ph.empty()
        st.error("Something went wrong while dubbing this video. You haven't been "
                 "charged. Try again, or try a shorter clip.")
    finally:
        if clone_id and ELKEY:
            el_delete_voice(clone_id, ELKEY)
        shutil.rmtree(work_dir, ignore_errors=True)

# ══════════════════════════════════════════════════════════════════════════════
# PREVIEW + PAY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.done and st.session_state.preview_bytes:
    q = st.session_state.quote
    langs = st.session_state.result_langs
    names = join_names([lang_name(k) for k in langs])

    st.markdown('<div class="ud-result-head">Your free preview</div>',
                unsafe_allow_html=True)
    for n in st.session_state.notes:
        st.info(n)
    st.video(st.session_state.preview_bytes)

    extras = []
    if st.session_state.result_voice:
        extras.append("in your own voice")
    if st.session_state.result_lips:
        extras.append("with lip matching")
    what = names + (" " + " and ".join(extras) if extras else "")
    st.caption(f"The first 15 seconds in {lang_name(langs[0])}. You're buying: {what}. "
               "Every version comes with a subtitle file.")

    rows = (f'<div class="ud-qline"><span>Dubbing ({q["dur"]} min, {q["n_langs"]} '
            f'language{"s" if q["n_langs"] > 1 else ""})</span>'
            f'<span>${q["lang_price"]:.2f}</span></div>')
    if q["savings"]:
        rows += '<div class="ud-qline"><span>Third language</span><span>Free</span></div>'
    if q["clone"]:
        rows += (f'<div class="ud-qline"><span>Your own voice</span>'
                 f'<span>${q["clone"]:.2f}</span></div>')
    if q["ls"]:
        rows += (f'<div class="ud-qline"><span>Lip matching</span>'
                 f'<span>${q["ls"]:.2f}</span></div>')
    rows += (f'<div class="ud-qline total"><span>Total</span>'
             f'<span>${q["total"]:.2f}</span></div>')
    st.markdown(f'<div class="ud-quote">{rows}</div>', unsafe_allow_html=True)

    url = html.escape(st.session_state.checkout_url or "", quote=True)
    st.markdown(
        f'<a class="ud-pay-btn" href="{url}" target="_top">'
        f'Pay ${q["total"]:.2f} and download</a>'
        '<div class="ud-pay-note">Secure checkout by Stripe. '
        'Your downloads open right after payment.</div>',
        unsafe_allow_html=True)

    st.write("")
    if st.button("Start over", use_container_width=True):
        reset_results()
        st.rerun()

render_footer()
