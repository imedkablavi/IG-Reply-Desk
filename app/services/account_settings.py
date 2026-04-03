import copy
import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.all_models import Setting

OWNER_TEXTS_PREFIX = "owner_texts"
COMMENT_DM_RULES_PREFIX = "comment_dm_rules"

OWNER_TEXT_DEFAULTS = {
    "welcome_text": "👋 أهلاً بك! أنا مساعد المتجر، كيف يمكنني خدمتك؟",
    "fallback_text": "تم استلام رسالتك وسيتم الرد عليك قريباً من فريق المتجر ⏳",
    "soft_welcome_text": "أهلاً بك 👋",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\u064B-\u065F\u0640]", "", text.strip().lower())
    text = re.sub(r"[إأآ]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    return text


def _account_key(prefix: str, account_id: int) -> str:
    return f"{prefix}:{account_id}"


async def _get_json_setting(session: AsyncSession, key: str, default: Any) -> Any:
    stmt = select(Setting).where(Setting.key == key)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if not row or not row.value:
        return copy.deepcopy(default)
    try:
        return json.loads(row.value)
    except json.JSONDecodeError:
        return copy.deepcopy(default)


async def _set_json_setting(session: AsyncSession, key: str, value: Any) -> None:
    stmt = select(Setting).where(Setting.key == key)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    encoded = json.dumps(value, ensure_ascii=False)
    if row:
        row.value = encoded
    else:
        session.add(Setting(key=key, value=encoded))


def _sanitize_owner_texts(raw: dict[str, Any]) -> dict[str, str]:
    data = dict(OWNER_TEXT_DEFAULTS)
    if not isinstance(raw, dict):
        return data

    for key in OWNER_TEXT_DEFAULTS:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            data[key] = value.strip()
    return data


def _sanitize_comment_rules(raw: Any) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        return []

    seen: set[str] = set()
    rules: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        keyword = item.get("keyword")
        response = item.get("response")
        if not isinstance(keyword, str) or not isinstance(response, str):
            continue
        keyword = keyword.strip()
        response = response.strip()
        if not keyword or not response:
            continue

        normalized = normalize_text(keyword)
        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        rules.append({"keyword": keyword, "response": response})

    return rules


async def get_owner_texts(session: AsyncSession, account_id: int) -> dict[str, str]:
    key = _account_key(OWNER_TEXTS_PREFIX, account_id)
    raw = await _get_json_setting(session, key, {})
    return _sanitize_owner_texts(raw)


async def set_owner_text(session: AsyncSession, account_id: int, text_key: str, value: str) -> None:
    if text_key not in OWNER_TEXT_DEFAULTS:
        raise ValueError(f"Unsupported owner text key: {text_key}")
    if not value or not value.strip():
        raise ValueError("Owner text value cannot be empty")

    key = _account_key(OWNER_TEXTS_PREFIX, account_id)
    raw = await _get_json_setting(session, key, {})
    if not isinstance(raw, dict):
        raw = {}
    raw[text_key] = value.strip()
    await _set_json_setting(session, key, raw)


async def reset_owner_text(session: AsyncSession, account_id: int, text_key: str) -> None:
    if text_key not in OWNER_TEXT_DEFAULTS:
        raise ValueError(f"Unsupported owner text key: {text_key}")

    key = _account_key(OWNER_TEXTS_PREFIX, account_id)
    raw = await _get_json_setting(session, key, {})
    if not isinstance(raw, dict):
        raw = {}
    raw.pop(text_key, None)
    await _set_json_setting(session, key, raw)


async def get_comment_dm_rules(session: AsyncSession, account_id: int) -> list[dict[str, str]]:
    key = _account_key(COMMENT_DM_RULES_PREFIX, account_id)
    raw = await _get_json_setting(session, key, [])
    return _sanitize_comment_rules(raw)


async def upsert_comment_dm_rule(
    session: AsyncSession,
    account_id: int,
    keyword: str,
    response: str,
) -> bool:
    keyword = (keyword or "").strip()
    response = (response or "").strip()
    if not keyword or not response:
        raise ValueError("Keyword and response are required")

    key = _account_key(COMMENT_DM_RULES_PREFIX, account_id)
    rules = await get_comment_dm_rules(session, account_id)
    normalized = normalize_text(keyword)
    inserted = True

    for rule in rules:
        if normalize_text(rule["keyword"]) == normalized:
            rule["keyword"] = keyword
            rule["response"] = response
            inserted = False
            break
    else:
        rules.append({"keyword": keyword, "response": response})

    await _set_json_setting(session, key, rules)
    return inserted


async def delete_comment_dm_rule(session: AsyncSession, account_id: int, keyword: str) -> bool:
    normalized = normalize_text(keyword)
    if not normalized:
        return False

    key = _account_key(COMMENT_DM_RULES_PREFIX, account_id)
    rules = await get_comment_dm_rules(session, account_id)
    filtered = [rule for rule in rules if normalize_text(rule["keyword"]) != normalized]
    deleted = len(filtered) != len(rules)

    if deleted:
        await _set_json_setting(session, key, filtered)
    return deleted


def find_comment_dm_match(
    rules: list[dict[str, str]],
    comment_text: str,
) -> tuple[str, str] | tuple[None, None]:
    normalized_comment = normalize_text(comment_text)
    if not normalized_comment:
        return None, None

    for rule in rules:
        keyword = rule["keyword"]
        response = rule["response"]
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword and normalized_keyword in normalized_comment:
            return keyword, response

    return None, None
