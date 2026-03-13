"""
Audit service — records all significant system actions to the audit log.
"""

import datetime


def log_action(store, action: str, user: str, details: str):
    """Append an audit entry to the store's audit log."""
    store.audit_log.append({
        "timestamp": str(datetime.datetime.now()),
        "action": action,
        "user": user,
        "details": details,
    })
