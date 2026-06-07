# services/chatwoot_api.py
# Semua fungsi untuk hit Chatwoot API

import requests
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

from config.settings import (
    CHATWOOT_BASE_URL,
    CHATWOOT_API_TOKEN,
    CHATWOOT_ACCOUNT_ID,
    CONVERSATION_STATUSES,
    TYPE_MAPPING
)

HEADERS = {
    "api_access_token": CHATWOOT_API_TOKEN,
    "Content-Type": "application/json"
}

# =====================
# CONVERSATIONS
# =====================

def get_conversations_by_status(status, date_from=None, date_to=None):
    """Ambil semua conversation by status dengan pagination + filter tanggal"""
    all_conversations = []
    page              = 1
    stop_pagination   = False

    while not stop_pagination:
        response = requests.get(
            CHATWOOT_BASE_URL + "/api/v1/accounts/" + str(CHATWOOT_ACCOUNT_ID) + "/conversations",
            headers=HEADERS,
            params={"page": page, "status": status},
            timeout=30
        )

        if response.status_code != 200:
            print("[GAGAL] Status " + status + " page " + str(page) + " -> HTTP " + str(response.status_code))
            break

        data          = response.json()
        conversations = data.get("data", {}).get("payload", [])

        if not conversations:
            break

        for conv in conversations:
            created_at = conv.get("created_at")
            if created_at:
                conv_date = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d")
                if date_from and conv_date < date_from:
                    stop_pagination = True
                    continue
                if date_to and conv_date > date_to:
                    continue
            all_conversations.append(conv)

        page += 1

    return all_conversations

def get_all_conversations(date_from=None, date_to=None):
    """Ambil semua conversation dari semua status dalam date range"""
    all_conversations = []

    for status in CONVERSATION_STATUSES:
        print("[INFO] Fetching status: " + status + "...")
        convs = get_conversations_by_status(status, date_from, date_to)
        print("[INFO] -> " + str(len(convs)) + " conversations")
        for conv in convs:
            conv["_status"] = status
        all_conversations.extend(convs)

    all_conversations.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return all_conversations

# =====================
# MESSAGES
# =====================

def get_messages(conversation_id):
    """Ambil semua messages dari 1 conversation"""
    response = requests.get(
        CHATWOOT_BASE_URL + "/api/v1/accounts/" + str(CHATWOOT_ACCOUNT_ID) + "/conversations/" + str(conversation_id) + "/messages",
        headers=HEADERS,
        timeout=10
    )
    if response.status_code != 200:
        return []
    return response.json().get("payload", [])

# =====================
# PARSERS
# =====================

def parse_labels(labels):
    """
    Parse labels menjadi:
    - service   : dari prefix 2_xxx
    - priority  : dari p1/p2/p3/p4
    - escalate  : dari l1/l2
    - type      : dari prefix 10_xxx (pakai TYPE_MAPPING)
    - raw_labels: original CSV
    """
    service   = None
    priority  = None
    escalate  = None
    type_val  = None
    raw       = ", ".join(labels) if labels else ""

    for label in labels:
        label = label.strip().lower()

        # Service → prefix 2_
        if label.startswith("2_"):
            service = label[2:].replace("_", " ").title()

        # Priority → p1/p2/p3/p4
        elif label in ["p1", "p2", "p3", "p4"]:
            priority = label.upper()

        # Escalate → l1/l2
        elif label in ["l1", "l2"]:
            escalate = label.upper()

        # Type → prefix 10_
        elif label.startswith("10_"):
            key      = label[3:]
            type_val = TYPE_MAPPING.get(key, key.replace("_", " ").title())

    return service, priority, escalate, type_val, raw

def parse_frt(conv):
    """Hitung First Response Time dari first_reply_created_at - created_at"""
    created_at     = conv.get("created_at")
    first_reply_at = conv.get("first_reply_created_at")
    if first_reply_at and created_at:
        return int(first_reply_at - created_at)
    return None

def parse_resolution_time(messages, created_at):
    """Hitung Resolution Time dari last activity message 'resolved'"""
    resolved_messages = [
        m for m in messages
        if m.get("message_type") == 2
        and "resolved" in (m.get("content") or "").lower()
    ]
    if not resolved_messages:
        return None
    resolved_at = resolved_messages[-1].get("created_at")
    if resolved_at and created_at:
        return int(resolved_at - created_at)
    return None

def parse_resolve_count(messages):
    """Hitung berapa kali conversation di-resolve"""
    count = 0
    for m in messages:
        if m.get("message_type") == 2 and "resolved" in (m.get("content") or "").lower():
            count += 1
    return count

def parse_last_note(messages):
    """Ambil last private note"""
    private_notes = [m for m in messages if m.get("private") is True]
    if not private_notes:
        return None
    content = private_notes[-1].get("content") or ""
    content = content.replace("
", " ").replace("\r", " ").strip()
    return content if content else None

def parse_customer_info(conv):
    """Ambil info customer dari meta.sender"""
    sender  = conv.get("meta", {}).get("sender", {})
    attrs   = sender.get("additional_attributes", {})
    return {
        "company"  : attrs.get("company_name") or None,
        "customer" : sender.get("name") or None,
        "phone"    : sender.get("phone_number") or None,
    }

# =====================
# MAIN BUILDER
# =====================

def build_conversation_data(conv, messages):
    """
    Gabungkan semua data menjadi 1 dict siap simpan ke DB
    """
    created_at              = conv.get("created_at")
    labels                  = conv.get("labels", [])
    service, priority, escalate, type_val, raw_labels = parse_labels(labels)
    customer_info           = parse_customer_info(conv)
    assignee                = conv.get("meta", {}).get("assignee")
    resolve_count           = parse_resolve_count(messages)

    return {
        "ticket_id"              : conv.get("id"),
        "created_at"             : datetime.fromtimestamp(created_at) if created_at else None,
        "status"                 : conv.get("_status", conv.get("status", "")),
        "agent"                  : assignee.get("name") if assignee else None,
        "service"                : service,
        "priority"               : priority,
        "escalate"               : escalate,
        "type"                   : type_val,
        "raw_labels"             : raw_labels,
        "frt_seconds"            : parse_frt(conv),
        "resolution_time_seconds": parse_resolution_time(messages, created_at),
        "resolve_count"          : resolve_count,
        "is_reopened"            : resolve_count > 1,
        "last_note"              : parse_last_note(messages),
        "company"                : customer_info["company"],
        "customer"               : customer_info["customer"],
        "phone"                  : customer_info["phone"],
    }
