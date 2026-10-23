"""Security, privacy defense-in-depth, PII redaction, and encryption at rest."""
from __future__ import annotations

import base64
import hashlib
import logging
import re
import time
from dataclasses import dataclass

from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.config import get_settings

logger = logging.getLogger("festify.security")

# 8-Pattern Comprehensive PII Regex Suite
PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "bank_account": re.compile(r"\b(?:routing|account|acct|iban)[\s#:]+[A-Za-z0-9]{6,16}\b", re.IGNORECASE),
    "street_address": re.compile(
        r"\b\d{1,5}\s+[A-Za-z0-9.\s]{3,25}\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b",
        re.IGNORECASE,
    ),
    "dob": re.compile(r"\b(?:DOB|birthdate|born)[\s:]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.IGNORECASE),
    "ip_address": re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
}

PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(?:an?\s+)?unrestricted", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?secret\s+key", re.IGNORECASE),
    re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
)


@dataclass
class RedactionResult:
    sanitized_text: str
    redaction_counts: dict[str, int]
    total_redacted: int


def redact_pii(text: str) -> RedactionResult:
    """Mask sensitive PII before text is stored or sent to any LLM."""
    counts: dict[str, int] = {}
    total = 0
    sanitized = text

    for pii_type, pattern in PII_PATTERNS.items():
        matches = pattern.findall(sanitized)
        if matches:
            counts[pii_type] = len(matches)
            total += len(matches)
            sanitized = pattern.sub(f"[REDACTED_{pii_type.upper()}]", sanitized)

    return RedactionResult(sanitized_text=sanitized, redaction_counts=counts, total_redacted=total)


def sanitize_prompt_input(text: str) -> str:
    """Sanitize user-provided prompt content against jailbreaks and instruction override attempts."""
    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = pattern.sub("[REMOVED_INSTRUCTION_OVERRIDE]", sanitized)
    return sanitized


# Fernet Symmetric Encryption at Rest
_fernet_instance: Fernet | None = None


def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is None:
        settings = get_settings()
        key = settings.encryption_key
        if not key:
            # Deterministic dev key derived from secret_key
            derived = hashlib.sha256(settings.secret_key.encode()).digest()
            key = base64.urlsafe_b64encode(derived).decode()
        _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet_instance


def encrypt_data(plaintext: str) -> str:
    """Encrypt sensitive event details or client notes using AES-128 Fernet."""
    return get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_data(ciphertext: str) -> str:
    """Decrypt ciphertext at rest."""
    return get_fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")


# Anonymous JWT Session Tokens
JWT_ALGORITHM = "HS256"


def create_session_token(session_id: str, expires_in_minutes: int = 120) -> str:
    settings = get_settings()
    expire_timestamp = time.time() + (expires_in_minutes * 60)
    payload = {
        "sub": session_id,
        "exp": int(expire_timestamp),
        "iat": int(time.time()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def verify_session_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# In-Memory Token Bucket Rate Limiting (Stateless & Fast)
_RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}


def check_rate_limit(client_id: str, limit: int = 60, window_seconds: int = 60) -> bool:
    """Token bucket rate limiter. Returns True if request is allowed, False if exceeded."""
    now = time.time()
    cutoff = now - window_seconds
    timestamps = _RATE_LIMIT_BUCKETS.setdefault(client_id, [])

    # Prune expired timestamps
    _RATE_LIMIT_BUCKETS[client_id] = [t for t in timestamps if t > cutoff]
    if len(_RATE_LIMIT_BUCKETS[client_id]) >= limit:
        return False

    _RATE_LIMIT_BUCKETS[client_id].append(now)
    return True
