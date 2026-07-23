"""AI GitHub Agent Streamlit application."""

import html
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from modules.analyzer import Analyzer
from modules.github_client import GitHubAPIError, GitHubClient
from modules.intent_router import IntentRouter
from modules.knowledge_base import KnowledgeBase
from modules.learning_path import LearningPathGenerator
from modules.llm_client import LLMClient


st.set_page_config(
    page_title="AI GitHub Agent",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --primary: #111111;
        --primary-hover: #000000;
        --primary-soft: #f4f4f4;
        --page-bg: #ffffff;
        --panel-bg: #ffffff;
        --soft-bg: #f7f7f7;
        --nav-active: #ececec;
        --text-title: #0d0d0d;
        --text-body: #171717;
        --text-muted: #6b6b6b;
        --text-soft: #424242;
        --border: #e5e5e5;
        --border-soft: #ededed;
        --danger: #d92d20;
    }
    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text-body);
        letter-spacing: 0;
    }
    [data-testid="stAppViewContainer"] { background: var(--page-bg); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] {
        background: #f9f9f9;
        border-right: 1px solid var(--border);
        min-width: 274px;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding: 1rem 0.85rem 1rem 0.85rem;
    }
    .block-container {
        max-width: 1480px;
        padding-top: 1rem;
        padding-bottom: 4.5rem;
    }
    .main .block-container { padding-left: 3rem; padding-right: 3rem; }
    h1, h2, h3 {
        color: var(--text-title);
        letter-spacing: 0;
    }
    h1 { font-size: 1.5rem; line-height: 1.25; font-weight: 760; }
    h2 { font-size: 1.22rem; line-height: 1.3; font-weight: 740; }
    h3 { font-size: 1.05rem; line-height: 1.35; font-weight: 720; }
    a { color: var(--text-title); text-decoration: none; }
    a:hover { color: var(--primary); }
    .sidebar-brand {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.65rem;
        padding: 0.15rem 0.45rem 1rem 0.45rem;
        color: #111111;
        font-weight: 760;
    }
    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.62rem;
        min-width: 0;
    }
    .brand-mark {
        width: 30px;
        height: 30px;
        border: 1px solid var(--border);
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        color: #111111;
        flex: 0 0 auto;
    }
    .brand-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .collapse-mark { color: var(--text-muted); font-size: 0.95rem; }
    .side-section {
        color: var(--text-body);
        font-size: 0.84rem;
        font-weight: 720;
        margin: 1.25rem 0.65rem 0.45rem 0.65rem;
    }
    .side-muted {
        color: var(--text-muted);
        font-size: 0.88rem;
        margin: 0.25rem 0.65rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .side-history-item {
        background: var(--nav-active);
        border-radius: 12px;
        color: var(--text-body);
        font-size: 0.88rem;
        padding: 0.58rem 0.75rem;
        margin: 0.25rem 0 0.4rem 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .account-pill {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-top: 1.5rem;
        color: var(--text-body);
        font-size: 0.9rem;
        font-weight: 650;
    }
    .account-avatar {
        width: 32px;
        height: 32px;
        border-radius: 999px;
        background: var(--nav-active);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.82rem;
        color: var(--text-body);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.24rem;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 12px;
        min-height: 2.45rem;
        padding: 0.18rem 0.72rem;
        color: var(--text-body);
        font-weight: 690;
        transition: background 140ms ease, color 140ms ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: var(--soft-bg);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: var(--nav-active);
        color: #111111;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 0.96rem;
        line-height: 1.2;
        font-weight: 690;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none;
    }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 2.8rem;
        margin: 0 0 1.2rem 0;
    }
    .top-context {
        color: var(--text-muted);
        font-size: 0.9rem;
        font-weight: 650;
    }
    .top-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.5rem;
    }
    .top-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.42rem;
        min-height: 2rem;
        border: 1px solid transparent;
        border-radius: 999px;
        padding: 0.22rem 0.65rem;
        color: var(--text-body);
        font-weight: 720;
        font-size: 0.9rem;
        background: transparent;
    }
    .top-pill.secondary { color: var(--text-muted); }
    .chat-grid {
        align-items: stretch;
    }
    .chat-home {
        max-width: 820px;
        margin: 12vh auto 0 auto;
        text-align: center;
    }
    .chat-logo-row {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        margin-bottom: 2.1rem;
    }
    .chat-logo-row .brand-mark {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        color: #000000;
    }
    .chat-title {
        font-size: 3.15rem;
        line-height: 1.05;
        font-weight: 780;
        color: #050505;
        letter-spacing: 0;
    }
    .chat-subtitle {
        color: var(--text-muted);
        font-size: 0.98rem;
        margin-top: -1.4rem;
        margin-bottom: 1rem;
    }
    .composer-shell {
        border: 1px solid var(--border);
        border-radius: 999px;
        background: #ffffff;
        padding: 0.58rem 0.62rem 0.58rem 1rem;
        box-shadow: 0 2px 8px rgba(24, 32, 50, 0.05);
        margin: 0.45rem 0 0.85rem 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) {
        border: 1px solid var(--border);
        border-radius: 999px;
        background: #ffffff;
        padding: 0.58rem 0.62rem 0.58rem 1rem;
        box-shadow: 0 2px 8px rgba(24, 32, 50, 0.05);
        margin: 0.45rem 0 0.85rem 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) div[data-testid="stForm"] {
        border: 0;
        padding: 0;
        background: transparent;
    }
    .composer-shell [data-testid="stTextInput"] input {
        border: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        font-size: 1.02rem;
        color: var(--text-body);
        padding-left: 0;
    }
    .composer-shell [data-testid="stTextInput"] input::placeholder {
        color: var(--text-muted);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) [data-testid="stTextInput"] input {
        border: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        font-size: 1.02rem;
        color: var(--text-body);
        padding-left: 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) [data-testid="stTextInput"] input::placeholder {
        color: var(--text-muted);
    }
    .composer-shell [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border: 0;
        background: transparent;
        box-shadow: none;
        font-weight: 720;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border: 0;
        background: transparent;
        box-shadow: none;
        font-weight: 720;
    }
    .composer-shell .stButton > button,
    .composer-shell button[data-testid="baseButton-primary"],
    .composer-shell button[data-testid="baseButton-secondary"] {
        min-height: 2.55rem;
        width: 2.55rem;
        padding: 0;
        border-radius: 999px;
        background: #050505 !important;
        color: #ffffff !important;
        border-color: #050505 !important;
        font-size: 1rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) .stButton > button,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) button[data-testid="baseButton-primary"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]) button[data-testid="baseButton-secondary"] {
        min-height: 2.55rem;
        width: 2.55rem;
        padding: 0;
        border-radius: 999px;
        background: #050505 !important;
        color: #ffffff !important;
        border-color: #050505 !important;
        font-size: 1rem;
    }
    .quick-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.5rem;
        margin: 0.65rem 0 1.2rem 0;
    }
    .quick-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 0.35rem 0.68rem;
        background: #ffffff;
        color: var(--text-body);
        font-size: 0.9rem;
        font-weight: 650;
    }
    .connect-card {
        max-width: 560px;
        margin: 1rem auto 0 auto;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: #ffffff;
        padding: 0.9rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
        box-shadow: 0 2px 8px rgba(24, 32, 50, 0.04);
        text-align: left;
    }
    .connect-title { color: var(--text-body); font-weight: 740; font-size: 0.98rem; }
    .connect-copy { color: var(--text-muted); font-size: 0.88rem; margin-top: 0.12rem; }
    .connect-action {
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 0.45rem 0.9rem;
        font-weight: 720;
        background: #ffffff;
        white-space: nowrap;
    }
    .thread-shell {
        max-width: 860px;
        margin: 0 auto;
    }
    .thread-toolbar {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .thought-panel {
        position: sticky;
        top: 1rem;
        min-height: calc(100vh - 2rem);
        border-left: 1px solid var(--border);
        padding: 0.1rem 0 1rem 1.15rem;
        color: var(--text-body);
        background: var(--page-bg);
    }
    .thought-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 1.05rem;
        font-weight: 760;
        margin-bottom: 1.2rem;
    }
    .thought-close { color: var(--text-muted); font-size: 1.4rem; font-weight: 400; }
    .thought-block {
        border-top: 1px solid var(--border);
        padding: 1rem 0 1.05rem 0;
    }
    .thought-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-body);
        font-size: 0.95rem;
        font-weight: 760;
        margin-bottom: 0.6rem;
    }
    .thought-title span {
        color: var(--text-muted);
        font-weight: 650;
    }
    .thought-block ul {
        margin: 0;
        padding-left: 1.1rem;
        color: var(--text-muted);
        font-size: 0.9rem;
        line-height: 1.45;
    }
    .thought-block li { margin-bottom: 0.48rem; }
    .hero-panel {
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.15rem 1.25rem;
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.05rem;
        line-height: 1.15;
        font-weight: 760;
        color: var(--text-title);
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        color: var(--text-muted);
        font-size: 0.98rem;
        margin-bottom: 0.85rem;
    }
    .stat-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.65rem;
        margin-top: 0.75rem;
    }
    .stat-pill {
        border: 1px solid var(--border-soft);
        border-radius: 10px;
        padding: 0.65rem 0.75rem;
        background: #ffffff;
    }
    .stat-label { color: var(--text-muted); font-size: 0.76rem; }
    .stat-value { color: var(--text-body); font-size: 1rem; font-weight: 700; margin-top: 0.1rem; }
    .section-label {
        color: var(--text-soft);
        font-size: 0.84rem;
        font-weight: 650;
        margin: 0.75rem 0 0.35rem 0;
    }
    .repo-card {
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.95rem 1rem;
        margin: 0.65rem 0;
        background: #ffffff;
    }
    .repo-title { font-size: 1.05rem; font-weight: 750; margin-bottom: 0.25rem; }
    .repo-desc { color: var(--text-soft); font-size: 0.91rem; min-height: 1.25rem; }
    .repo-meta {
        color: var(--text-muted);
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.55rem;
        font-size: 0.82rem;
    }
    .repo-chip {
        border: 1px solid var(--border-soft);
        border-radius: 999px;
        background: var(--soft-bg);
        padding: 0.18rem 0.55rem;
    }
    .compare-card {
        border: 1px solid var(--border);
        border-radius: 18px;
        background: #ffffff;
        overflow: hidden;
        margin: 0.85rem 0 1rem 0;
        box-shadow: 0 2px 8px rgba(24, 32, 50, 0.04);
    }
    .compare-card-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.95rem 1rem 0.75rem 1rem;
        border-bottom: 1px solid var(--border);
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }
    .compare-card-title {
        color: var(--text-title);
        font-size: 1.05rem;
        line-height: 1.35;
        font-weight: 760;
    }
    .compare-card-subtitle {
        color: var(--text-muted);
        font-size: 0.86rem;
        line-height: 1.4;
        margin-top: 0.18rem;
    }
    .compare-card-count {
        border: 1px solid var(--border-soft);
        border-radius: 999px;
        background: #ffffff;
        color: var(--text-muted);
        font-size: 0.82rem;
        font-weight: 650;
        padding: 0.22rem 0.6rem;
        white-space: nowrap;
    }
    .compare-table-wrap {
        overflow-x: auto;
        width: 100%;
    }
    .compare-table {
        width: 100%;
        min-width: 760px;
        border-collapse: separate;
        border-spacing: 0;
    }
    .compare-table th,
    .compare-table td {
        padding: 0.8rem 0.9rem;
        border-bottom: 1px solid var(--border-soft);
        border-right: 1px solid var(--border-soft);
        vertical-align: top;
        text-align: left;
    }
    .compare-table th:last-child,
    .compare-table td:last-child {
        border-right: 0;
    }
    .compare-table tr:last-child td {
        border-bottom: 0;
    }
    .compare-table th {
        background: #ffffff;
        color: var(--text-title);
        font-size: 0.88rem;
        font-weight: 760;
    }
    .compare-dimension {
        width: 9rem;
        min-width: 9rem;
        color: var(--text-soft);
        background: #fbfbfa;
        font-size: 0.84rem;
        font-weight: 720;
    }
    .compare-repo-name {
        color: var(--text-title);
        font-size: 0.95rem;
        font-weight: 760;
        line-height: 1.3;
    }
    .compare-repo-desc {
        color: var(--text-muted);
        font-size: 0.8rem;
        line-height: 1.35;
        margin-top: 0.22rem;
        max-width: 18rem;
    }
    .compare-cell {
        color: var(--text-body);
        font-size: 0.88rem;
        line-height: 1.45;
    }
    .compare-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-top: 0.45rem;
    }
    .compare-chip {
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--border-soft);
        border-radius: 999px;
        background: var(--soft-bg);
        color: var(--text-muted);
        font-size: 0.76rem;
        line-height: 1.2;
        padding: 0.16rem 0.5rem;
        white-space: nowrap;
    }
    .compare-score {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 3.4rem;
        border-radius: 999px;
        background: #050505;
        color: #ffffff;
        font-size: 0.82rem;
        font-weight: 760;
        padding: 0.22rem 0.52rem;
    }
    .compare-recommendation {
        border-top: 1px solid var(--border);
        padding: 0.8rem 1rem 0.95rem 1rem;
        background: #ffffff;
        color: var(--text-muted);
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .compare-recommendation b {
        color: var(--text-body);
    }
    .answer-summary {
        border-left: 3px solid var(--primary);
        background: var(--primary-soft);
        padding: 0.8rem 0.95rem;
        border-radius: 10px;
        margin: 0.35rem 0;
    }
    .muted { color: var(--text-muted); font-size: 0.9rem; }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--border);
        padding: 0.7rem;
        border-radius: 10px;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 18px;
        background: transparent;
        padding: 0.2rem 0;
    }
    .stButton > button {
        border-radius: 999px;
        min-height: 2.35rem;
        border: 1px solid var(--border);
        background: #ffffff;
        color: var(--text-body);
        font-weight: 680;
        box-shadow: none;
    }
    .stButton > button:hover {
        border-color: var(--border);
        background: var(--soft-bg);
        color: #111111;
    }
    button[data-testid="baseButton-primary"] {
        background: #050505 !important;
        border-color: #050505 !important;
        color: #ffffff !important;
    }
    input, textarea {
        border-radius: 12px !important;
    }
    div[data-baseweb="input"] {
        border-radius: 12px;
    }
    div[data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid var(--border);
    }
    @media (max-width: 1180px) {
        .thought-panel { display: none; }
        .chat-home { margin-top: 8vh; }
    }
    @media (max-width: 900px) {
        .main .block-container { padding-left: 1rem; padding-right: 1rem; }
        .stat-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .hero-title { font-size: 1.65rem; }
        .chat-title { font-size: 2.25rem; }
        .chat-logo-row .brand-mark { width: 46px; height: 46px; }
        .top-bar { align-items: flex-start; gap: 0.6rem; }
    }

    /* GPT-style chat experience */
    .chat-home {
        max-width: 760px;
        margin: 14vh auto 0 auto;
        text-align: center;
    }
    .chat-logo-row {
        margin-bottom: 1rem;
    }
    .chat-logo-row .brand-mark {
        width: 48px;
        height: 48px;
        border-radius: 15px;
        background: #111111;
        color: #ffffff;
        border-color: #111111;
    }
    .chat-title {
        font-size: 2rem;
        line-height: 1.2;
        font-weight: 720;
        color: #0d0d0d;
    }
    .chat-subtitle {
        max-width: 600px;
        margin: 0.65rem auto 1.6rem auto;
        color: #6b6b6b;
        font-size: 1rem;
        line-height: 1.6;
    }
    .chat-status-line {
        margin-top: 1rem;
        color: #8a8a8a;
        font-size: 0.82rem;
        text-align: center;
    }
    .thread-heading {
        padding: 0.2rem 0 1rem 0;
        border-bottom: 1px solid var(--border-soft);
        margin-bottom: 0.25rem;
    }
    .thread-heading-title {
        color: var(--text-title);
        font-size: 1rem;
        font-weight: 700;
    }
    .thread-heading-copy {
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-top: 0.18rem;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 0;
        background: transparent;
        padding: 1.05rem 0;
        gap: 0.7rem;
    }
    div[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        color: var(--text-body);
        line-height: 1.65;
    }
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        justify-content: flex-start;
    }
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] {
        display: none;
    }
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        flex: 0 1 auto;
        max-width: 78%;
        background: #f4f4f4;
        border-radius: 18px;
        padding: 0.62rem 0.9rem;
    }
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageAvatarAssistant"],
    div[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarCustom"] {
        width: 30px;
        height: 30px;
        min-width: 30px;
        border-radius: 9px;
        background: #111111;
        color: #ffffff;
    }
    [data-testid="stBottomBlockContainer"] {
        max-width: 860px;
        margin: 0 auto;
        padding: 0.75rem 1rem 1rem 1rem;
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, #ffffff 30%);
    }
    [data-testid="stChatInput"] > div {
        border: 1px solid #d9d9d9;
        border-radius: 24px;
        background: #ffffff;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
    }
    [data-testid="stChatInput"] textarea {
        min-height: 3.25rem;
        padding-top: 0.85rem;
        color: var(--text-body);
    }
    .recommendation-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin: 1rem 0 0.45rem 0;
        color: var(--text-title);
        font-size: 0.92rem;
        font-weight: 720;
    }
    .recommendation-count {
        color: var(--text-muted);
        font-size: 0.78rem;
        font-weight: 500;
    }
    .repo-card {
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.95rem 1rem;
        margin: 0.65rem 0 0.45rem 0;
        background: #ffffff;
        transition: border-color 140ms ease, background 140ms ease;
    }
    .repo-card-link,
    .repo-card-link:hover {
        display: block;
        color: inherit;
        text-decoration: none;
    }
    .repo-card:hover {
        border-color: #cfcfcf;
        background: #fdfdfd;
    }
    .repo-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
    }
    .repo-rank {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.45rem;
        height: 1.45rem;
        border-radius: 999px;
        background: #111111;
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .repo-open-mark {
        margin-left: auto;
        color: var(--text-muted);
        font-size: 0.9rem;
        font-weight: 500;
    }
    .repo-tech-label {
        color: var(--text-muted);
        font-size: 0.76rem;
        font-weight: 650;
        margin-top: 0.65rem;
    }
    .repo-score {
        border-radius: 999px;
        background: #111111;
        color: #ffffff;
        padding: 0.18rem 0.58rem;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .repo-reason {
        color: var(--text-muted);
        font-size: 0.84rem;
        line-height: 1.5;
        margin-top: 0.58rem;
    }
    .stButton > button {
        border-radius: 12px;
    }
    @media (max-width: 900px) {
        .chat-home { margin-top: 8vh; }
        .chat-title { font-size: 1.65rem; }
        [data-testid="stBottomBlockContainer"] { padding-left: 0.75rem; padding-right: 0.75rem; }
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
            max-width: 90%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


APP_MARK_SVG = """
<svg width="22" height="22" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M39 8L27.8 29.4L9 40L20.2 18.6L39 8Z" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linejoin="round"/>
  <path d="M12 26C12 16.6 19.6 9 29 9C31.8 9 34.4 9.7 36.7 10.9" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/>
  <path d="M36 22C36 31.4 28.4 39 19 39C16.2 39 13.6 38.3 11.3 37.1" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/>
</svg>
"""

PAGE_OPTIONS = ["智能聊天", "项目搜索", "AI 问答", "项目分析", "项目对比", "我的收藏", "每日推荐", "数据概览"]
NAV_LABELS = {
    "项目搜索": "⌕  Search",
    "智能聊天": "✎  Chat",
    "AI 问答": "◌  Ask",
    "项目分析": "◇  Analyze",
    "项目对比": "⇄  Compare",
    "我的收藏": "☆  Library",
    "每日推荐": "◈  Daily",
    "数据概览": "▦  Overview",
}
PAGE_CONTEXT = {
    "项目搜索": "Search open-source repositories",
    "智能聊天": "AI GitHub 项目推荐助手",
    "AI 问答": "Ask about current repository",
    "项目分析": "Analyze repository structure",
    "项目对比": "Compare repositories",
    "我的收藏": "Saved knowledge base",
    "每日推荐": "Daily GitHub radar",
    "数据概览": "Workspace overview",
}


def init_state() -> None:
    if "github" not in st.session_state:
        st.session_state.github = GitHubClient()
    if "llm" not in st.session_state:
        st.session_state.llm = LLMClient()
    if "kb" not in st.session_state:
        st.session_state.kb = KnowledgeBase()
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = Analyzer()
    if "learning" not in st.session_state:
        st.session_state.learning = LearningPathGenerator()
    if "router" not in st.session_state:
        st.session_state.router = IntentRouter()
    st.session_state.setdefault("search_results", [])
    st.session_state.setdefault("current_repo", None)
    st.session_state.setdefault("analysis", None)
    st.session_state.setdefault("compare_repos", [])
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("chat_memory", {})
    st.session_state.setdefault("chat_pending_artifact", None)
    st.session_state.setdefault("chat_artifact_counter", 0)
    st.session_state.setdefault("last_user_message", "")
    st.session_state.setdefault("last_answer", "")


def main() -> None:
    init_state()
    page = render_sidebar()
    render_top_bar(page)

    if page == "智能聊天":
        render_chat()
    elif page == "数据概览":
        render_home()
    elif page == "项目搜索":
        render_search()
    elif page == "项目分析":
        render_analysis()
    elif page == "AI 问答":
        render_qa()
    elif page == "项目对比":
        render_compare()
    elif page == "我的收藏":
        render_favorites()
    elif page == "每日推荐":
        render_daily()


def render_sidebar() -> str:
    active_page = st.session_state.get("active_page", "智能聊天")
    if active_page not in PAGE_OPTIONS:
        active_page = "智能聊天"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="brand-lockup">
                <div class="brand-mark">{APP_MARK_SVG}</div>
                <div class="brand-text">AI GitHub Agent</div>
            </div>
            <div class="collapse-mark">«</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "导航",
        PAGE_OPTIONS,
        index=PAGE_OPTIONS.index(active_page),
        format_func=lambda item: NAV_LABELS.get(item, item),
        key="active_page",
        label_visibility="collapsed",
    )

    st.sidebar.markdown('<div class="side-section">Chat</div>', unsafe_allow_html=True)
    st.sidebar.button("＋ 新对话", use_container_width=True, on_click=start_new_chat)

    st.sidebar.markdown('<div class="side-section">History</div>', unsafe_allow_html=True)
    history_label = st.session_state.last_user_message or "No recent request"
    st.sidebar.markdown(
        f'<div class="side-history-item">{html.escape(history_label[:42])}</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="side-muted">See all</div>', unsafe_allow_html=True)

    selected_repos = st.session_state.compare_repos
    st.sidebar.markdown('<div class="side-section">项目对比</div>', unsafe_allow_html=True)
    if selected_repos:
        for repo in selected_repos:
            st.sidebar.markdown(
                f'<div class="side-muted">✓ {html.escape(repo.get("full_name") or "")}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.sidebar.markdown('<div class="side-muted">尚未选择项目</div>', unsafe_allow_html=True)
    st.sidebar.button(
        f"开始对比（{len(selected_repos)}）",
        type="primary",
        use_container_width=True,
        disabled=len(selected_repos) < 2,
        on_click=queue_selected_comparison,
    )
    if selected_repos:
        st.sidebar.button("清空对比", use_container_width=True, on_click=clear_selected_comparison)

    provider_labels = {
        name: meta["label"] for name, meta in config.LLM_PROVIDERS.items()
    }
    providers = list(config.LLM_PROVIDERS.keys())
    with st.sidebar.expander("模型设置", expanded=False):
        provider = st.selectbox(
            "LLM Provider",
            providers,
            index=providers.index(st.session_state.llm.provider)
            if st.session_state.llm.provider in providers
            else 0,
            format_func=lambda item: provider_labels[item],
        )
        models = config.LLM_PROVIDERS[provider]["models"]
        model = st.selectbox("Model", models)
        st.session_state.llm.set_provider(provider, model)

    status = st.session_state.llm.provider_status()
    st.sidebar.caption("连接状态")
    st.sidebar.write(f"DeepSeek: {'已配置' if status['deepseek'] else '未配置'}")
    st.sidebar.write(f"GitHub Token: {'已配置' if config.GITHUB_TOKEN else '未配置'}")
    if not status.get(provider):
        st.sidebar.warning("当前 LLM 未配置 API key，应用会使用规则分析兜底。")
    st.sidebar.markdown(
        """
        <div class="account-pill">
            <span class="account-avatar">JS</span>
            <span>Local Workspace</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return page


def start_new_chat() -> None:
    st.session_state.chat_messages = []
    st.session_state.chat_memory = {}
    st.session_state.chat_pending_artifact = None
    st.session_state.chat_artifact_counter = 0
    st.session_state.search_results = []
    st.session_state.compare_repos = []
    st.session_state.last_user_message = ""
    st.session_state.last_answer = ""
    st.session_state.active_page = "智能聊天"


def queue_selected_comparison() -> None:
    repos = st.session_state.get("compare_repos", [])
    if len(repos) < 2:
        return
    names = " 和 ".join(repo.get("full_name", "") for repo in repos if repo.get("full_name"))
    st.session_state.active_page = "智能聊天"
    submit_chat(f"请对比这些项目：{names}")


def submit_chat_from_action(message: str) -> None:
    st.session_state.active_page = "智能聊天"
    submit_chat(message)


def start_learning_plan(repo_name: str) -> None:
    submit_chat_from_action(f"请为 {repo_name} 制定一个 2 周学习计划")


def clear_selected_comparison() -> None:
    st.session_state.compare_repos = []


def start_new_project() -> None:
    st.session_state.current_repo = None
    st.session_state.analysis = None
    st.session_state.active_page = "项目分析"


def render_top_bar(page: str) -> None:
    context = PAGE_CONTEXT.get(page, page)
    private_state = "Private" if config.GITHUB_TOKEN else "Public"
    provider_label = config.LLM_PROVIDERS.get(st.session_state.llm.provider, {}).get("label", "Rules")
    model_label = st.session_state.llm.model if st.session_state.llm.is_ready() else "Rules fallback"
    st.markdown(
        f"""
        <div class="top-bar">
            <div class="top-context">{html.escape(context)}</div>
            <div class="top-actions">
                <span class="top-pill">{html.escape(provider_label)} · {html.escape(model_label)}</span>
                <span class="top-pill secondary">◌ {private_state}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat() -> None:
    stats = st.session_state.kb.get_statistics()
    _, main_col, _ = st.columns([0.55, 6.4, 0.55])

    with main_col:
        if st.session_state.chat_messages or st.session_state.search_results:
            render_chat_thread()
        else:
            render_chat_landing(stats)

    prompt = st.chat_input("描述你想找的项目，例如：适合新手学习的 Python AI Agent 项目")
    if prompt and prompt.strip():
        submit_chat(prompt.strip())
        st.rerun()


def render_chat_landing(stats: Dict[str, Any]) -> None:
    provider = config.LLM_PROVIDERS.get(st.session_state.llm.provider, {}).get("label", "Rules")
    model_state = f"{provider} · {st.session_state.llm.model}" if st.session_state.llm.is_ready() else "规则推荐模式"
    st.markdown(
        f"""
        <div class="chat-home">
            <div class="chat-logo-row">
                <div class="brand-mark">{APP_MARK_SVG}</div>
            </div>
            <div class="chat-title">今天想探索什么开源项目？</div>
            <div class="chat-subtitle">告诉我你的目标、技术栈或经验水平。我会搜索 GitHub、解释推荐理由，并在后续对话中继续帮你筛选、比较和制定学习路线。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_quick_actions("home")
    st.markdown(
        f"""
        <div class="chat-status-line">{html.escape(model_state)} · 已收藏 {stats["favorites_count"]} 个项目 · 支持连续追问</div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_thread() -> None:
    first_request = next(
        (message.get("content", "") for message in st.session_state.chat_messages if message.get("role") == "user"),
        "GitHub 项目推荐",
    )
    toolbar_left, toolbar_mid, toolbar_right = st.columns([4.8, 0.9, 0.9])
    toolbar_left.markdown(
        f"""
        <div class="thread-heading">
            <div class="thread-heading-title">{html.escape(first_request[:52])}</div>
            <div class="thread-heading-copy">可以继续追问语言、Stars、活跃度、难度或项目对比</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if toolbar_mid.button("新对话", key="thread_clear", use_container_width=True):
        start_new_chat()
        st.rerun()
    if toolbar_right.button("重试", key="thread_retry", use_container_width=True) and st.session_state.last_user_message:
        submit_chat(st.session_state.last_user_message, regenerate=True)
        st.rerun()

    for message in st.session_state.chat_messages:
        avatar = "🤖" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"], unsafe_allow_html=message["role"] == "assistant")
            artifact = message.get("artifact")
            if artifact and artifact.get("type") == "repo_recommendations":
                render_recommendation_artifact(artifact)

def render_quick_actions(key_prefix: str) -> None:
    quick_prompts = [
        ("寻找 AI Agent 项目", "帮我找适合学习 AI Agent 的 Python 项目"),
        ("寻找 RAG 入门项目", "推荐几个适合新手学习 RAG 的 Python 项目"),
        ("寻找活跃的前端项目", "找最近仍活跃维护的 TypeScript 前端项目"),
        ("比较热门 Agent 框架", "对比 LangGraph、CrewAI 和 AutoGen"),
    ]
    cols = st.columns(2)
    for idx, (label, prompt) in enumerate(quick_prompts):
        with cols[idx % 2]:
            st.button(
                label,
                key=f"{key_prefix}_quick_{idx}",
                use_container_width=True,
                help=prompt,
                on_click=submit_chat_from_action,
                args=(prompt,),
            )


def submit_chat(message: str, regenerate: bool = False) -> None:
    if regenerate and st.session_state.chat_messages:
        if st.session_state.chat_messages[-1].get("role") == "assistant":
            st.session_state.chat_messages.pop()
    else:
        st.session_state.chat_messages.append({"role": "user", "content": message})
    st.session_state.last_user_message = message
    st.session_state.chat_pending_artifact = None
    with st.spinner("正在理解需求并搜索 GitHub..."):
        try:
            answer = handle_chat_message(message)
        except GitHubAPIError as exc:
            answer = f"GitHub 数据获取失败：{exc}"
    st.session_state.last_answer = answer
    assistant_message: Dict[str, Any] = {"role": "assistant", "content": answer}
    if st.session_state.chat_pending_artifact:
        assistant_message["artifact"] = st.session_state.chat_pending_artifact
    st.session_state.chat_messages.append(assistant_message)
    st.session_state.chat_pending_artifact = None


def handle_chat_message(message: str) -> str:
    memory = st.session_state.chat_memory
    routed = st.session_state.router.route(message, memory)
    intent = routed["intent"]

    if intent in ("search", "refine_search"):
        return chat_search(routed)
    if intent == "compare":
        return chat_compare(routed)
    if intent == "intro":
        return chat_intro(routed)
    if intent == "learning":
        return chat_learning(routed)
    if intent == "followup":
        return chat_followup(routed)
    return chat_general(routed)


def chat_search(routed: Dict[str, Any]) -> str:
    filters = dict(routed["filters"])
    query = routed["query"]
    memory = st.session_state.chat_memory
    is_refinement = routed["intent"] == "refine_search" and memory.get("last_search_query")
    if is_refinement:
        query = memory["last_search_query"]
        filters = {**memory.get("last_filters", {}), **filters}

    raw = routed["raw"].lower()
    wants_next_batch = is_refinement and any(
        phrase in raw for phrase in ("更多", "换一批", "再来", "下一批", "还有吗")
    )
    page = int(memory.get("last_search_page", 1)) + 1 if wants_next_batch else 1

    repos = st.session_state.github.search_repos(
        query=query,
        language=filters.get("language", ""),
        min_stars=filters.get("min_stars", 0),
        license_id=filters.get("license", ""),
        recent=filters.get("recent", False),
        sort="updated" if filters.get("recent") else "stars",
        per_page=10,
        page=page,
    )
    repos = rank_recommendations(repos, routed["raw"], filters)

    if not repos:
        if wants_next_batch:
            return "这组条件下暂时没有更多结果了。你可以放宽 Stars、语言或最近更新时间，我会继续帮你找。"
        st.session_state.search_results = []
        return f"没有找到明显匹配 `{query}` 的项目。可以换成更具体的技术词，例如 `LangGraph RAG Python`。"

    st.session_state.search_results = repos
    memory["last_search_query"] = query
    memory["last_filters"] = filters
    memory["last_search_page"] = page
    memory["last_repos"] = repos
    st.session_state.chat_artifact_counter += 1
    st.session_state.chat_pending_artifact = {
        "type": "repo_recommendations",
        "id": f"repos_{st.session_state.chat_artifact_counter}",
        "query": query,
        "filters": filters,
        "page": page,
        "repos": repos[:10],
    }
    return format_recommendations(repos, query, filters, page)


def chat_compare(routed: Dict[str, Any]) -> str:
    repos = resolve_repos_from_route(routed)
    if len(repos) < 2:
        return "我还缺少至少 2 个项目。你可以输入 `对比 langchain-ai/langgraph 和 crewAIInc/crewAI`，或先搜索后说 `对比第 1 和第 3 个`。"

    st.session_state.compare_repos = repos
    st.session_state.chat_memory["last_compare_repos"] = repos
    basic = format_compare_table(repos)
    best = max(repos, key=lambda repo: st.session_state.analyzer.recommendation_score(repo))
    hottest = max(repos, key=lambda repo: repo.get("stargazers_count", 0) or 0)
    return (
        f"已对比你在侧边栏选择的 **{len(repos)} 个项目**。\n\n{basic}\n\n"
        f"综合评分最高的是 **{best.get('full_name') or ''}**；"
        f"GitHub Stars 最高的是 **{hottest.get('full_name') or ''}**。"
        "如果你告诉我使用场景，我还可以继续给出更具体的选型建议。"
    )


def chat_intro(routed: Dict[str, Any]) -> str:
    repo = resolve_single_repo(routed)
    if not repo:
        return "我没能识别到具体项目。请提供 GitHub URL 或 `owner/repo`，例如 `microsoft/autogen`。"
    if not run_analysis(repo["full_name"], load_issues=False):
        return "项目数据获取失败，请稍后重试。"
    analysis = st.session_state.analysis
    if not analysis:
        return "项目数据获取失败，请稍后重试。"
    st.session_state.chat_memory["current_repo"] = repo["full_name"]
    return format_project_intro(analysis)


def chat_learning(routed: Dict[str, Any]) -> str:
    repo = resolve_single_repo(routed)
    if repo:
        if not run_analysis(repo["full_name"], load_issues=False):
            return "项目数据获取失败，请稍后重试。"
    elif not st.session_state.analysis and st.session_state.chat_memory.get("current_repo"):
        if not run_analysis(st.session_state.chat_memory["current_repo"], load_issues=False):
            return "项目数据获取失败，请稍后重试。"

    analysis = st.session_state.analysis
    if not analysis:
        return "请先告诉我要学习哪个项目，例如 `给 langchain-ai/langgraph 一个 2 周学习计划`。"
    st.session_state.chat_memory["current_repo"] = analysis["repo"]["full_name"]
    return format_learning_plan(analysis, routed["period"], routed["level"])


def chat_followup(routed: Dict[str, Any]) -> str:
    raw = routed["raw"]
    if routed["indexes"]:
        repos = repos_from_indexes(routed["indexes"])
        if len(repos) >= 2:
            return chat_compare({**routed, "repos": [repo["full_name"] for repo in repos]})
        if len(repos) == 1:
            if run_analysis(repos[0]["full_name"], load_issues=False):
                return format_project_intro(st.session_state.analysis)
            return "项目数据获取失败，请稍后重试。"
    if "学习" in raw or "路线" in raw or "计划" in raw:
        return chat_learning(routed)
    if "新手" in raw or "简单" in raw or "更多" in raw:
        routed["intent"] = "refine_search"
        routed["filters"]["difficulty"] = "入门"
        return chat_search(routed)
    return chat_general(routed)


def chat_general(routed: Dict[str, Any]) -> str:
    context = ""
    if st.session_state.analysis:
        context = st.session_state.analysis.get("context", "")
    if st.session_state.llm.is_ready():
        recent_messages = st.session_state.chat_messages[-8:]
        conversation = "\n".join(
            f"{'用户' if message.get('role') == 'user' else '助手'}：{message.get('content', '')[:2500]}"
            for message in recent_messages
        )
        project_context = f"\n\n当前项目上下文：\n{context[:7000]}" if context else ""
        try:
            answer = st.session_state.llm.generate(
                f"""请自然回复用户的最后一条消息。

最近对话：
{conversation}
{project_context}
""",
                (
                    "你是 AI GitHub Agent。你可以像通用聊天助手一样正常交流，也擅长 GitHub 项目发现、"
                    "技术分析、项目对比和学习规划。普通聊天直接回答，不要生硬地把每个问题都转成项目搜索；"
                    "只有用户明确提出寻找或推荐项目时，搜索流程才会由系统单独处理。"
                ),
                max_tokens=1200,
            )
            if answer:
                return answer
        except Exception as exc:
            return f"这次普通对话调用失败了：{exc}。你仍可以继续提出 GitHub 项目搜索或分析需求。"
    if any(word in routed["raw"].lower() for word in ("你好", "hello", "hi", "嗨")):
        return "你好！我们可以正常聊天。需要找开源项目时，直接描述目标、技术栈和经验水平，我会切换到 GitHub 推荐流程。"
    if st.session_state.search_results:
        return "当然可以继续聊。关于刚才的推荐，你也可以直接补充筛选条件、询问某个项目，或把多个项目加入侧边栏后开始对比。"
    return "可以，我们可以正常聊天。当前未配置可用的大模型时，我会优先处理 GitHub 项目搜索、介绍、对比和学习规划。"


def render_home() -> None:
    st.title("AI GitHub Agent")
    st.caption("帮助开发者发现、理解和学习 GitHub 开源项目的智能助手。")

    stats = st.session_state.kb.get_statistics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("收藏项目", stats["favorites_count"])
    c2.metric("学习记录", stats["learning_records"])
    c3.metric("问答记录", stats["qa_count"])
    c4.metric("学习笔记", stats["notes_count"])

    st.subheader("快速开始")
    keyword = st.text_input("输入技术关键词", value="LangGraph", placeholder="Spring AI / RAG / MCP / FastAPI")
    if st.button("搜索项目", type="primary"):
        st.session_state.quick_keyword = keyword
        st.session_state.search_results = []
        st.rerun()

    st.subheader("推荐方向")
    cols = st.columns(4)
    for idx, topic in enumerate(["AI Agent", "LangGraph", "RAG", "MCP", "Spring AI", "OCR", "LLM", "FastAPI"]):
        with cols[idx % 4]:
            if st.button(topic, use_container_width=True):
                st.session_state.quick_keyword = topic
                st.session_state.search_results = []
                st.rerun()


def render_search() -> None:
    st.header("项目搜索与推荐")
    default_keyword = st.session_state.pop("quick_keyword", "")
    with st.form("search_form"):
        c1, c2, c3, c4 = st.columns([3, 1.2, 1.2, 1])
        keyword = c1.text_input("关键词", value=default_keyword, placeholder="LangGraph / RAG / MCP / Spring AI")
        language = c2.selectbox("语言", ["All", "Python", "Java", "Go", "Rust", "TypeScript", "JavaScript"])
        sort = c3.selectbox("排序", ["stars", "forks", "updated"])
        per_page = c4.slider("数量", 5, 20, config.SEARCH_PER_PAGE)
        submitted = st.form_submit_button("搜索", type="primary")

    if submitted and keyword.strip():
        with st.spinner("正在搜索 GitHub..."):
            try:
                repos = st.session_state.github.search_repos(keyword, language=language, sort=sort, per_page=per_page)
            except GitHubAPIError as exc:
                st.error(f"GitHub 搜索失败：{exc}")
                return
        st.session_state.search_results = repos
        st.success(f"找到 {len(st.session_state.search_results)} 个项目")

    if st.session_state.search_results:
        st.subheader("推荐结果")
        for idx, repo in enumerate(st.session_state.search_results):
            render_repo_card(repo, idx)


def render_repo_card(repo: Dict[str, Any], idx: int) -> None:
    analyzer = st.session_state.analyzer
    score = analyzer.recommendation_score(repo)
    reason = rule_recommendation(repo, score)
    with st.container():
        c1, c2 = st.columns([4, 1.2])
        with c1:
            st.markdown(f"<div class='repo-title'><a href='{repo.get('html_url')}'>{repo.get('full_name')}</a></div>", unsafe_allow_html=True)
            st.write(repo.get("description") or "暂无描述")
        with c2:
            st.metric("推荐指数", f"{score}/10")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Stars", repo.get("stargazers_count", 0))
        m2.metric("Forks", repo.get("forks_count", 0))
        m3.metric("语言", repo.get("language") or "Unknown")
        m4.metric("更新", (repo.get("updated_at") or "")[:10])
        st.write(f"推荐理由: {reason}")
        b1, b2, b3 = st.columns([1, 1, 4])
        if b1.button("分析", key=f"analyze_{idx}"):
            st.session_state.current_repo = repo
            st.session_state.analysis = None
            st.rerun()
        if b2.button("收藏", key=f"fav_{idx}"):
            st.session_state.kb.add_favorite(repo)
            st.toast("已收藏")


def render_analysis() -> None:
    st.header("项目分析")
    default_repo = ""
    if st.session_state.current_repo:
        default_repo = st.session_state.current_repo.get("full_name", "")
    repo_input = st.text_input("GitHub Repository", value=default_repo, placeholder="owner/repo 或 GitHub URL")

    c1, c2, c3 = st.columns([1, 1, 4])
    analyze = c1.button("开始分析", type="primary")
    load_issues = c2.checkbox("含 Issues/PR", value=False)

    if analyze and repo_input:
        run_analysis(repo_input, load_issues=load_issues)

    if st.session_state.analysis:
        show_analysis(st.session_state.analysis)


def run_analysis(repo_input: str, load_issues: bool = False) -> bool:
    full_name = st.session_state.github.normalize_repo_name(repo_input)
    if not full_name:
        st.error("请输入正确格式，例如 langchain-ai/langgraph")
        st.session_state.analysis = None
        return False

    with st.spinner("正在获取仓库、README、目录结构和技术栈..."):
        try:
            repo = st.session_state.github.get_repo(full_name)
            if not repo:
                st.error("无法获取仓库信息")
                st.session_state.analysis = None
                return False
            readme = st.session_state.github.get_readme(repo["full_name"])
            structure = st.session_state.github.get_repo_structure(
                repo["full_name"],
                branch=repo.get("default_branch"),
            )
            languages = st.session_state.github.get_languages(repo["full_name"])
            releases = st.session_state.github.get_releases(repo["full_name"])
            topics = st.session_state.github.get_topics(repo["full_name"])
            issues = st.session_state.github.get_issues(repo["full_name"]) if load_issues else []
            prs = st.session_state.github.get_pull_requests(repo["full_name"]) if load_issues else []
        except GitHubAPIError as exc:
            st.error(f"GitHub 数据获取失败：{exc}")
            st.session_state.analysis = None
            return False

        analyzer = st.session_state.analyzer
        tech_stack = analyzer.detect_tech_stack(repo, languages, structure, readme)
        modules = analyzer.identify_core_modules(structure)
        directories = analyzer.summarize_structure(structure)
        key_files = analyzer.key_files_for_learning(structure)
        learning_path = st.session_state.learning.generate(repo, tech_stack, key_files)
        context = analyzer.build_context(repo, readme, structure, tech_stack, modules)

    readme_report = ""
    if readme and st.session_state.llm.is_ready():
        with st.spinner("正在生成 README 智能分析..."):
            try:
                readme_report = st.session_state.llm.analyze_readme(repo, readme)
            except Exception as exc:
                readme_report = f"LLM 分析失败: {exc}"
    if not readme_report:
        readme_report = fallback_readme_report(repo, readme)

    st.session_state.current_repo = repo
    st.session_state.analysis = {
        "repo": repo,
        "readme": readme,
        "readme_report": readme_report,
        "structure": structure,
        "directories": directories,
        "languages": languages,
        "tech_stack": tech_stack,
        "modules": modules,
        "key_files": key_files,
        "learning_path": learning_path,
        "context": context,
        "releases": releases,
        "topics": topics,
        "issues": issues,
        "prs": prs,
    }
    st.session_state.kb.add_learning_record(repo["full_name"], "analyze", {"items": len(structure)})
    return True


def show_analysis(analysis: Dict[str, Any]) -> None:
    repo = analysis["repo"]
    st.subheader(repo["full_name"])
    st.caption(repo.get("description") or "")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stars", repo.get("stargazers_count", 0))
    c2.metric("Forks", repo.get("forks_count", 0))
    c3.metric("语言", repo.get("language") or "Unknown")
    c4.metric("License", (repo.get("license") or {}).get("name", "Unknown"))

    if st.button("保存到知识库"):
        st.session_state.kb.add_favorite(repo, analysis["readme_report"])
        st.success("已保存到收藏和知识库")

    tabs = st.tabs(["README", "项目结构", "技术栈", "学习路线", "核心代码", "元数据"])
    with tabs[0]:
        st.markdown(analysis["readme_report"])
    with tabs[1]:
        st.dataframe(analysis["directories"], use_container_width=True, hide_index=True)
        with st.expander("完整目录样本"):
            st.code("\n".join(item.get("path", "") for item in analysis["structure"][:160]))
    with tabs[2]:
        show_tech_stack(analysis["tech_stack"])
    with tabs[3]:
        st.dataframe(analysis["learning_path"], use_container_width=True, hide_index=True)
    with tabs[4]:
        modules = analysis["modules"]
        if modules:
            st.dataframe(modules, use_container_width=True, hide_index=True)
        else:
            st.info("暂未识别到明显核心模块。")
        st.write(st.session_state.analyzer.architecture_summary(repo, modules))
        if st.button("生成 AI 架构报告"):
            if not st.session_state.llm.is_ready():
                st.warning("当前 LLM 未配置 API key。")
            else:
                with st.spinner("正在生成架构分析..."):
                    report = st.session_state.llm.analyze_architecture(analysis["context"])
                st.markdown(report)
    with tabs[5]:
        st.write("Topics:", ", ".join(analysis["topics"]) or "无")
        st.write("Releases:", len(analysis["releases"]))
        st.write("Open Issues:", len(analysis["issues"]))
        st.write("Open Pull Requests:", len(analysis["prs"]))


def show_tech_stack(tech_stack: Dict[str, List[str]]) -> None:
    rows = [{"类别": key, "技术": ", ".join(values) if values else "未识别"} for key, values in tech_stack.items()]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.markdown("### 技术栈分析报告")
    for key, values in tech_stack.items():
        if values:
            st.write(f"- {key}: {', '.join(values)}")


def render_qa() -> None:
    st.header("AI 问答")
    repo_name = st.text_input(
        "当前项目",
        value=(st.session_state.current_repo or {}).get("full_name", ""),
        placeholder="先在项目分析页加载项目，或输入 owner/repo",
    )

    presets = [
        "这个项目解决什么问题？",
        "如何启动项目？",
        "Agent 是如何工作的？",
        "Workflow 在哪里？",
        "Prompt 在哪个文件？",
        "RAG 是如何实现的？",
        "哪些代码最值得阅读？",
        "适合新手学习吗？",
    ]
    cols = st.columns(4)
    for idx, question in enumerate(presets):
        if cols[idx % 4].button(question, use_container_width=True):
            st.session_state.qa_question = question

    question = st.text_area("你的问题", value=st.session_state.get("qa_question", ""), height=110)
    if st.button("提问", type="primary") and question.strip():
        if not repo_name:
            st.warning("请先选择一个项目。")
            return
        ensure_context(repo_name)
        analysis = st.session_state.analysis
        context = analysis["context"] if analysis else ""
        if not st.session_state.llm.is_ready():
            answer = fallback_answer(question, analysis)
        else:
            with st.spinner("正在结合 README 和源码结构回答..."):
                try:
                    answer = st.session_state.llm.answer_question(question, context)
                except Exception as exc:
                    answer = f"LLM 调用失败: {exc}\n\n{fallback_answer(question, analysis)}"
        st.session_state.kb.add_qa_record(repo_name, question, answer)
        st.markdown(answer)

    if repo_name:
        records = st.session_state.kb.get_qa_records(repo_name, limit=8)
        if records:
            st.subheader("历史问答")
            for record in records:
                with st.expander(record["question"]):
                    st.markdown(record["answer"])


def ensure_context(repo_name: str) -> None:
    current = (st.session_state.current_repo or {}).get("full_name")
    if st.session_state.analysis and current == repo_name:
        return
    run_analysis(repo_name, load_issues=False)


def render_compare() -> None:
    st.header("项目对比")
    text = st.text_area(
        "输入要对比的仓库，每行一个",
        value="langchain-ai/langgraph\ncrewAIInc/crewAI",
        height=120,
    )
    if st.button("开始对比", type="primary"):
        repos = []
        with st.spinner("正在获取项目数据..."):
            try:
                for line in text.splitlines():
                    full_name = st.session_state.github.normalize_repo_name(line)
                    if full_name:
                        repo = st.session_state.github.get_repo(full_name)
                        if repo:
                            repos.append(repo)
            except GitHubAPIError as exc:
                st.error(f"GitHub 数据获取失败：{exc}")
                return
        st.session_state.compare_repos = repos

    repos = st.session_state.compare_repos
    if repos:
        st.markdown(format_compare_table(repos), unsafe_allow_html=True)
        if st.button("生成 AI 对比报告"):
            if not st.session_state.llm.is_ready():
                st.warning("当前 LLM 未配置 API key。")
            else:
                with st.spinner("正在生成对比报告..."):
                    report = st.session_state.llm.compare_repos(repos)
                st.markdown(report)


def render_favorites() -> None:
    st.header("我的收藏")
    favorites = st.session_state.kb.get_favorites()
    if not favorites:
        st.info("暂无收藏项目。")
        return

    for idx, fav in enumerate(favorites):
        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### [{fav['full_name']}]({fav.get('html_url') or ''})")
                st.write(fav.get("description") or "暂无描述")
                st.caption(f"收藏时间: {fav.get('added_at')} | 阅读次数: {fav.get('view_count', 0)}")
            with c2:
                if st.button("分析", key=f"favorite_analyze_{idx}"):
                    st.session_state.kb.mark_viewed(fav["full_name"])
                    run_analysis(fav["full_name"])
                    st.rerun()
                if st.button("取消收藏", key=f"favorite_remove_{idx}"):
                    st.session_state.kb.remove_favorite(fav["full_name"])
                    st.rerun()
            notes = st.text_area("学习笔记", value=fav.get("notes") or "", key=f"note_{idx}", height=90)
            if st.button("保存笔记", key=f"save_note_{idx}"):
                st.session_state.kb.update_notes(fav["full_name"], notes)
                st.success("笔记已保存")
            if fav.get("analysis_report"):
                with st.expander("分析报告"):
                    st.markdown(fav["analysis_report"])

    st.subheader("学习记录")
    st.dataframe(st.session_state.kb.get_learning_records(), use_container_width=True, hide_index=True)


def render_daily() -> None:
    st.header("每日项目推荐")
    category = st.selectbox(
        "推荐类型",
        ["今日热门项目", "AI 新项目", "Star 增长最快项目", "Agent 项目", "RAG 项目", "Spring AI 项目"],
    )
    if st.button("获取推荐", type="primary"):
        with st.spinner("正在扫描 GitHub..."):
            try:
                st.session_state.daily_repos = st.session_state.github.daily_recommendations(category)
            except GitHubAPIError as exc:
                st.error(f"GitHub 推荐获取失败：{exc}")
                return

    repos = st.session_state.get("daily_repos", [])
    if repos:
        for idx, repo in enumerate(repos):
            render_repo_card(repo, idx + 1000)
        if st.button("生成 GitHub Daily Report"):
            if st.session_state.llm.is_ready():
                with st.spinner("正在生成日报..."):
                    report = st.session_state.llm.daily_report(repos, category)
            else:
                report = fallback_daily_report(repos, category)
            st.markdown(report)
            st.download_button("下载 Markdown", report, file_name="github_daily_report.md")


PROJECT_ALIASES = {
    "langchain": "langchain-ai/langchain",
    "langgraph": "langchain-ai/langgraph",
    "crewai": "crewAIInc/crewAI",
    "crew ai": "crewAIInc/crewAI",
    "autogen": "microsoft/autogen",
    "auto gen": "microsoft/autogen",
    "spring ai": "spring-projects/spring-ai",
    "llamaindex": "run-llama/llama_index",
    "llama index": "run-llama/llama_index",
}


def render_recommendation_artifact(artifact: Dict[str, Any]) -> None:
    repos = artifact.get("repos", [])
    if not repos:
        return

    st.markdown(
        f"""
        <div class="recommendation-heading">
            <span>推荐项目</span>
            <span class="recommendation-count">第 {artifact.get('page', 1)} 批 · {len(repos)} 个</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_names = {
        repo.get("full_name") for repo in st.session_state.get("compare_repos", [])
    }
    artifact_id = artifact.get("id", f"repos_{artifact.get('page', 1)}")
    for idx, repo in enumerate(repos, start=1):
        score = st.session_state.analyzer.recommendation_score(repo)
        repo_name_raw = repo.get("full_name") or ""
        repo_name = html.escape(repo_name_raw)
        repo_desc = html.escape(repo.get("description") or "暂无项目介绍")
        repo_url = html.escape(repo.get("html_url") or f"https://github.com/{repo_name_raw}")
        technologies = repo_technologies(repo)
        tech_chips = "".join(
            f'<span class="repo-chip">{html.escape(technology)}</span>'
            for technology in technologies
        )
        reason = html.escape(rule_recommendation(repo, score))
        updated = (repo.get("pushed_at") or repo.get("updated_at") or "")[:10]
        st.markdown(
            f"""
            <a class="repo-card-link" href="{repo_url}" target="_blank" rel="noopener noreferrer">
                <div class="repo-card">
                    <div class="repo-title">
                        <span class="repo-rank">{idx}</span>
                        <span>{repo_name}</span>
                        <span class="repo-open-mark">↗</span>
                    </div>
                    <div class="repo-desc">{repo_desc}</div>
                    <div class="repo-tech-label">用到技术</div>
                    <div class="repo-meta">{tech_chips}</div>
                    <div class="repo-meta">
                        <span class="repo-chip">GitHub Stars {format_count(repo.get('stargazers_count', 0))}</span>
                        <span class="repo-chip">最近更新 {html.escape(updated or '未知')}</span>
                        <span class="repo-score">评分 {score}/10</span>
                    </div>
                    <div class="repo-reason">{reason}</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )
        is_selected = repo_name_raw in selected_names
        learn_col, compare_col, _ = st.columns([1.45, 1.15, 3.2])
        learn_col.button(
            "启动学习计划",
            key=f"chat_plan_{artifact_id}_{idx}",
            use_container_width=True,
            on_click=start_learning_plan,
            args=(repo_name_raw,),
        )
        compare_col.button(
            "已加入对比" if is_selected else "加入对比",
            key=f"chat_compare_{artifact_id}_{idx}",
            use_container_width=True,
            disabled=is_selected,
            on_click=add_compare_repo,
            args=(repo,),
        )


def rank_recommendations(repos: List[Dict[str, Any]], user_need: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    need = user_need.lower()
    ranked = []
    for repo in repos:
        score = st.session_state.analyzer.recommendation_score(repo)
        text = f"{repo.get('full_name', '')} {repo.get('description') or ''}".lower()
        for token in need.split():
            if len(token) > 2 and token in text:
                score += 0.25
        if filters.get("difficulty") == "入门":
            size = repo.get("size", 0) or 0
            if size < 30000:
                score += 0.6
            if repo.get("has_wiki") or repo.get("homepage"):
                score += 0.2
        if repo.get("license"):
            score += 0.2
        if repo.get("pushed_at") or repo.get("updated_at"):
            score += 0.1
        ranked.append((score, repo))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [repo for _, repo in ranked]


def format_recommendations(
    repos: List[Dict[str, Any]],
    query: str,
    filters: Dict[str, Any],
    page: int,
) -> str:
    top = repos[0]
    filter_text = format_search_filters(filters)
    batch_text = f"这是第 {page} 批结果。" if page > 1 else ""
    safe_query = html.escape(query)
    safe_top_name = html.escape(top.get("full_name") or "")
    safe_top_description = html.escape(top.get("description") or "暂无描述")
    return (
        f"我按 **{safe_query}** 为你整理了 **{len(repos)} 个** GitHub 项目"
        f"{filter_text}。{batch_text}\n\n"
        f"本轮首选是 **{safe_top_name}**：{safe_top_description}\n\n"
        "点击任意项目主卡片可打开 GitHub 详情页；也可以直接启动学习计划或加入侧边栏对比。"
        "你还可以继续说“只看 TypeScript”“Stars 至少 1000”或“换一批”。"
    )


def format_search_filters(filters: Dict[str, Any]) -> str:
    labels = []
    if filters.get("language"):
        labels.append(str(filters["language"]))
    if filters.get("min_stars"):
        labels.append(f"Stars ≥ {filters['min_stars']}")
    if filters.get("recent"):
        labels.append("近半年活跃")
    if filters.get("license"):
        labels.append(str(filters["license"]).upper())
    if filters.get("difficulty"):
        labels.append(str(filters["difficulty"]))
    return f"（筛选：{html.escape('、'.join(labels))}）" if labels else ""


def repo_technologies(repo: Dict[str, Any]) -> List[str]:
    technologies: List[str] = []
    language = repo.get("language")
    if language:
        technologies.append(str(language))
    for topic in repo.get("topics") or []:
        label = str(topic).strip()
        if label and label.lower() not in {item.lower() for item in technologies}:
            technologies.append(label)
        if len(technologies) >= 5:
            break
    return technologies or ["技术栈待分析"]


def resolve_repos_from_route(routed: Dict[str, Any]) -> List[Dict[str, Any]]:
    repos = []
    cached_repos = list(st.session_state.get("compare_repos", [])) + list(
        st.session_state.get("search_results", [])
    )
    cached_by_name = {
        (repo.get("full_name") or "").lower(): repo
        for repo in cached_repos
        if repo.get("full_name")
    }
    for repo_name in routed.get("repos", []):
        repo = cached_by_name.get(repo_name.lower()) or st.session_state.github.resolve_repo(repo_name)
        if repo:
            repos.append(repo)
    if routed.get("indexes"):
        repos.extend(repos_from_indexes(routed["indexes"]))
    if not repos:
        for name in candidate_project_names(routed["raw"]):
            repo = st.session_state.github.resolve_repo(name)
            if repo:
                repos.append(repo)
    unique = []
    seen = set()
    for repo in repos:
        full_name = repo.get("full_name")
        if full_name and full_name not in seen:
            seen.add(full_name)
            unique.append(repo)
    return unique


def resolve_single_repo(routed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    repos = resolve_repos_from_route(routed)
    if repos:
        return repos[0]
    current = st.session_state.chat_memory.get("current_repo")
    if current:
        return st.session_state.github.resolve_repo(current)
    if st.session_state.current_repo:
        return st.session_state.current_repo
    return None


def repos_from_indexes(indexes: List[int]) -> List[Dict[str, Any]]:
    repos = st.session_state.search_results or st.session_state.chat_memory.get("last_repos", [])
    selected = []
    for index in indexes:
        if 1 <= index <= len(repos):
            selected.append(repos[index - 1])
    return selected


def candidate_project_names(text: str) -> List[str]:
    lowered = text.lower()
    names = []
    for alias, full_name in PROJECT_ALIASES.items():
        if alias in lowered:
            names.append(full_name)
    cleaned = text
    for token in ["对比", "比较", "介绍", "分析", "一下", "和", "与", "以及", "哪个", "更适合", "项目"]:
        cleaned = cleaned.replace(token, " ")
    for part in cleaned.replace("，", " ").replace(",", " ").replace("、", " ").split():
        if "/" in part:
            names.append(part)
        elif re_like_project_name(part):
            names.append(part)
    return names


def re_like_project_name(value: str) -> bool:
    if len(value) < 3:
        return False
    lowered = value.lower()
    blocked = {"github", "agent", "rag", "python", "java", "typescript", "react", "项目"}
    return lowered not in blocked and any(ch.isalpha() for ch in value)


def add_compare_repo(repo: Dict[str, Any]) -> None:
    current = st.session_state.compare_repos
    if not any(item.get("full_name") == repo.get("full_name") for item in current):
        current.append(repo)


def format_compare_table(repos: List[Dict[str, Any]]) -> str:
    if not repos:
        return ""

    body_rows = []
    for repo in repos:
        repo_name = html.escape(repo.get("full_name") or "Unknown")
        repo_url = html.escape(repo.get("html_url") or "#")
        repo_desc = html.escape(repo.get("description") or "暂无描述")
        stars = html.escape(format_count(repo.get("stargazers_count", 0)))
        score = st.session_state.analyzer.recommendation_score(repo)
        technology_chips = "".join(
            f'<span class="compare-chip">{html.escape(item)}</span>'
            for item in repo_technologies(repo)
        )
        body_rows.append(
            f'<tr>'
            f'<td><div class="compare-repo-name"><a href="{repo_url}" target="_blank" '
            f'rel="noopener noreferrer">{repo_name}</a></div></td>'
            f'<td><div class="compare-cell">{repo_desc}</div></td>'
            f'<td><div class="compare-chip-row">{technology_chips}</div></td>'
            f'<td><div class="compare-cell">{stars}</div></td>'
            f'<td><span class="compare-score">{score}/10</span></td>'
            f'</tr>'
        )

    easiest = min(repos, key=lambda repo: (repo.get("size", 0) or 0))
    hottest = max(repos, key=lambda repo: repo.get("stargazers_count", 0) or 0)
    return (
        '<div class="compare-card">'
        '<div class="compare-card-head">'
        '<div>'
        '<div class="compare-card-title">项目对比表格</div>'
        '<div class="compare-card-subtitle">基于 GitHub 公开元数据生成，适合做学习选型和初筛。</div>'
        '</div>'
        f'<div class="compare-card-count">{len(repos)} 个项目</div>'
        '</div>'
        '<div class="compare-table-wrap">'
        '<table class="compare-table">'
        '<thead><tr>'
        '<th>项目</th>'
        '<th>简介</th>'
        '<th>技术</th>'
        '<th>GitHub Stars</th>'
        '<th>评分</th>'
        '</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        '</table>'
        '</div>'
        '<div class="compare-recommendation">'
        f'<b>推荐选择：</b>新手优先看 <b>{html.escape(easiest.get("full_name") or "")}</b>；'
        f'看重社区热度优先评估 <b>{html.escape(hottest.get("full_name") or "")}</b>。'
        '生产使用前继续复核 Release、Issue 响应、License 和依赖生态。'
        '</div>'
        '</div>'
    )


def format_project_intro(analysis: Dict[str, Any]) -> str:
    repo = analysis["repo"]
    tech = ", ".join(
        item for values in analysis["tech_stack"].values() for item in values
    ) or (repo.get("language") or "Unknown")
    dirs = "\n".join(f"- `{row['目录']}`：{row['说明']}" for row in analysis["directories"][:8]) or "- 未获取到目录结构"
    modules = "\n".join(f"- {row['模块']}：{row['文件']}" for row in analysis["modules"][:8]) or "- 暂未识别明显核心模块"
    return f"""
## {repo.get('full_name')} 项目介绍

### 一句话总结
{repo.get('description') or '该项目暂无 GitHub description，需要结合 README 继续确认定位。'}

### 项目概述
- Stars / Forks：{repo.get('stargazers_count', 0)} / {repo.get('forks_count', 0)}
- 主要语言：{repo.get('language') or 'Unknown'}
- License：{(repo.get('license') or {}).get('name', 'Unknown')}
- 最近更新：{(repo.get('pushed_at') or repo.get('updated_at') or '')[:10]}

### 技术栈
{tech}

### 目录结构解读
{dirs}

### 关键模块
{modules}

### 优势
- 有公开仓库数据可追踪，便于学习和选型。
- 可以从 README、入口文件、配置和核心模块逐层阅读。

### 局限或风险
- README 质量、Release 节奏、Issue 响应和 License 需要继续核实。
- AI 总结不能替代安全审计或商业合规审查。

### 快速上手建议
1. 先读 README 并跑通最小示例。
2. 查看配置文件和入口文件。
3. 沿核心模块阅读主调用链。
4. 做一个小功能改造并记录学习笔记。
"""


def format_learning_plan(analysis: Dict[str, Any], period: str, level: str) -> str:
    repo = analysis["repo"]
    steps = analysis["learning_path"]
    if period == "3 天":
        phases = ["第 1 天：运行和理解 README", "第 2 天：阅读入口与核心模块", "第 3 天：完成小改造并总结"]
    elif period == "2 周":
        phases = [
            "第 1-2 天：读 README、安装依赖、跑通示例",
            "第 3-4 天：阅读入口文件和配置文件",
            "第 5-7 天：阅读核心业务模块并画出调用链",
            "第 8-10 天：阅读 Workflow / Prompt / Tool / RAG 等关键能力",
            "第 11-13 天：完成一个二次开发小功能",
            "第 14 天：整理技术笔记和复盘",
        ]
    else:
        phases = ["阶段 1：运行项目", "阶段 2：阅读核心模块", "阶段 3：实践改造", "阶段 4：总结输出"]

    step_lines = "\n".join(
        f"- {row['步骤']}：{row['目标']}（重点：`{row['重点文件']}`）"
        for row in steps
    )
    phase_lines = "\n".join(f"- {phase}" for phase in phases)
    return f"""
## {repo.get('full_name')} 学习规划

- 学习周期：{period}
- 用户水平：{level}
- 学习目标：从运行项目到理解核心结构，再完成一个小功能改造。

### 分阶段计划
{phase_lines}

### 推荐阅读路线
{step_lines}

### 实践任务
- 跑通官方示例或最小 Demo。
- 记录项目结构和核心调用链。
- 修改一个配置、Prompt、Tool、API 或示例流程。
- 输出一篇学习笔记或技术分享。

### 最终产出
- 可运行 Demo
- 项目结构笔记
- 核心流程图
- 一个二次开发小功能
"""


def activity_level(repo: Dict[str, Any]) -> str:
    pushed = (repo.get("pushed_at") or repo.get("updated_at") or "")[:10]
    issues = repo.get("open_issues_count", 0) or 0
    if not pushed:
        return "未知"
    if issues > 0:
        return f"较活跃，最近更新 {pushed}"
    return f"最近更新 {pushed}"


def doc_quality(repo: Dict[str, Any]) -> str:
    if repo.get("has_pages") or repo.get("homepage"):
        return "较好，有主页或文档入口"
    if repo.get("description"):
        return "中等，可先读 README"
    return "信息较少"


def risk_summary(repo: Dict[str, Any]) -> str:
    risks = []
    if not repo.get("license"):
        risks.append("License 不清晰")
    if (repo.get("open_issues_count", 0) or 0) > 500:
        risks.append("Issue 较多")
    if not risks:
        risks.append("需复核维护节奏")
    return "、".join(risks)


def format_count(value: Any) -> str:
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return "0"
    if number >= 1000000:
        return f"{number / 1000000:.1f}M"
    if number >= 1000:
        return f"{number / 1000:.1f}K"
    return str(number)


def fallback_readme_report(repo: Dict[str, Any], readme: str) -> str:
    description = repo.get("description") or "README 暂无足够描述。"
    readme_preview = readme[:1200] if readme else "未获取到 README。"
    return f"""
## 3 分钟读懂该项目

### 项目简介
{description}

### 项目解决的问题
根据仓库描述和 README，该项目面向 `{repo.get('full_name')}` 相关场景，具体细节建议继续阅读 README 和核心目录。

### 核心功能
- 提供开源项目中的主要能力实现
- 包含可学习的工程结构和技术选型
- 可结合源码进一步分析入口、配置和核心模块

### 技术特点
主要语言: {repo.get('language') or 'Unknown'}

### 安装步骤 / 快速开始 / 使用方式 / 注意事项
以下是 README 摘录:

```text
{readme_preview}
```
"""


def fallback_answer(question: str, analysis: Optional[Dict[str, Any]]) -> str:
    if not analysis:
        return "当前没有足够项目上下文。请先在项目分析页加载仓库。"
    modules = analysis.get("modules", [])
    files = "\n".join(f"- {row['模块']}: {row['文件']}" for row in modules[:8]) or "暂未识别到核心文件。"
    return f"""
基于当前已获取的 README 和目录结构，可以先这样判断:

{analysis.get('repo', {}).get('description') or '该项目暂无描述。'}

相关核心文件:
{files}

你的问题是: {question}

当前未启用 LLM，因此这是规则分析结果。配置 API key 后可以得到更深入的自然语言回答。
"""


def fallback_daily_report(repos: List[Dict[str, Any]], category: str) -> str:
    lines = [f"# GitHub Daily Report - {category}", "", "## 今日推荐"]
    for idx, repo in enumerate(repos[:10], start=1):
        lines.append(
            f"{idx}. [{repo.get('full_name')}]({repo.get('html_url')}) - "
            f"{repo.get('description') or '暂无描述'} "
            f"({repo.get('stargazers_count', 0)} stars)"
        )
    lines.append("\n## 学习建议\n优先选择 README 清晰、最近仍在更新、示例和测试完整的项目。")
    return "\n".join(lines)


def rule_recommendation(repo: Dict[str, Any], score: float) -> str:
    stars = repo.get("stargazers_count", 0) or 0
    updated = (repo.get("updated_at") or "")[:10]
    language = repo.get("language") or "Unknown"
    if score >= 8:
        return f"社区关注度高，{language} 技术栈清晰，最近更新于 {updated}，适合作为重点学习对象。"
    if stars > 100:
        return f"已有一定社区基础，适合用于了解 {language} 方向的工程实践。"
    return f"项目体量可能较轻，适合作为快速浏览或专项学习素材。"


def difficulty(repo: Dict[str, Any]) -> str:
    stars = repo.get("stargazers_count", 0) or 0
    size = repo.get("size", 0) or 0
    if size > 80000 or stars > 50000:
        return "较高"
    if size > 15000 or stars > 5000:
        return "中等"
    return "较低"


if __name__ == "__main__":
    main()
