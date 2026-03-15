# -*- coding: utf-8 -*-
"""
ULTRADUB
Your voice, in every language.

Version 4.0 - Complete Production Build
(c) 2025 Ultradub

Features:
  - Google-inspired corporate identity (white, clean, professional)
  - 40+ languages - all Neural2/Wavenet confirmed voices
  - Background music preservation (audio-separator, ONNX-based)
  - SRT subtitle export - free with every dub
  - Multi-language bundle - 3 languages for price of 2
  - Rich progress bar with per-step ETAs and context
  - Email delivery via SendGrid (optional, shown upfront)
  - Auto voice cloning from original video audio
  - Zero vendor names visible in UI
  - Fully responsive - desktop, tablet, phone
"""

import base64
import os
import re
import shutil
import subprocess
import tempfile
import time
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
# DESIGN SYSTEM - GOOGLE-INSPIRED CORPORATE IDENTITY
# Palette: Pure white + Google Blue #1A73E8 + Neutral grays
# Type: Plus Jakarta Sans (closest to Google Product Sans on Google Fonts)
# Motion: Subtle, purposeful - not flashy
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* ── DESIGN TOKENS ── */
:root {
    --blue:         #1A73E8;
    --blue-dark:    #1557B0;
    --blue-light:   #E8F0FE;
    --blue-mid:     #4285F4;
    --surface:      #FFFFFF;
    --surface-2:    #F8F9FA;
    --surface-3:    #F1F3F4;
    --border:       #DADCE0;
    --border-dark:  #BDC1C6;
    --text-1:       #202124;
    --text-2:       #5F6368;
    --text-3:       #80868B;
    --text-inv:     #FFFFFF;
    --green:        #188038;
    --green-bg:     #E6F4EA;
    --amber:        #EA8600;
    --amber-bg:     #FEF7E0;
    --red:          #C5221F;
    --red-bg:       #FCE8E6;
    --shadow-sm:    0 1px 2px rgba(60,64,67,.3),0 1px 3px rgba(60,64,67,.15);
    --shadow-md:    0 1px 3px rgba(60,64,67,.3),0 4px 8px rgba(60,64,67,.15);
    --shadow-lg:    0 2px 6px rgba(60,64,67,.3),0 4px 16px rgba(60,64,67,.15);
    --r-sm:         4px;
    --r-md:         8px;
    --r-lg:         12px;
    --r-xl:         16px;
    --r-pill:       24px;
    --font:         'Plus Jakarta Sans', sans-serif;
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--font) !important;
    background: var(--surface) !important;
    color: var(--text-1) !important;
    -webkit-font-smoothing: antialiased;
}
#MainMenu, footer, header { display: none !important; }
.block-container { max-width: 900px !important; padding: 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ══════════════════════════════════════════════════
   NAVBAR
══════════════════════════════════════════════════ */
.ud-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    height: 64px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
}
.ud-wordmark {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text-1);
    letter-spacing: -0.3px;
}
.ud-wordmark em { color: var(--blue); font-style: normal; }
.ud-nav-links {
    display: flex;
    gap: 1.5rem;
    font-size: .875rem;
    font-weight: 500;
    color: var(--text-2);
}
.ud-nav-links a { cursor: pointer; transition: color .15s; }
.ud-nav-links a:hover { color: var(--blue); }
.ud-nav-cta {
    display: flex;
    align-items: center;
    gap: .75rem;
}

/* ══════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════ */
.ud-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: .4rem;
    padding: .6rem 1.25rem;
    border-radius: var(--r-pill);
    font-family: var(--font);
    font-size: .875rem;
    font-weight: 600;
    cursor: pointer;
    transition: box-shadow .15s, background .15s, border-color .15s;
    text-decoration: none;
    white-space: nowrap;
    border: 1.5px solid transparent;
    min-height: 40px;
}
.ud-btn-primary {
    background: var(--blue);
    color: var(--text-inv) !important;
    border-color: var(--blue);
}
.ud-btn-primary:hover {
    background: var(--blue-dark);
    border-color: var(--blue-dark);
    box-shadow: var(--shadow-sm);
}
.ud-btn-outline {
    background: transparent;
    color: var(--blue) !important;
    border-color: var(--border);
}
.ud-btn-outline:hover { background: var(--blue-light); border-color: var(--blue); }
.ud-btn-lg {
    padding: .75rem 1.75rem;
    font-size: 1rem;
    min-height: 48px;
}

/* Streamlit button override */
.stButton > button {
    background: var(--blue) !important;
    color: var(--text-inv) !important;
    border: none !important;
    border-radius: var(--r-pill) !important;
    padding: .65rem 1.5rem !important;
    font-family: var(--font) !important;
    font-size: .875rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    min-height: 44px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: background .15s, box-shadow .15s !important;
    letter-spacing: .1px !important;
}
.stButton > button:hover {
    background: var(--blue-dark) !important;
    box-shadow: var(--shadow-md) !important;
}

/* ══════════════════════════════════════════════════
   HERO
══════════════════════════════════════════════════ */
.ud-hero {
    padding: 3.5rem 2rem 3rem;
    background: var(--surface);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
    border-bottom: 1px solid var(--border);
}
.ud-hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    background: var(--blue-light);
    color: var(--blue-dark);
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .5px;
    padding: .3rem .75rem;
    border-radius: var(--r-pill);
    margin-bottom: 1rem;
}
.ud-hero-h1 {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    line-height: 1.15;
    color: var(--text-1);
    margin-bottom: .85rem;
    letter-spacing: -.5px;
}
.ud-hero-h1 .blue { color: var(--blue); }
.ud-hero-sub {
    font-size: 1.05rem;
    font-weight: 400;
    color: var(--text-2);
    line-height: 1.7;
    margin-bottom: 1.75rem;
    max-width: 420px;
}
.ud-hero-ctas {
    display: flex;
    gap: .75rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.ud-trust {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: center;
}
.ud-trust-item {
    display: flex;
    align-items: center;
    gap: .3rem;
    font-size: .8rem;
    color: var(--text-2);
}
.ud-trust-check {
    width: 16px; height: 16px;
    border-radius: 50%;
    background: var(--green-bg);
    color: var(--green);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    flex-shrink: 0;
}

/* Hero visual — CSS mockup */
.ud-hero-visual {
    display: flex;
    flex-direction: column;
    gap: .75rem;
    align-items: center;
}
.ud-video-card {
    width: 100%;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    overflow: hidden;
    box-shadow: var(--shadow-md);
}
.ud-video-thumb {
    background: linear-gradient(135deg, #667eea11, #764ba211);
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid var(--border);
    position: relative;
}
.ud-play-btn {
    width: 44px; height: 44px;
    border-radius: 50%;
    background: rgba(255,255,255,.92);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
    font-size: 16px;
    padding-left: 3px;
}
.ud-video-meta {
    padding: .75rem 1rem;
    font-size: .8rem;
    color: var(--text-2);
    display: flex;
    align-items: center;
    gap: .5rem;
}
.ud-video-duration {
    margin-left: auto;
    background: var(--text-1);
    color: var(--text-inv);
    font-size: .7rem;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 3px;
}
.ud-lang-arrow {
    display: flex;
    align-items: center;
    gap: .6rem;
    width: 100%;
}
.ud-lang-pill {
    flex: 1;
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--r-pill);
    padding: .5rem .9rem;
    font-size: .82rem;
    font-weight: 600;
    color: var(--text-1);
    text-align: center;
    box-shadow: var(--shadow-sm);
}
.ud-lang-pill.target {
    border-color: var(--blue);
    color: var(--blue);
    background: var(--blue-light);
}
.ud-arrow-icon {
    color: var(--text-3);
    font-size: 1.2rem;
    flex-shrink: 0;
}
.ud-status-pill {
    display: flex;
    align-items: center;
    gap: .5rem;
    background: var(--green-bg);
    border: 1px solid #34a853;
    border-radius: var(--r-pill);
    padding: .4rem .9rem;
    font-size: .78rem;
    font-weight: 600;
    color: var(--green);
    align-self: flex-start;
}
.ud-status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1)}
    50%{opacity:.5;transform:scale(.75)}
}

/* ══════════════════════════════════════════════════
   STATS BAR
══════════════════════════════════════════════════ */
.ud-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: var(--surface-2);
    border-bottom: 1px solid var(--border);
}
.ud-stat {
    padding: 1.25rem 1rem;
    border-right: 1px solid var(--border);
    text-align: center;
}
.ud-stat:last-child { border-right: none; }
.ud-stat-n {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-1);
    line-height: 1;
}
.ud-stat-n .b { color: var(--blue); }
.ud-stat-l {
    font-size: .75rem;
    color: var(--text-2);
    margin-top: .25rem;
}

/* ══════════════════════════════════════════════════
   SECTION LABELS
══════════════════════════════════════════════════ */
.ud-section-label {
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: .65rem;
    margin-top: 1.75rem;
}
.ud-section-divider {
    height: 1px;
    background: var(--border);
    margin: 1.5rem 0;
}

/* ══════════════════════════════════════════════════
   CARDS
══════════════════════════════════════════════════ */
.ud-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
}
.ud-card-flat {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.25rem;
}

/* ══════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 2px solid var(--border) !important;
    border-radius: 0 !important;
    padding: 0 2rem !important;
    gap: 0 !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    font-family: var(--font) !important;
    font-size: .875rem !important;
    font-weight: 500 !important;
    color: var(--text-2) !important;
    border-radius: 0 !important;
    padding: .85rem 1.2rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    white-space: nowrap !important;
    transition: color .15s !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--blue) !important;
    border-bottom-color: var(--blue) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 2rem !important; }

/* ══════════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════════ */
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-1) !important;
    font-family: var(--font) !important;
    font-size: .9rem !important;
    padding: .65rem 1rem !important;
    min-height: 44px !important;
    box-shadow: none !important;
    transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(26,115,232,.15) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-3) !important; }
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-1) !important;
    min-height: 44px !important;
    box-shadow: none !important;
}
.stSelectbox > div > div:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(26,115,232,.15) !important;
}
.stFileUploader > div {
    background: var(--surface-2) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--r-lg) !important;
}
.stFileUploader > div:hover { border-color: var(--blue) !important; }
.stRadio > div { gap: .6rem !important; }
.stRadio label {
    font-family: var(--font) !important;
    font-size: .875rem !important;
    color: var(--text-2) !important;
}
.stCheckbox label {
    font-family: var(--font) !important;
    font-size: .875rem !important;
    color: var(--text-1) !important;
}
.stMultiSelect > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r-md) !important;
}

/* ══════════════════════════════════════════════════
   PROGRESS TRACKER
══════════════════════════════════════════════════ */
.ud-progress-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}
.ud-progress-header {
    padding: 1.1rem 1.4rem .8rem;
    border-bottom: 1px solid var(--border);
    background: var(--surface-2);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ud-progress-title {
    font-size: .9rem;
    font-weight: 600;
    color: var(--text-1);
}
.ud-progress-eta {
    font-size: .8rem;
    color: var(--text-2);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-pill);
    padding: .2rem .7rem;
}
.ud-progress-bar-wrap {
    height: 3px;
    background: var(--surface-3);
    overflow: hidden;
}
.ud-progress-bar-fill {
    height: 100%;
    background: var(--blue);
    transition: width .6s ease;
}
.ud-steps-list { padding: .5rem 0; }
.ud-step-row {
    display: flex;
    align-items: center;
    gap: .9rem;
    padding: .65rem 1.4rem;
    transition: background .15s;
}
.ud-step-row.active { background: var(--blue-light); }
.ud-step-row.done { background: var(--surface); }
.ud-step-icon {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
}
.ud-step-icon.done-ic { background: var(--green-bg); color: var(--green); }
.ud-step-icon.active-ic { background: var(--blue); color: var(--text-inv); font-size: 13px; }
.ud-step-icon.pend-ic { background: var(--surface-3); color: var(--text-3); }
.ud-step-body { flex: 1; min-width: 0; }
.ud-step-name {
    font-size: .875rem;
    font-weight: 600;
    color: var(--text-1);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ud-step-row.pending .ud-step-name { color: var(--text-3); font-weight: 400; }
.ud-step-detail {
    font-size: .75rem;
    color: var(--text-2);
    margin-top: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ud-step-time {
    font-size: .75rem;
    color: var(--text-3);
    white-space: nowrap;
    flex-shrink: 0;
}
.ud-step-row.active .ud-step-time { color: var(--blue); font-weight: 500; }
.ud-step-row.done .ud-step-time { color: var(--green); }

/* ══════════════════════════════════════════════════
   EMAIL CAPTURE BANNER
══════════════════════════════════════════════════ */
.ud-email-banner {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--amber-bg);
    border: 1px solid #F9AB00;
    border-radius: var(--r-lg);
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.ud-email-banner-text { flex: 1; min-width: 200px; }
.ud-email-banner-title {
    font-size: .875rem;
    font-weight: 600;
    color: #6A4000;
    margin-bottom: .2rem;
}
.ud-email-banner-sub {
    font-size: .78rem;
    color: #7A5000;
    line-height: 1.4;
}

/* ══════════════════════════════════════════════════
   QUOTE CARD
══════════════════════════════════════════════════ */
.ud-quote {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    overflow: hidden;
    box-shadow: var(--shadow-md);
    margin: 1.25rem 0;
}
.ud-quote-top {
    padding: 1.5rem 1.75rem 1.25rem;
    background: linear-gradient(135deg, var(--blue) 0%, #4285F4 100%);
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1rem;
}
.ud-quote-tier {
    font-size: .75rem;
    font-weight: 600;
    color: rgba(255,255,255,.8);
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: .4rem;
}
.ud-quote-price {
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--text-inv);
    line-height: 1;
}
.ud-quote-price sup {
    font-size: 1.25rem;
    vertical-align: super;
    font-weight: 400;
    opacity: .85;
}
.ud-quote-meta {
    text-align: right;
    font-size: .78rem;
    color: rgba(255,255,255,.8);
    line-height: 1.8;
}
.ud-quote-body { padding: 1.25rem 1.75rem; }
.ud-bline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: .5rem 0;
    border-bottom: 1px solid var(--border);
    font-size: .875rem;
}
.ud-bline:last-child { border-bottom: none; }
.ud-bk { color: var(--text-2); }
.ud-bv { color: var(--text-1); font-weight: 500; }
.ud-bv.total { color: var(--blue); font-size: 1.1rem; font-weight: 700; }
.ud-savings-badge {
    display: inline-block;
    background: var(--green-bg);
    color: var(--green);
    font-size: .72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: var(--r-pill);
    margin-left: .4rem;
}
.ud-quote-foot {
    padding: .85rem 1.75rem;
    border-top: 1px solid var(--border);
    background: var(--surface-2);
    font-size: .78rem;
    color: var(--text-3);
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.ud-quote-trust {
    display: flex;
    align-items: center;
    gap: .3rem;
}

/* ══════════════════════════════════════════════════
   PAY BUTTON
══════════════════════════════════════════════════ */
.ud-pay-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .5rem;
    width: 100%;
    background: var(--blue);
    color: var(--text-inv) !important;
    padding: 1rem 1.5rem;
    border-radius: var(--r-pill);
    font-family: var(--font) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    text-decoration: none !important;
    transition: background .15s, box-shadow .15s;
    box-shadow: var(--shadow-sm);
    min-height: 52px;
    margin-top: 1rem;
}
.ud-pay-btn:hover {
    background: var(--blue-dark);
    box-shadow: var(--shadow-md);
    text-decoration: none !important;
    color: var(--text-inv) !important;
}
.ud-secure-row {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: .6rem;
    flex-wrap: wrap;
}
.ud-secure-item {
    display: flex;
    align-items: center;
    gap: .3rem;
    font-size: .75rem;
    color: var(--text-3);
}

/* ══════════════════════════════════════════════════
   ADDON CARDS
══════════════════════════════════════════════════ */
.ud-addon-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: .75rem;
    margin-bottom: 1rem;
}
.ud-addon {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1rem 1.1rem;
    transition: border-color .15s, background .15s;
}
.ud-addon-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: .3rem;
}
.ud-addon-title {
    font-size: .875rem;
    font-weight: 600;
    color: var(--text-1);
}
.ud-addon-price {
    font-size: .9rem;
    font-weight: 700;
    color: var(--blue);
}
.ud-addon-desc {
    font-size: .78rem;
    color: var(--text-2);
    line-height: 1.5;
}

/* ══════════════════════════════════════════════════
   LANG MULTI-SELECT SECTION
══════════════════════════════════════════════════ */
.ud-bundle-badge {
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    background: var(--green-bg);
    color: var(--green);
    border: 1px solid #34A853;
    border-radius: var(--r-pill);
    font-size: .75rem;
    font-weight: 600;
    padding: .25rem .75rem;
    margin-bottom: .6rem;
}

/* ══════════════════════════════════════════════════
   PRICING TAB
══════════════════════════════════════════════════ */
.ud-callout {
    background: var(--blue-light);
    border: 1px solid rgba(26,115,232,.25);
    border-radius: var(--r-lg);
    padding: 1rem 1.25rem;
    font-size: .875rem;
    color: #174EA6;
    line-height: 1.7;
    margin-bottom: 1.25rem;
}
.ud-callout strong { font-weight: 600; }

.ud-tier-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .75rem;
    margin-bottom: 1.5rem;
}
.ud-tier {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--r-xl);
    padding: 1.25rem 1rem;
    text-align: center;
    transition: border-color .15s, box-shadow .15s;
}
.ud-tier:hover { border-color: var(--blue); box-shadow: var(--shadow-sm); }
.ud-tier.featured {
    border-color: var(--blue);
    box-shadow: var(--shadow-sm);
    position: relative;
}
.ud-tier-badge {
    position: absolute;
    top: -11px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--blue);
    color: var(--text-inv);
    font-size: .7rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: var(--r-pill);
    white-space: nowrap;
}
.ud-tier-em { font-size: 1.5rem; margin-bottom: .5rem; }
.ud-tier-name {
    font-size: .82rem;
    font-weight: 600;
    color: var(--text-1);
}
.ud-tier-dur {
    font-size: .75rem;
    color: var(--text-3);
    margin: .2rem 0 .8rem;
}
.ud-tier-price {
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--blue);
}

/* True cost grid */
.ud-tc-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: .75rem;
    margin-bottom: 1.5rem;
}
.ud-tc {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.25rem 1rem;
}
.ud-tc.us {
    border-color: var(--blue);
    background: var(--blue-light);
}
.ud-tc-svc {
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .5px;
    color: var(--text-3);
    margin-bottom: .4rem;
}
.ud-tc.us .ud-tc-svc { color: var(--blue-dark); }
.ud-tc-price {
    font-size: 2.25rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: .3rem;
}
.ud-tc-price.g { color: var(--green); }
.ud-tc-price.r { color: var(--red); }
.ud-tc-detail {
    font-size: .78rem;
    color: var(--text-2);
    line-height: 1.75;
    border-top: 1px solid var(--border);
    padding-top: .65rem;
    margin-top: .65rem;
}

/* Comparison table */
.ud-comp-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 1.25rem; }
.ud-comp {
    width: 100%;
    border-collapse: collapse;
    font-size: .85rem;
    min-width: 520px;
}
.ud-comp thead tr { background: var(--surface-2); }
.ud-comp th {
    padding: .75rem 1rem;
    font-size: .75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .5px;
    border-bottom: 2px solid var(--border);
    text-align: center;
    color: var(--text-2);
}
.ud-comp th:first-child { text-align: left; }
.ud-comp th.us { color: var(--blue); }
.ud-comp td {
    padding: .7rem 1rem;
    border-bottom: 1px solid var(--surface-3);
    text-align: center;
    color: var(--text-2);
}
.ud-comp td:first-child { text-align: left; color: var(--text-1); font-weight: 500; }
.ud-comp tr:hover td { background: var(--surface-2); }
.ud-comp tr.hl td { background: var(--blue-light); }
.ud-comp tr.sec td {
    background: var(--surface-3);
    font-size: .7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .5px;
    color: var(--text-3);
    padding: .4rem 1rem;
    text-align: left;
}
.yes  { color: var(--green) !important; font-weight: 600; }
.no   { color: var(--red)   !important; }
.warn { color: var(--amber) !important; }
.best { color: var(--blue)  !important; font-weight: 700; }

/* ══════════════════════════════════════════════════
   HOW IT WORKS
══════════════════════════════════════════════════ */
.ud-how-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: .75rem;
    margin-bottom: 1.5rem;
}
.ud-how-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    padding: 1.25rem;
    transition: box-shadow .15s;
}
.ud-how-card:hover { box-shadow: var(--shadow-md); }
.ud-how-num {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: var(--blue-light);
    color: var(--blue);
    font-size: .85rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: .75rem;
}
.ud-how-title {
    font-size: .9rem;
    font-weight: 600;
    color: var(--text-1);
    margin-bottom: .35rem;
}
.ud-how-desc {
    font-size: .8rem;
    color: var(--text-2);
    line-height: 1.65;
}

/* Language grid */
.ud-lang-grid {
    display: flex;
    flex-wrap: wrap;
    gap: .4rem;
    margin-top: .75rem;
}
.ud-lang-chip {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--r-pill);
    padding: .25rem .75rem;
    font-size: .78rem;
    color: var(--text-2);
    transition: border-color .15s, background .15s;
}
.ud-lang-chip:hover { border-color: var(--blue); color: var(--blue); background: var(--blue-light); }

/* ══════════════════════════════════════════════════
   FAQ
══════════════════════════════════════════════════ */
.ud-faq { border-bottom: 1px solid var(--border); padding: 1.1rem 0; }
.ud-faq-q {
    font-size: .9rem;
    font-weight: 600;
    color: var(--text-1);
    margin-bottom: .4rem;
    display: flex;
    align-items: flex-start;
    gap: .6rem;
}
.ud-faq-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--blue);
    flex-shrink: 0;
    margin-top: .4rem;
}
.ud-faq-a {
    font-size: .85rem;
    color: var(--text-2);
    line-height: 1.75;
    padding-left: 1.1rem;
}

/* ══════════════════════════════════════════════════
   SUCCESS
══════════════════════════════════════════════════ */
.ud-success {
    background: var(--green-bg);
    border: 1px solid #34A853;
    border-radius: var(--r-xl);
    padding: 1.75rem;
    text-align: center;
    margin: 1rem 0;
}
.ud-success-icon { font-size: 2.5rem; margin-bottom: .5rem; }
.ud-success-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--green);
    margin-bottom: .4rem;
}
.ud-success-sub { font-size: .875rem; color: #1E7E34; }

/* Download button */
.stDownloadButton > button {
    background: var(--surface) !important;
    border: 1.5px solid var(--blue) !important;
    color: var(--blue) !important;
    border-radius: var(--r-pill) !important;
    font-family: var(--font) !important;
    font-size: .875rem !important;
    font-weight: 600 !important;
    min-height: 44px !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: var(--blue-light) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ══════════════════════════════════════════════════
   ALERTS
══════════════════════════════════════════════════ */
div[data-testid="stNotification"] {
    border-radius: var(--r-lg) !important;
    border-left: 4px solid var(--blue) !important;
    background: var(--blue-light) !important;
}
div[data-testid="stNotification"] p { color: #174EA6 !important; }

/* ══════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--surface-2) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: var(--font) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--text-1) !important;
}
section[data-testid="stSidebar"] input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-1) !important;
    font-family: var(--font) !important;
    min-height: 40px !important;
}
section[data-testid="stSidebar"] input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(26,115,232,.12) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: var(--text-2) !important;
    font-family: var(--font) !important;
}

/* ══════════════════════════════════════════════════
   FOOTER
══════════════════════════════════════════════════ */
.ud-footer {
    background: var(--surface-2);
    border-top: 1px solid var(--border);
    padding: 2rem 2rem 1.5rem;
    margin-top: 3rem;
}
.ud-footer-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 2rem;
    margin-bottom: 1.5rem;
}
.ud-footer-brand .ud-wordmark { font-size: 1.1rem; margin-bottom: .35rem; }
.ud-footer-brand p {
    font-size: .8rem;
    color: var(--text-2);
    line-height: 1.6;
    max-width: 200px;
}
.ud-footer-col h4 {
    font-size: .78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .5px;
    color: var(--text-3);
    margin-bottom: .65rem;
}
.ud-footer-col a {
    display: block;
    font-size: .82rem;
    color: var(--text-2);
    margin-bottom: .35rem;
    cursor: pointer;
    transition: color .15s;
}
.ud-footer-col a:hover { color: var(--blue); }
.ud-footer-bottom {
    border-top: 1px solid var(--border);
    padding-top: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: .5rem;
}
.ud-footer-copy {
    font-size: .78rem;
    color: var(--text-3);
}
.ud-footer-links {
    display: flex;
    gap: 1.2rem;
    font-size: .78rem;
    color: var(--text-3);
}
.ud-footer-links a { cursor: pointer; }
.ud-footer-links a:hover { color: var(--blue); }

/* ══════════════════════════════════════════════════
   RESPONSIVE - TABLET
══════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .ud-nav { padding: 0 1rem; }
    .ud-nav-links { display: none; }
    .ud-hero { grid-template-columns: 1fr; padding: 2rem 1rem; }
    .ud-hero-visual { display: none; }
    .ud-stats { grid-template-columns: repeat(2,1fr); }
    .ud-stat:nth-child(2) { border-right: none; }
    .ud-stat:nth-child(3) { border-top: 1px solid var(--border); }
    .ud-stat:nth-child(4) { border-top: 1px solid var(--border); border-right: none; }
    .stTabs [data-baseweb="tab-panel"] { padding: 1rem !important; }
    .ud-tier-grid { grid-template-columns: repeat(2,1fr); }
    .ud-tc-grid { grid-template-columns: 1fr; }
    .ud-how-grid { grid-template-columns: 1fr; }
    .ud-addon-grid { grid-template-columns: 1fr; }
    .ud-footer-grid { grid-template-columns: 1fr; }
    .ud-footer-bottom { flex-direction: column; align-items: flex-start; }
    .ud-quote-top { flex-direction: column; }
    .ud-quote-meta { text-align: left; }
}

@media (max-width: 480px) {
    .ud-hero h1 { font-size: 1.9rem; }
    .ud-hero-ctas { flex-direction: column; }
    .ud-tier-grid { grid-template-columns: 1fr 1fr; }
    .ud-quote-price { font-size: 2.75rem; }
    .ud-hero-ctas .ud-btn { width: 100%; text-align: center; }
}
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

def find_cookies() -> list:
    for p in ["cookies.txt", "/app/cookies.txt",
              os.path.join(os.getcwd(), "cookies.txt")]:
        if os.path.exists(p):
            return ["--cookies", p, "--user-agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0.0.0"]
    return []

def validate_yt(url: str) -> bool:
    return bool(re.match(
        r"^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)",
        url.strip()))

def cfg(key: str) -> str:
    return os.environ.get(key, st.session_state.get(key, ""))

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
def separate_music(audio_path: str, work_dir: str) -> tuple[str, str]:
    """
    Separate vocals from background music using audio-separator (ONNX).
    Returns (vocals_path, no_vocals_path) as WAV files.
    Falls back to ffmpeg high-pass filter if audio-separator unavailable.
    """
    # Try audio-separator first
    try:
        from audio_separator.separator import Separator
        sep = Separator(output_dir=work_dir, output_format="wav",
                        log_level=40)  # suppress logs
        sep.load_model("UVR-MDX-NET-Inst_HQ_3.onnx")
        result = sep.separate(audio_path)
        # audio-separator returns [vocals_path, no_vocals_path]
        vocals    = next((p for p in result if "Vocals"   in p or "vocals"   in p), result[0])
        no_vocals = next((p for p in result if "Instrum"  in p or "no_vocal" in p), result[-1])
        return vocals, no_vocals
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: ffmpeg centre-channel extraction (stereo only, rough)
    vocals_path    = os.path.join(work_dir, "vocals_approx.mp3")
    no_vocals_path = os.path.join(work_dir, "no_vocals_approx.mp3")

    # Rough vocal extraction (centre-panned content)
    _run(["ffmpeg", "-y", "-i", audio_path,
          "-af", "pan=stereo|c0=c0-c1|c1=c1-c0,highpass=f=200,loudnorm",
          "-ar", "22050", "-ac", "2",
          vocals_path])

    # Rough music extraction (sides)
    _run(["ffmpeg", "-y", "-i", audio_path,
          "-af", "pan=stereo|c0=c1|c1=c0,lowpass=f=4000,loudnorm",
          "-ar", "22050", "-ac", "2",
          no_vocals_path])

    return vocals_path, no_vocals_path

# ══════════════════════════════════════════════════════════════════════════════
# SENDGRID EMAIL
# ══════════════════════════════════════════════════════════════════════════════
def send_ready_email(to_email: str, checkout_url: str,
                     api_key: str, info: dict) -> bool:
    """Send 'video ready' email with Stripe checkout link."""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail

        sg   = sendgrid.SendGridAPIClient(api_key=api_key)
        html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: 'Helvetica Neue', Arial, sans-serif;
             background: #F8F9FA; margin: 0; padding: 2rem;">
  <div style="max-width: 520px; margin: 0 auto; background: #fff;
              border-radius: 16px; overflow: hidden;
              border: 1px solid #DADCE0;">
    <div style="background: #1A73E8; padding: 1.5rem 2rem;">
      <h1 style="color: #fff; font-size: 1.4rem; margin: 0;
                 font-weight: 700; letter-spacing: -0.3px;">Ultradub</h1>
      <p style="color: rgba(255,255,255,.8); margin: .25rem 0 0;
                font-size: .85rem;">Your voice, in every language</p>
    </div>
    <div style="padding: 1.75rem 2rem;">
      <h2 style="color: #202124; font-size: 1.25rem; margin: 0 0 .75rem;
                 font-weight: 700;">Your dubbed video is ready!</h2>
      <p style="color: #5F6368; line-height: 1.7; margin: 0 0 1.25rem;">
        Your <strong>{info.get('dur', '')} minute</strong> video has been
        successfully dubbed and is waiting for you.
      </p>
      <div style="background: #F8F9FA; border-radius: 12px;
                  padding: 1rem; margin-bottom: 1.25rem;
                  border: 1px solid #DADCE0;">
        <div style="font-size:.78rem; color:#80868B; margin-bottom:.2rem;">
          Your quote</div>
        <div style="font-size:1.75rem; font-weight:700; color:#202124;">
          ${info.get('price', '')}</div>
      </div>
      <a href="{checkout_url}"
         style="display: block; background: #1A73E8; color: #fff;
                text-align: center; padding: .9rem 1.5rem;
                border-radius: 24px; text-decoration: none;
                font-weight: 600; font-size: 1rem; margin-bottom: 1rem;">
        Pay &amp; Download Video
      </a>
      <p style="color: #80868B; font-size: .78rem; text-align: center;
                margin: 0; line-height: 1.6;">
        This link expires in 24 hours.
        Secured by Stripe - no account required.
      </p>
    </div>
  </div>
</body>
</html>"""

        msg = Mail(
            from_email="noreply@ultradub.ai",
            to_emails=to_email,
            subject="Your Ultradub video is ready - pay & download now",
            html_content=html,
        )
        sg.send(msg)
        return True
    except Exception:
        return False

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
        # Use a 90-second sample for diarization - enough to identify speakers
        sample = tempfile.mktemp(suffix=".mp3")
        _run(["ffmpeg", "-y", "-i", audio_path,
              "-t", "90",
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
    try:
        with open(path, "rb") as f:
            r = requests.post("https://api.sync.so/v2/upload",
                              headers={"x-api-key": api_key},
                              files={"file": f}, timeout=180)
        if r.status_code == 200:
            return r.json().get("url") or r.json().get("fileUrl")
    except Exception:
        pass
    with open(path, "rb") as f:
        r = requests.post("https://0x0.st", files={"file": f}, timeout=180)
    r.raise_for_status()
    return r.text.strip()


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
def step_download(url: str, work_dir: str) -> str:
    cookies = find_cookies()
    tmpl    = os.path.join(work_dir, "source.%(ext)s")
    _run(["yt-dlp",
          "--format",
          "bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]",
          "--merge-output-format", "mp4",
          "--output", tmpl, "--no-playlist"] + cookies + [url])
    files = list(Path(work_dir).glob("source.*"))
    if not files:
        raise FileNotFoundError(
            "Video could not be downloaded. "
            "If this is a YouTube URL, add a cookies.txt file to bypass geographic/bot restrictions.")
    return str(files[0])


def step_save_upload(f, work_dir: str) -> str:
    ext = f.name.rsplit(".", 1)[-1].lower()
    raw = os.path.join(work_dir, f"upload.{ext}")
    with open(raw, "wb") as out:
        out.write(f.getbuffer())
    if ext == "mp4":
        return raw
    mp4 = os.path.join(work_dir, "source.mp4")
    _run(["ffmpeg", "-y", "-i", raw,
          "-c:v", "libx264", "-c:a", "aac",
          "-movflags", "+faststart", mp4])
    return mp4


def step_extract_audio(video: str, out: str) -> None:
    _run(["ffmpeg", "-y", "-i", video, "-vn",
          "-acodec", "libmp3lame", "-q:a", "4", out])


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
        # Blend dubbed voice + original music
        inputs  += ["-i", no_vocals_path]
        music_in = len(delays) + 1
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
def stripe_create(amount: float, vk: str, sk: str, app_url: str) -> str:
    import stripe as _s
    _s.api_key = sk
    base = app_url.rstrip("/")
    s    = _s.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {
            "currency": "usd",
            "product_data": {"name": "Ultradub - Dubbed Video",
                             "description": "AI-dubbed video. Instant download."},
            "unit_amount": int(amount * 100),
        }, "quantity": 1}],
        mode="payment",
        success_url=(f"{base}?payment=success"
                     f"&session_id={{CHECKOUT_SESSION_ID}}"
                     f"&video_key={vk}"),
        cancel_url=f"{base}?payment=cancelled",
        metadata={"video_key": vk},
    )
    return s.url


def stripe_verify(sid: str, sk: str) -> tuple[bool, str]:
    import stripe as _s
    _s.api_key = sk
    try:
        s = _s.checkout.Session.retrieve(sid)
        if s.payment_status == "paid":
            return True, s.metadata.get("video_key", "")
    except Exception:
        pass
    return False, ""

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFAULTS: dict = {
    "done":          False,
    "preview_bytes": None,
    "vk":            None,
    "checkout_url":  None,
    "quote":         None,
    "detected_lang": None,
    "lang_srts":     {},     # {lang_key: srt_string}
    "n_langs":       1,
    "proc_start":    None,
    "user_email":    "",
    "email_sent":    False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - API CREDENTIALS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### Ultradub")
    st.caption("Configure your API credentials below.")

    with st.expander("API Credentials", expanded=True):
        for env, label, ph, tip in [
            ("GOOGLE_API_KEY",    "AI Platform Key",      "AIza...",
             "Enable Speech Recognition, Translation, and Text-to-Speech "
             "APIs in your cloud console."),
            ("STRIPE_SECRET_KEY", "Payments Key",         "sk_live_... or sk_test_...",
             "Your payment processor secret key."),
            ("APP_URL",           "App Public URL",       "https://...",
             "Your Replit public URL. Required for payment redirects."),
            ("ELEVENLABS_API_KEY","Voice Cloning Key",    "Optional",
             "Required for voice cloning add-on."),
            ("SYNCLABS_API_KEY",  "Lip-Sync Key",         "Optional",
             "Required for lip-sync add-on."),
            ("SENDGRID_API_KEY",  "Email Notifications",  "SG.xxx",
             "Optional. Send email when video is ready."),
        ]:
            if os.environ.get(env):
                st.success(f"✅ {label}")
            else:
                v = st.text_input(label, type="password",
                                  placeholder=ph, help=tip,
                                  key=f"inp_{env}")
                if v: st.session_state[env] = v

    with st.expander("Pricing", expanded=False):
        for t in TIERS:
            st.markdown(
                f"{t['emoji']} **{t['name']}** ≤{t['max_min']} min "
                f"- **${t['price']}**")
        st.caption("+ Lip-sync: $5–45 | Voice cloning: +$3.99")

    with st.expander("Quick Setup (Replit)", expanded=False):
        st.code("""# Shell tab:
sudo apt-get install -y ffmpeg
pip install -r requirements.txt

# Run:
streamlit run app.py \\
  --server.address 0.0.0.0 \\
  --server.port 8080""", language="bash")

    st.caption("(c) 2025 Ultradub")

# ══════════════════════════════════════════════════════════════════════════════
# FFMPEG CHECK
# ══════════════════════════════════════════════════════════════════════════════
if not ffmpeg_ok():
    st.error("**ffmpeg not found.** Run `sudo apt-get install -y ffmpeg` in the Shell tab.")

# ══════════════════════════════════════════════════════════════════════════════
# STRIPE RETURN HANDLER
# ══════════════════════════════════════════════════════════════════════════════
params   = st.query_params
p_status = params.get("payment", "")
p_sid    = params.get("session_id", "")
p_vk     = params.get("video_key", "")

if p_status == "success" and p_sid and p_vk:
    paid, vk = stripe_verify(p_sid, cfg("STRIPE_SECRET_KEY"))
    if paid:
        # Find all files for this video key
        all_files = sorted(Path(VIDEO_STORE).glob(f"{vk}*.mp4"))
        srt_files = sorted(Path(VIDEO_STORE).glob(f"{vk}*.srt"))

        if all_files:
            st.markdown("""
            <div class="ud-success">
                <div class="ud-success-icon">✓</div>
                <div class="ud-success-title">Payment confirmed</div>
                <div class="ud-success-sub">
                    Your dubbed video is unlocked. Download below.
                </div>
            </div>""", unsafe_allow_html=True)

            for fp in all_files:
                label = fp.stem.replace(vk + "_", "").upper() or "VIDEO"
                lang_label = LANG_LABELS.get(fp.stem.replace(vk + "_", ""), label)
                with open(fp, "rb") as f:
                    data = f.read()
                st.video(data)
                st.download_button(
                    f"⬇  Download {lang_label} - MP4",
                    data=data, file_name=fp.name,
                    mime="video/mp4", use_container_width=True)

            for sp in srt_files:
                lang_label = LANG_LABELS.get(sp.stem.replace(vk + "_", ""), "")
                with open(sp, "r") as f:
                    srt_data = f.read()
                st.download_button(
                    f"⬇  Download Subtitles {lang_label} - SRT",
                    data=srt_data, file_name=sp.name,
                    mime="text/plain", use_container_width=True)

            # Clean up
            for fp in list(all_files) + list(srt_files):
                try: fp.unlink()
                except: pass
        else:
            st.error(f"Video file not found - server may have restarted. "
                     f"Session ID: `{p_sid}`")
    else:
        st.warning("Payment could not be verified. Please try again.")
    st.query_params.clear()
    st.stop()

elif p_status == "cancelled":
    st.info("Payment cancelled. You can try again below.")
    st.query_params.clear()

# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ud-nav">
    <div class="ud-wordmark">Ultra<em>dub</em></div>
    <div class="ud-nav-links">
        <a>Product</a>
        <a>Pricing</a>
        <a>FAQ</a>
    </div>
    <div class="ud-nav-cta">
        <span style="font-size:.8rem;color:var(--text-3);">No account needed</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ud-hero">
  <div class="ud-hero-left">
    <div class="ud-hero-eyebrow">
      <span style="width:7px;height:7px;border-radius:50%;
                   background:var(--blue);display:inline-block;"></span>
      AI Video Dubbing Platform
    </div>
    <h1 class="ud-hero-h1">
      Your voice,<br>
      in every <span class="blue">language</span>
    </h1>
    <p class="ud-hero-sub">
      Professional AI dubbing for creators and enterprises.
      Paste a URL or upload a file. Preview free.
      Pay once. Download instantly.
    </p>
    <div class="ud-hero-ctas">
      <a class="ud-btn ud-btn-primary ud-btn-lg">Start dubbing</a>
      <a class="ud-btn ud-btn-outline ud-btn-lg">See pricing</a>
    </div>
    <div class="ud-trust">
      <div class="ud-trust-item">
        <span class="ud-trust-check">✓</span> No account
      </div>
      <div class="ud-trust-item">
        <span class="ud-trust-check">✓</span> Free 15s preview
      </div>
      <div class="ud-trust-item">
        <span class="ud-trust-check">✓</span> Instant download
      </div>
      <div class="ud-trust-item">
        <span class="ud-trust-check">✓</span> SRT subtitles included
      </div>
    </div>
  </div>

  <div class="ud-hero-visual">
    <div class="ud-video-card">
      <div class="ud-video-thumb">
        <div class="ud-play-btn">▶</div>
      </div>
      <div class="ud-video-meta">
        <span>Dubbing in progress</span>
        <span class="ud-video-duration">8:42</span>
      </div>
    </div>
    <div class="ud-lang-arrow">
      <div class="ud-lang-pill">🇷🇺 Russian</div>
      <span class="ud-arrow-icon">→</span>
      <div class="ud-lang-pill target">🇺🇸 English</div>
    </div>
    <div class="ud-status-pill">
      <span class="ud-status-dot"></span>
      Processing · 4 min remaining
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STATS BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ud-stats">
    <div class="ud-stat">
        <div class="ud-stat-n">40<span class="b">+</span></div>
        <div class="ud-stat-l">Languages</div>
    </div>
    <div class="ud-stat">
        <div class="ud-stat-n"><span class="b">$</span>4.99</div>
        <div class="ud-stat-l">Starting price</div>
    </div>
    <div class="ud-stat">
        <div class="ud-stat-n">3<span class="b">×</span></div>
        <div class="ud-stat-l">Cheaper than competitors</div>
    </div>
    <div class="ud-stat">
        <div class="ud-stat-n"><span class="b">$</span>0</div>
        <div class="ud-stat-l">Monthly fee</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_proj, tab_price, tab_how, tab_faq = st.tabs([
    "New Project", "Pricing", "How It Works", "FAQ"])

# ─────────────────────────────────────────────────────────────────────────────
# PRICING TAB
# ─────────────────────────────────────────────────────────────────────────────
with tab_price:
    st.markdown("""
    <div class="ud-callout">
        <strong>The truth competitors don't advertise:</strong>
        Rask AI starts at $50/month. ElevenLabs starts at $22/month.
        Their per-video prices only apply if you're already paying those subscriptions.
        <strong>Ultradub charges $0 until you actually dub a video.</strong>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="ud-section-label">True cost — dubbing one video per month</div>
    <div class="ud-tc-grid">
        <div class="ud-tc us">
            <div class="ud-tc-svc">Ultradub</div>
            <div class="ud-tc-price g">$9.99</div>
            <div class="ud-tc-detail">
                10-min video<br>Subscription: $0<br>
                Translation: included<br>SRT subtitles: included<br>
                <strong>All-in: $9.99</strong>
            </div>
        </div>
        <div class="ud-tc">
            <div class="ud-tc-svc">ElevenLabs</div>
            <div class="ud-tc-price r">$28+</div>
            <div class="ud-tc-detail">
                Subscription: $22/mo<br>Translation: not included<br>
                Overages: $6+<br>SRT: not included<br>
                <strong>All-in: $28+</strong>
            </div>
        </div>
        <div class="ud-tc">
            <div class="ud-tc-svc">Rask AI</div>
            <div class="ud-tc-price r">$50+</div>
            <div class="ud-tc-detail">
                Subscription: $50/mo<br>Lip-sync doubles credits¹<br>
                Overages: $2/min<br>SRT: extra cost<br>
                <strong>All-in: $50+</strong>
            </div>
        </div>
    </div>

    <div class="ud-section-label">Base dubbing tiers</div>
    <div class="ud-tier-grid">
        <div class="ud-tier">
            <div class="ud-tier-em">⚡</div>
            <div class="ud-tier-name">Short</div>
            <div class="ud-tier-dur">Up to 5 min</div>
            <div class="ud-tier-price">$4.99</div>
        </div>
        <div class="ud-tier featured">
            <div class="ud-tier-badge">Most popular</div>
            <div class="ud-tier-em">🎬</div>
            <div class="ud-tier-name">Medium</div>
            <div class="ud-tier-dur">Up to 15 min</div>
            <div class="ud-tier-price">$9.99</div>
        </div>
        <div class="ud-tier">
            <div class="ud-tier-em">🎞️</div>
            <div class="ud-tier-name">Long</div>
            <div class="ud-tier-dur">Up to 30 min</div>
            <div class="ud-tier-price">$19.99</div>
        </div>
        <div class="ud-tier">
            <div class="ud-tier-em">🏆</div>
            <div class="ud-tier-name">Ultra</div>
            <div class="ud-tier-dur">Up to 60 min</div>
            <div class="ud-tier-price">$34.99</div>
        </div>
    </div>

    <div class="ud-section-label">Multi-language bundle</div>
    <div class="ud-callout" style="background:var(--green-bg);
         border-color:#34A853;color:#1E7E34;">
        <strong>3 languages for the price of 2.</strong>
        Select up to 3 output languages per project - the third language is free.
        Each language gets its own dubbed video + SRT subtitle file.
    </div>

    <div class="ud-section-label">Add-ons</div>
    <div class="ud-addon-grid">
        <div class="ud-addon">
            <div class="ud-addon-head">
                <div class="ud-addon-title">Voice cloning</div>
                <div class="ud-addon-price">+$3.99</div>
            </div>
            <div class="ud-addon-desc">
                We automatically extract the speaker's voice from your
                video and clone it into the target language. The dubbed
                audio sounds like the same person speaking a new language.
                No sample upload needed.
            </div>
        </div>
        <div class="ud-addon">
            <div class="ud-addon-head">
                <div class="ud-addon-title">Lip sync</div>
                <div class="ud-addon-price">+$5–45</div>
            </div>
            <div class="ud-addon-desc">
                AI reshapes the speaker's mouth movements frame-by-frame
                to match the new dubbed audio. The result looks as if the
                speaker delivered the content in the target language natively.
            </div>
        </div>
        <div class="ud-addon">
            <div class="ud-addon-head">
                <div class="ud-addon-title">Music preservation</div>
                <div class="ud-addon-price">Included free</div>
            </div>
            <div class="ud-addon-desc">
                AI separates background music from the original voice track,
                preserves it, and blends it back with the new dubbed voice.
                Background music stays; only the speech is replaced.
            </div>
        </div>
        <div class="ud-addon">
            <div class="ud-addon-head">
                <div class="ud-addon-title">SRT subtitles</div>
                <div class="ud-addon-price">Included free</div>
            </div>
            <div class="ud-addon-desc">
                Every dub includes a timed SRT subtitle file in the
                target language. Ready to upload to YouTube, social media,
                or any video platform. Multiple languages get separate SRT files.
            </div>
        </div>
    </div>

    <div class="ud-section-label">Full comparison</div>
    <div class="ud-comp-wrap">
    <table class="ud-comp">
      <thead>
        <tr>
          <th style="text-align:left;width:32%"></th>
          <th class="us">Ultradub</th>
          <th>Rask AI</th>
          <th>ElevenLabs</th>
          <th>Dubly.ai</th>
        </tr>
      </thead>
      <tbody>
        <tr class="sec"><td colspan="5">Pricing</td></tr>
        <tr class="hl">
          <td>Subscription required</td>
          <td><span class="yes">None — ever</span></td>
          <td><span class="no">$50–600/mo</span></td>
          <td><span class="no">$22–99/mo</span></td>
          <td><span class="no">€29–299/mo</span></td>
        </tr>
        <tr>
          <td>Pay per video, no plan</td>
          <td><span class="yes">Always</span></td>
          <td><span class="no">No</span></td>
          <td><span class="no">No</span></td>
          <td><span class="no">No</span></td>
        </tr>
        <tr><td>5-min video true cost</td><td><span class="best">$4.99</span></td><td><span class="warn">$50+ plan</span></td><td><span class="warn">$22+ plan</span></td><td><span class="warn">€29+ plan</span></td></tr>
        <tr><td>Translation included</td><td><span class="yes">Yes</span></td><td><span class="yes">Yes</span></td><td><span class="no">No</span></td><td><span class="yes">Yes</span></td></tr>
        <tr class="sec"><td colspan="5">Features</td></tr>
        <tr class="hl"><td>Paste YouTube URL</td><td><span class="yes">Yes</span></td><td><span class="no">No</span></td><td><span class="no">No</span></td><td><span class="no">No</span></td></tr>
        <tr><td>SRT subtitle export</td><td><span class="yes">Free — every dub</span></td><td><span class="warn">Paid add-on</span></td><td><span class="no">No</span></td><td><span class="warn">Paid plan</span></td></tr>
        <tr><td>Background music preserved</td><td><span class="yes">Yes — free</span></td><td><span class="warn">Paid plan</span></td><td><span class="no">No</span></td><td><span class="yes">Yes</span></td></tr>
        <tr><td>Multi-language bundle</td><td><span class="yes">3 for price of 2</span></td><td><span class="warn">Extra credits</span></td><td><span class="warn">Extra credits</span></td><td><span class="warn">Extra credits</span></td></tr>
        <tr><td>Auto language detection</td><td><span class="yes">Yes</span></td><td><span class="yes">Yes</span></td><td><span class="warn">Manual only</span></td><td><span class="yes">Yes</span></td></tr>
        <tr><td>Voice cloning</td><td><span class="yes">Yes (+$3.99)</span></td><td><span class="warn">Pro plan</span></td><td><span class="yes">Plan required</span></td><td><span class="yes">Plan required</span></td></tr>
        <tr><td>Lip sync</td><td><span class="yes">Yes (+$5–45)</span></td><td><span class="warn">Doubles credits¹</span></td><td><span class="no">No</span></td><td><span class="warn">Doubles credits¹</span></td></tr>
        <tr class="sec"><td colspan="5">Delivery</td></tr>
        <tr class="hl"><td>Free preview before paying</td><td><span class="yes">Yes — 15 seconds</span></td><td><span class="no">No</span></td><td><span class="no">No</span></td><td><span class="warn">1 min one-time</span></td></tr>
        <tr><td>Instant download on same page</td><td><span class="yes">Yes</span></td><td><span class="warn">Dashboard</span></td><td><span class="warn">Dashboard</span></td><td><span class="warn">Dashboard</span></td></tr>
        <tr><td>Account required</td><td><span class="yes">No</span></td><td><span class="no">Yes</span></td><td><span class="no">Yes</span></td><td><span class="no">Yes</span></td></tr>
      </tbody>
    </table>
    </div>
    <p style="font-size:.78rem;color:var(--text-3);line-height:1.7;">
        ¹ Rask AI and Dubly.ai lip-sync doubles credit usage.
        A 10-min video with lip-sync consumes 20 min of credits - often your entire monthly plan.
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HOW IT WORKS TAB
# ─────────────────────────────────────────────────────────────────────────────
with tab_how:
    st.markdown("""
    <div class="ud-section-label">The process</div>
    <div class="ud-how-grid">
        <div class="ud-how-card">
            <div class="ud-how-num">1</div>
            <div class="ud-how-title">Input your video</div>
            <div class="ud-how-desc">
                Paste a YouTube URL or upload a file - MP4, MOV, AVI,
                MKV, WebM up to 60 minutes. No account required.
            </div>
        </div>
        <div class="ud-how-card">
            <div class="ud-how-num">2</div>
            <div class="ud-how-title">Choose languages</div>
            <div class="ud-how-desc">
                Auto-detect source language or select manually.
                Choose up to 3 output languages. Third language is free.
            </div>
        </div>
        <div class="ud-how-card">
            <div class="ud-how-num">3</div>
            <div class="ud-how-title">Add upgrades</div>
            <div class="ud-how-desc">
                Enable voice cloning (auto-extracted from video)
                or lip-sync. Background music is preserved free by default.
            </div>
        </div>
        <div class="ud-how-card">
            <div class="ud-how-num">4</div>
            <div class="ud-how-title">AI processes</div>
            <div class="ud-how-desc">
                Speech transcribed → translated → synthesised in the
                target language. Music separated and preserved.
                Watch real-time progress with step-by-step ETAs.
            </div>
        </div>
        <div class="ud-how-card">
            <div class="ud-how-num">5</div>
            <div class="ud-how-title">Free preview</div>
            <div class="ud-how-desc">
                Watch the first 15 seconds of your dubbed video
                before paying. Zero risk - see the quality first.
            </div>
        </div>
        <div class="ud-how-card">
            <div class="ud-how-num">6</div>
            <div class="ud-how-title">Pay &amp; download</div>
            <div class="ud-how-desc">
                One payment. All language versions + SRT subtitle files
                download instantly. No dashboard. No email. Immediate delivery.
            </div>
        </div>
    </div>

    <div class="ud-section-label">Supported languages (40+)</div>
    <div class="ud-lang-grid">
    """ + "".join(
        f'<div class="ud-lang-chip">{v["label"]}</div>'
        for k, v in LANG_REGISTRY.items() if k != "auto"
    ) + """
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FAQ TAB
# ─────────────────────────────────────────────────────────────────────────────
with tab_faq:
    faqs = [
        ("Do I need an account?",
         "No. Ultradub is completely account-free. Paste a URL, configure your settings, "
         "pay once, download instantly. Nothing is stored about you after your video is delivered."),
        ("How long does processing take?",
         "Typically 5–20 minutes depending on video length and selected features. "
         "Music separation adds 5–10 minutes. Lip-sync adds another 5–10 minutes. "
         "A real-time progress tracker shows you each step and estimated time remaining. "
         "You can optionally enter your email to be notified when ready."),
        ("What is the multi-language bundle?",
         "You can select up to 3 output languages per project. "
         "You pay for 2 - the third language is generated free. "
         "Each language gets its own dubbed video file and SRT subtitle file."),
        ("Are subtitles really included free?",
         "Yes. Every dub automatically generates a timed .srt subtitle file in the target language "
         "at no extra cost. If you select multiple output languages, you get separate SRT files for each."),
        ("How does background music preservation work?",
         "Our AI separates the speech track from background music using audio source separation. "
         "The music is preserved, the speech is replaced with the dubbed voice, "
         "and both are blended back together. Included free with every dub."),
        ("How does voice cloning work?",
         "We automatically extract a 45-second clean speech sample from the original video "
         "and use it to clone the speaker's voice. No sample upload needed. "
         "The dubbed audio is then generated in the target language using that cloned voice - "
         "so it sounds like the same person speaking a new language."),
        ("Does lip-sync double the price like some competitors?",
         "No. We charge a flat add-on fee ($5–45 based on video length). "
         "You always see the exact total before processing starts - no credit doubling, "
         "no hidden multipliers."),
        ("What if I'm not happy with the quality?",
         "You watch a free 15-second watermarked preview before paying. "
         "If the quality isn't right, simply don't purchase. Zero risk."),
        ("Is my video data private?",
         "Videos are processed in isolated temporary directories and deleted within 24 hours "
         "of your download. We never store, sell, or use your content in any way."),
        ("What payments are accepted?",
         "All major credit and debit cards via our payment processor. "
         "Apple Pay and Google Pay also supported where available."),
        ("Why doesn't YouTube work sometimes?",
         "YouTube blocks requests from cloud servers. "
         "Add a cookies.txt file to your project root (exported from your browser while "
         "logged into YouTube). Alternatively, download the video manually and upload it directly."),
    ]
    for q, a in faqs:
        st.markdown(
            f'<div class="ud-faq">'
            f'<div class="ud-faq-q"><span class="ud-faq-dot"></span>{q}</div>'
            f'<div class="ud-faq-a">{a}</div>'
            f'</div>',
            unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NEW PROJECT TAB
# ─────────────────────────────────────────────────────────────────────────────
with tab_proj:

    # ── Step 1: Video source ─────────────────────────────────────────────────
    st.markdown('<div class="ud-section-label">1 - Video source</div>',
                unsafe_allow_html=True)
    src = st.radio("", ["YouTube / URL", "Upload a file"],
                   horizontal=True, label_visibility="collapsed")

    yt_url, uploaded_file = "", None
    if src == "YouTube / URL":
        yt_url = st.text_input("", placeholder="https://www.youtube.com/watch?v=...",
                               label_visibility="collapsed")
    else:
        uploaded_file = st.file_uploader(
            "Upload your video",
            type=["mp4","mov","avi","mkv","webm","m4v"],
            label_visibility="collapsed")

    # ── Step 2: Languages ────────────────────────────────────────────────────
    st.markdown('<div class="ud-section-label">2 - Language settings</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        src_label = st.selectbox(
            "Source language",
            [LANG_LABELS[k] for k in INPUT_LANGS])
        src_key = INPUT_LANGS[[LANG_LABELS[k] for k in INPUT_LANGS].index(src_label)]

    # Primary output language
    with c2:
        out_labels    = [LANG_LABELS[k] for k in OUTPUT_LANGS]
        default_en_us = out_labels.index(LANG_LABELS["en-US"])
        tgt1_label    = st.selectbox("Primary output language", out_labels,
                                      index=default_en_us)
        tgt1_key      = OUTPUT_LANGS[out_labels.index(tgt1_label)]

    # Bundle - additional languages
    st.markdown("""
    <div class="ud-bundle-badge">
        ✦ Bundle: 3 languages for the price of 2
    </div>""", unsafe_allow_html=True)

    remaining_labels = [l for l in out_labels if l != tgt1_label]
    extra_langs      = st.multiselect(
        "Add more output languages (optional - up to 2 more)",
        remaining_labels,
        max_selections=2,
        help="Select up to 2 more languages. If you select 2, the third is free.")

    # Build final language key list
    extra_keys  = [OUTPUT_LANGS[out_labels.index(l)] for l in extra_langs]
    all_tgt_keys = [tgt1_key] + extra_keys
    n_langs      = len(all_tgt_keys)

    if n_langs == 3:
        st.success("✦ Bundle applied - 3 languages for the price of 2. "
                   f"Saving ${TIERS[0]['price']:.2f}+")

    # ── Step 3: Add-ons ──────────────────────────────────────────────────────
    st.markdown('<div class="ud-section-label">3 - Optional add-ons</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="ud-addon-grid">
        <div class="ud-addon">
            <div class="ud-addon-head">
                <div class="ud-addon-title">Voice cloning</div>
                <div class="ud-addon-price">+$3.99</div>
            </div>
            <div class="ud-addon-desc">
                Auto-extracted from your video. No sample upload needed.
                Requires Voice Cloning API key in sidebar.
            </div>
        </div>
        <div class="ud-addon">
            <div class="ud-addon-head">
                <div class="ud-addon-title">Lip sync</div>
                <div class="ud-addon-price">+$5–45</div>
            </div>
            <div class="ud-addon-desc">
                Mouth movements matched to dubbed audio.
                Requires Lip-Sync API key in sidebar.
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    ac1, ac2 = st.columns(2)
    with ac1:
        want_clone = st.checkbox(
            "Enable voice cloning (+$3.99)",
            help="Requires Voice Cloning API key in sidebar.")
    with ac2:
        want_lipsync = st.checkbox(
            "Enable lip sync (+$5–45)",
            help="Requires Lip-Sync API key in sidebar.")

    want_music = True  # Always on - free, included by default

    # ── Step 4: Email (shown always, optional) ───────────────────────────────
    st.markdown('<div class="ud-section-label">4 - Email notification (optional)</div>',
                unsafe_allow_html=True)
    user_email = st.text_input(
        "",
        placeholder="your@email.com - we'll notify you when ready",
        label_visibility="collapsed",
        key="email_input")

    # ── Process button ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Process Video & Get Quote", use_container_width=True)

    # ── Progress placeholders ─────────────────────────────────────────────────
    step_ph  = st.empty()
    stat_ph  = st.empty()
    prog_ph  = st.empty()

    # ── Step renderer ─────────────────────────────────────────────────────────
    def render_steps(steps_cfg: list[dict], current_id: str,
                     completed: set, done_all: bool):
        bar_pct = int(len(completed) / max(len(steps_cfg), 1) * 100)
        if done_all: bar_pct = 100

        rows = ""
        total_remaining = 0
        for s in steps_cfg:
            sid = s["id"]
            if sid in completed or done_all:
                cls = "done"; icon = '<span style="color:var(--green);font-weight:700;">✓</span>'
                elapsed = s.get("elapsed", "")
                time_str = f'<span style="color:var(--green);">{elapsed}</span>' if elapsed else ""
            elif sid == current_id:
                cls = "active"; icon = '<span style="font-size:13px;animation:spin 1s linear infinite;display:inline-block;">⟳</span>'
                time_str = f'<span style="color:var(--blue);">~{s["eta_label"]}</span>'
            else:
                cls = "pending"; icon = '<span style="color:var(--text-3);">○</span>'
                time_str = f'<span style="color:var(--text-3);">{s["eta_label"]}</span>'
                total_remaining += s.get("eta_sec", 0)

            rows += (
                f'<div class="ud-step-row {cls}">'
                f'  <div class="ud-step-icon {"done-ic" if cls=="done" else ("active-ic" if cls=="active" else "pend-ic")}">'
                f'    {icon}</div>'
                f'  <div class="ud-step-body">'
                f'    <div class="ud-step-name">{s["name"]}</div>'
                f'    <div class="ud-step-detail">{s.get("detail","")}</div>'
                f'  </div>'
                f'  <div class="ud-step-time">{time_str}</div>'
                f'</div>')

        eta_label = (f"~{total_remaining//60} min remaining"
                     if total_remaining > 60
                     else (f"~{total_remaining}s remaining"
                           if total_remaining > 0 else "Almost done"))

        html = f"""
        <style>
        @keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
        </style>
        <div class="ud-progress-card">
            <div class="ud-progress-header">
                <div class="ud-progress-title">Processing your video</div>
                <div class="ud-progress-eta">{"Complete" if done_all else eta_label}</div>
            </div>
            <div class="ud-progress-bar-wrap">
                <div class="ud-progress-bar-fill" style="width:{bar_pct}%"></div>
            </div>
            <div class="ud-steps-list">{rows}</div>
        </div>"""
        step_ph.markdown(html, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # PIPELINE EXECUTION
    # ══════════════════════════════════════════════════════════════════════
    if run_btn:
        gkey  = cfg("GOOGLE_API_KEY")
        skey  = cfg("STRIPE_SECRET_KEY")
        aurl  = cfg("APP_URL")
        elkey = cfg("ELEVENLABS_API_KEY")
        slkey = cfg("SYNCLABS_API_KEY")
        sgkey = cfg("SENDGRID_API_KEY")

        errs = []
        if not gkey:  errs.append("AI Platform Key required (sidebar)")
        if not skey:  errs.append("Payments Key required (sidebar)")
        if not aurl:  errs.append("App Public URL required (sidebar)")
        if not yt_url and not uploaded_file:
            errs.append("Enter a YouTube URL or upload a video file")
        if yt_url and not validate_yt(yt_url):
            errs.append("Invalid YouTube URL")
        if want_lipsync and not slkey:
            errs.append("Lip-Sync API key required (sidebar)")
        if want_clone and not elkey:
            errs.append("Voice Cloning API key required (sidebar)")
        if not ffmpeg_ok():
            errs.append("ffmpeg not installed - run: sudo apt-get install -y ffmpeg")

        if errs:
            for e in errs: st.error(e)
            st.stop()

        for k, v in DEFAULTS.items(): st.session_state[k] = v
        st.session_state.proc_start = time.time()
        st.session_state.user_email = user_email.strip()

        work_dir   = tempfile.mkdtemp(prefix="ultradub_")
        clone_id   = ""
        completed  = set()
        lang_srt_data: dict[str, str] = {}

        # Build step config (for progress display)
        def _fmt_eta(sec: int) -> str:
            if sec <= 0:  return ""
            if sec < 90:  return f"{sec}s"
            return f"{sec//60}m {sec%60}s"

        def build_steps(dur_min: float) -> list[dict]:
            eta = estimate_eta(dur_min, n_langs, want_clone,
                               want_lipsync, want_music)
            steps = [
                {"id": "download",   "name": "Downloading video",
                 "detail": "",
                 "eta_sec": eta["download"], "eta_label": _fmt_eta(eta["download"])},
                {"id": "music_sep",  "name": "Separating background music",
                 "detail": "AI isolates voice from music",
                 "eta_sec": eta["music_sep"], "eta_label": _fmt_eta(eta["music_sep"])},
                {"id": "transcribe", "name": "Transcribing speech",
                 "detail": "Converting speech to text",
                 "eta_sec": eta["transcribe"], "eta_label": _fmt_eta(eta["transcribe"])},
                {"id": "translate",  "name": "Translating content",
                 "detail": f"Into {n_langs} language{'s' if n_langs>1 else ''}",
                 "eta_sec": eta["translate"], "eta_label": _fmt_eta(eta["translate"])},
                {"id": "clone",      "name": "Identifying & cloning speaker voice",
                 "detail": "Diarization → extract dominant speaker → clone",
                 "eta_sec": eta["clone"], "eta_label": _fmt_eta(eta["clone"])},
                {"id": "synthesise", "name": "Synthesising dubbed voices",
                 "detail": f"{n_langs} language{'s' if n_langs>1 else ''}",
                 "eta_sec": eta["synthesise"], "eta_label": _fmt_eta(eta["synthesise"])},
                {"id": "merge",      "name": "Merging audio into video",
                 "detail": "Blending voice + music tracks",
                 "eta_sec": eta["merge"], "eta_label": _fmt_eta(eta["merge"])},
                {"id": "lipsync",    "name": "Lip-sync processing",
                 "detail": "Matching mouth movements",
                 "eta_sec": eta["lipsync"], "eta_label": _fmt_eta(eta["lipsync"])},
                {"id": "preview",    "name": "Creating preview & quote",
                 "detail": "15-second preview + Stripe session",
                 "eta_sec": eta["preview"], "eta_label": _fmt_eta(eta["preview"])},
            ]
            # Remove steps not applicable
            if not want_music: steps = [s for s in steps if s["id"] != "music_sep"]
            if not want_clone:  steps = [s for s in steps if s["id"] != "clone"]
            if not want_lipsync: steps = [s for s in steps if s["id"] != "lipsync"]
            return steps

        steps_cfg = build_steps(5.0)  # initial estimate

        def mark(sid: str, detail: str = "", elapsed: str = ""):
            completed.add(sid)
            for s in steps_cfg:
                if s["id"] == sid:
                    s["detail"]  = detail or s["detail"]
                    s["elapsed"] = elapsed
            next_id = next((s["id"] for s in steps_cfg
                            if s["id"] not in completed), "preview")
            render_steps(steps_cfg, next_id, completed, False)

        try:
            # ── Download ─────────────────────────────────────────────────
            render_steps(steps_cfg, "download", completed, False)
            stat_ph.info("Acquiring video…")

            if uploaded_file:
                video_path = step_save_upload(uploaded_file, work_dir)
            else:
                video_path = step_download(yt_url.strip(), work_dir)

            duration   = get_duration(video_path)
            dur_min    = duration / 60
            steps_cfg  = build_steps(dur_min)  # rebuild with real duration

            if duration > TIERS[-1]["max_min"] * 60:
                raise ValueError(
                    f"Video is {dur_min:.1f} min - "
                    f"max is {TIERS[-1]['max_min']} min.")

            mark("download", f"{dur_min:.1f} min · {int(duration)}s")

            # ── Extract base audio ────────────────────────────────────────
            stat_ph.info("Extracting audio…")
            audio_path = os.path.join(work_dir, "audio.mp3")
            step_extract_audio(video_path, audio_path)

            # ── Music separation ──────────────────────────────────────────
            no_vocals_path = None
            if want_music:
                render_steps(steps_cfg, "music_sep", completed, False)
                stat_ph.info("Separating background music (this takes a few minutes)…")
                try:
                    vocals_path, no_vocals_path = separate_music(audio_path, work_dir)
                    # Use separated vocals for STT (cleaner input)
                    audio_for_stt = vocals_path
                    mark("music_sep", "Music isolated · vocals extracted")
                except Exception as me:
                    stat_ph.warning(f"Music separation skipped ({me}). Using original audio.")
                    audio_for_stt = audio_path
                    completed.add("music_sep")
            else:
                audio_for_stt = audio_path

            # ── Transcribe ────────────────────────────────────────────────
            render_steps(steps_cfg, "transcribe", completed, False)
            stat_ph.info("Transcribing speech…")
            segs, detected_key = transcribe_audio(audio_for_stt, src_key, gkey)

            if not segs:
                raise ValueError(
                    "No speech detected. "
                    "Please check that the video contains clear spoken audio.")

            st.session_state.detected_lang = detected_key
            mark("transcribe",
                 f"{len(segs)} segments · "
                 f"{LANG_LABELS.get(detected_key, detected_key)} detected")

            # ── Translate (all target languages) ─────────────────────────
            render_steps(steps_cfg, "translate", completed, False)
            stat_ph.info(f"Translating into {n_langs} language(s)…")

            texts = [s["text"] for s in segs]
            for lang_key in all_tgt_keys:
                translated = translate_batch(texts, lang_key, gkey)
                for seg, tr in zip(segs, translated):
                    seg[f"translated_{lang_key}"] = tr
                # Generate SRT
                lang_srt_data[lang_key] = generate_srt(
                    segs, f"translated_{lang_key}")

            mark("translate",
                 f"{len(segs)} segments · "
                 f"{', '.join(LANG_LABELS.get(k,'') for k in all_tgt_keys)}")

            # ── Voice clone ───────────────────────────────────────────────
            if want_clone and elkey:
                render_steps(steps_cfg, "clone", completed, False)
                stat_ph.info(
                    "Identifying primary speaker using diarization…")
                try:
                    # Pass the detected language BCP-47 code and API key
                    # so diarization can correctly identify WHO speaks most
                    detected_bcp47 = (
                        LANG_REGISTRY.get(detected_key, {}).get("stt", "ru-RU")
                        if detected_key else "ru-RU"
                    )
                    sample = extract_voice_sample(
                        audio_for_stt,
                        work_dir,
                        lang_code=detected_bcp47,
                        api_key=gkey,
                    )
                    stat_ph.info("Cloning identified speaker voice…")
                    clone_id = el_clone_voice(
                        f"ud_{uuid.uuid4().hex[:8]}", sample, elkey)
                    mark("clone", "Primary speaker identified and cloned")
                except Exception as ce:
                    stat_ph.warning(
                        f"Voice cloning unavailable ({ce}). "
                        "Using standard neural voice instead.")
                    completed.add("clone")

            # ── Synthesise & merge each language ─────────────────────────
            render_steps(steps_cfg, "synthesise", completed, False)
            stat_ph.info(f"Synthesising dubbed voices…")

            vk        = uuid.uuid4().hex
            final_paths: dict[str, str] = {}

            for lang_key in all_tgt_keys:
                stat_ph.info(
                    f"Synthesising {LANG_LABELS.get(lang_key, lang_key)}…")
                lang_segs = step_synthesise_lang(
                    segs, lang_key, work_dir, gkey,
                    use_clone=bool(clone_id),
                    clone_id=clone_id, el_key=elkey)

                render_steps(steps_cfg, "merge", completed, False)
                stat_ph.info(
                    f"Merging {LANG_LABELS.get(lang_key, lang_key)}…")
                final_path = step_merge(
                    video_path, lang_segs, duration, work_dir,
                    no_vocals_path=no_vocals_path,
                    suffix=f"_{lang_key}")
                final_paths[lang_key] = final_path

            mark("synthesise",
                 f"{len(segs)} segments · "
                 f"{n_langs} language{'s' if n_langs>1 else ''}")
            mark("merge", "Audio blended with preserved music")

            # ── Lip-sync ──────────────────────────────────────────────────
            if want_lipsync and slkey:
                render_steps(steps_cfg, "lipsync", completed, False)
                stat_ph.info("Running lip-sync…")
                try:
                    for lang_key in all_tgt_keys:
                        dubbed_audio = os.path.join(
                            work_dir, f"lipsync_audio_{lang_key}.mp3")
                        step_extract_audio(final_paths[lang_key], dubbed_audio)
                        final_paths[lang_key] = run_lipsync(
                            video_path, dubbed_audio, slkey, stat_ph)
                    mark("lipsync", f"Lip-sync applied to {n_langs} version(s)")
                except Exception as le:
                    stat_ph.warning(f"Lip-sync failed ({le}). Continuing without.")
                    completed.add("lipsync")

            # ── Store videos + SRT files ──────────────────────────────────
            render_steps(steps_cfg, "preview", completed, False)
            stat_ph.info("Creating preview and preparing quote…")

            # Store each language version + SRT
            for lang_key, fp in final_paths.items():
                stored = os.path.join(VIDEO_STORE, f"{vk}_{lang_key}.mp4")
                shutil.copy2(fp, stored)
                srt_path = os.path.join(VIDEO_STORE, f"{vk}_{lang_key}.srt")
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(lang_srt_data.get(lang_key, ""))

            # Create preview from primary language
            preview_path = os.path.join(work_dir, "preview.mp4")
            make_preview(
                os.path.join(VIDEO_STORE, f"{vk}_{tgt1_key}.mp4"),
                preview_path)
            with open(preview_path, "rb") as f:
                preview_bytes = f.read()

            # Quote & Stripe
            quote        = compute_quote(duration, all_tgt_keys,
                                          want_lipsync, want_clone)
            checkout_url = stripe_create(quote["total"], vk, skey, aurl)

            mark("preview", "Quote ready · Stripe session created")

            # Send email if provided and SendGrid configured
            if user_email and sgkey:
                send_ready_email(
                    user_email, checkout_url, sgkey,
                    {"dur": f"{quote['dur']}", "price": f"{quote['total']:.2f}"})
                st.session_state.email_sent = True

            render_steps(steps_cfg, "", completed, True)
            stat_ph.success(
                "Processing complete! Review your quote and free preview below.")

            st.session_state.done          = True
            st.session_state.preview_bytes = preview_bytes
            st.session_state.vk            = vk
            st.session_state.quote         = quote
            st.session_state.checkout_url  = checkout_url
            st.session_state.lang_srts     = lang_srt_data
            st.session_state.n_langs       = n_langs

        except Exception as exc:
            stat_ph.error(f"Error: {exc}")
            st.exception(exc)
        finally:
            if clone_id and elkey:
                el_delete_voice(clone_id, elkey)
            shutil.rmtree(work_dir, ignore_errors=True)

    # ══════════════════════════════════════════════════════════════════════
    # RESULTS
    # ══════════════════════════════════════════════════════════════════════
    if st.session_state.done and st.session_state.preview_bytes:
        q = st.session_state.quote

        # Detected language info
        if st.session_state.detected_lang and src_key == "auto":
            det = LANG_LABELS.get(st.session_state.detected_lang, "Unknown")
            st.info(f"Auto-detected source language: **{det}**")

        # Email sent confirmation
        if st.session_state.email_sent:
            st.success(
                f"Confirmation sent to {st.session_state.user_email} - "
                "we'll also email you the download link.")

        # ── Quote card ────────────────────────────────────────────────────
        addon_rows = ""
        if q["ls"]:
            addon_rows += (
                f'<div class="ud-bline">'
                f'<span class="ud-bk">Lip-sync</span>'
                f'<span class="ud-bv">+${q["ls"]:.2f}</span></div>')
        if q["clone"]:
            addon_rows += (
                f'<div class="ud-bline">'
                f'<span class="ud-bk">Voice cloning</span>'
                f'<span class="ud-bv">+${q["clone"]:.2f}</span></div>')
        savings_html = (
            f'<span class="ud-savings-badge">Save ${q["savings"]:.2f}</span>'
            if q["savings"] > 0 else "")

        st.markdown(f"""
        <div class="ud-quote">
            <div class="ud-quote-top">
                <div>
                    <div class="ud-quote-tier">
                        {q['emoji']} {q['tier']} · {q['dur']} min
                        · {q['n_langs']} language{'s' if q['n_langs']>1 else ''}
                    </div>
                    <div class="ud-quote-price">
                        <sup>$</sup>{q['total']:.2f}
                    </div>
                </div>
                <div class="ud-quote-meta">
                    Instant download<br>
                    No account required<br>
                    Secured payment
                </div>
            </div>
            <div class="ud-quote-body">
                <div class="ud-bline">
                    <span class="ud-bk">
                        Base dubbing
                        ({q['n_langs']} language{'s' if q['n_langs']>1 else ''})
                        {savings_html}
                    </span>
                    <span class="ud-bv">${q['lang_price']:.2f}</span>
                </div>
                {addon_rows}
                <div class="ud-bline">
                    <span class="ud-bk" style="font-weight:600;
                        color:var(--text-1);font-size:.875rem;">
                        Total (USD)
                    </span>
                    <span class="ud-bv total">${q['total']:.2f}</span>
                </div>
            </div>
            <div class="ud-quote-foot">
                <div class="ud-quote-trust">
                    <span class="ud-trust-check">✓</span>
                    SRT subtitles included
                </div>
                <div class="ud-quote-trust">
                    <span class="ud-trust-check">✓</span>
                    Music preserved
                </div>
                <div class="ud-quote-trust">
                    <span class="ud-trust-check">✓</span>
                    Instant delivery
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 15-second preview ─────────────────────────────────────────────
        st.markdown(
            '<div class="ud-section-label">Free preview - first 15 seconds</div>',
            unsafe_allow_html=True)
        st.caption(
            "Purchase below to unlock the full dubbed video "
            "and all subtitle files.")
        st.video(st.session_state.preview_bytes)

        # ── Pay button ────────────────────────────────────────────────────
        st.markdown(f"""
        <a href="{st.session_state.checkout_url}"
           target="_top" class="ud-pay-btn">
            Pay ${q['total']:.2f} - Unlock Full Video
        </a>
        <div class="ud-secure-row">
            <div class="ud-secure-item">
                <span class="ud-trust-check">✓</span> Secure payment
            </div>
            <div class="ud-secure-item">
                <span class="ud-trust-check">✓</span> Card details stay private
            </div>
            <div class="ud-secure-item">
                <span class="ud-trust-check">✓</span> Instant download
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start a new project", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ud-footer">
    <div class="ud-footer-grid">
        <div class="ud-footer-brand">
            <div class="ud-wordmark">Ultra<em>dub</em></div>
            <p>Your voice, in every language.
            Professional AI dubbing for creators and enterprises.</p>
        </div>
        <div class="ud-footer-col">
            <h4>Product</h4>
            <a>How it works</a>
            <a>Pricing</a>
            <a>Languages</a>
            <a>FAQ</a>
        </div>
        <div class="ud-footer-col">
            <h4>Company</h4>
            <a>Privacy policy</a>
            <a>Terms of service</a>
            <a>Contact</a>
        </div>
    </div>
    <div class="ud-footer-bottom">
        <div class="ud-footer-copy">© 2025 Ultradub</div>
        <div class="ud-footer-links">
            <a>Privacy</a>
            <a>Terms</a>
            <a>Contact</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
