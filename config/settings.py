# config/settings.py
# Load semua environment variables dan konstanta global

import os
from dotenv import load_dotenv

load_dotenv()

# =====================
# CHATWOOT API
# =====================
CHATWOOT_BASE_URL   = os.getenv("CHATWOOT_BASE_URL", "")
CHATWOOT_API_TOKEN  = os.getenv("CHATWOOT_API_TOKEN", "")
CHATWOOT_ACCOUNT_ID = int(os.getenv("CHATWOOT_ACCOUNT_ID", "1"))

# =====================
# DATABASE
# =====================
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME", "dashboard_report_csicube")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# =====================
# AUTH
# =====================
JWT_SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "change_this_secret")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "8"))

# =====================
# TYPE MAPPING (10_xxx → display name)
# =====================
TYPE_MAPPING = {
    "bug"               : "Bug",
    "he"                : "Human Error",
    "others_issue"      : "Others Issue",
    "question"          : "Question",
    "req"               : "Request",
    "system_code_issue" : "System/Code Issue",
}

# =====================
# CONVERSATION STATUSES
# =====================
CONVERSATION_STATUSES = ["open", "resolved", "pending", "snoozed"]
