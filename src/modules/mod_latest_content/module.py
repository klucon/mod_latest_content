from __future__ import annotations

import json
from html import escape

from sqlalchemy import text


def _settings(settings: str) -> dict[str, object]:
    raw = (settings or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _limit(value: object) -> int:
    try:
        number = int(str(value or "5"))
    except ValueError:
        return 5
    return min(max(number, 1), 20)


async def render(context: dict | None = None) -> str:
    context = context or {}
    db = context.get("db")
    if db is None:
        return ""

    settings = _settings(str(context.get("settings") or ""))
    limit = _limit(settings.get("limit"))
    heading = str(settings.get("heading") or "Nejnovější články").strip()
    content_slug = str(settings.get("content_slug") or "clanky").strip().strip("/") or "clanky"

    try:
        rows = (
            await db.execute(
                text(
                    "SELECT title, slug, updated_at FROM com_content_articles "
                    "WHERE status = 'published' "
                    "ORDER BY updated_at DESC, id DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
        ).mappings().all()
    except Exception:
        return ""
    if not rows:
        return ""

    parts = ['<section class="mod-latest-content">']
    if heading:
        parts.append(f'<h2 class="mod-latest-content__heading">{escape(heading)}</h2>')
    parts.append('<ul class="mod-latest-content__list">')
    for row in rows:
        title = escape(str(row["title"] or ""))
        slug = escape(str(row["slug"] or ""), quote=True)
        parts.append(
            '<li class="mod-latest-content__item">'
            f'<a class="mod-latest-content__link" href="/{escape(content_slug, quote=True)}/{slug}">'
            f"{title}</a></li>"
        )
    parts.append("</ul></section>")
    return "".join(parts)
