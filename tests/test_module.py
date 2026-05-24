from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "src/modules/mod_latest_content/module.py"
SPEC = importlib.util.spec_from_file_location("mod_latest_content_module", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
render = module.render


class _Result:
    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, object]]:
        return [{"title": "První článek", "slug": "prvni-clanek", "updated_at": "2026-01-01"}]


class _Db:
    async def execute(self, statement: object, params: dict[str, object] | None = None) -> _Result:
        assert params == {"limit": 3}
        return _Result()


@pytest.mark.asyncio
async def test_render_latest_content() -> None:
    html = await render(
        {
            "db": _Db(),
            "settings": '{"limit": 3, "heading": "Novinky", "content_slug": "clanky"}',
        }
    )

    assert "Novinky" in html
    assert "První článek" in html
    assert 'href="/clanky/prvni-clanek"' in html
