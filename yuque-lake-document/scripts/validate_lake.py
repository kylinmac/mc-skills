#!/usr/bin/env python3
"""Structural check for native Yuque .lake documents."""

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


class LakeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doctype = ""
        self.metas: dict[str, str] = {}
        self.ids: list[str] = []
        self.cards: list[dict[str, str]] = []

    def handle_decl(self, decl: str) -> None:
        self.doctype = decl.lower()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "meta" and values.get("name"):
            self.metas[values["name"]] = values.get("content", "")
        if values.get("data-lake-id"):
            assert values.get("id") == values["data-lake-id"], f"mismatched Lake ID: {tag}"
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "card":
            self.cards.append(values)


def decode_card(card: dict[str, str]):
    assert card.get("type") in {"block", "inline"}, "invalid card type"
    assert card.get("name"), "card name missing"
    value = card.get("value", "")
    assert value.startswith("data:"), f"card value missing data: prefix: {card['name']}"
    decoded = unquote(value[5:])
    return json.loads(decoded)


def validate_board(board: object) -> None:
    assert isinstance(board, dict), "board payload must be an object"
    assert isinstance(board.get("diagramData"), dict), "board diagramData missing"
    body = board["diagramData"].get("body")
    assert isinstance(body, list), "board body missing"
    assert board.get("viewportOption") in {"adapt", "current"}, "board viewportOption invalid"
    assert isinstance(board.get("viewportSetting"), dict), "board viewportSetting missing"
    assert isinstance(board.get("graphicsBBox"), dict), "board graphicsBBox missing"
    assert board.get("id"), "board id missing"


def main() -> None:
    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")
    parser = LakeParser()
    parser.feed(source)

    assert parser.doctype == "doctype lake", "missing <!doctype lake>"
    assert parser.metas.get("doc-version") == "1", "doc-version must be 1"
    assert parser.metas.get("viewport") == "fixed", "viewport must be fixed"
    assert len(parser.ids) == len(set(parser.ids)), "duplicate element ids"

    counts: dict[str, int] = {}
    for card in parser.cards:
        payload = decode_card(card)
        name = card["name"]
        counts[name] = counts.get(name, 0) + 1
        if name == "checkbox":
            assert isinstance(payload, bool), "checkbox payload must be boolean"
        elif name in {"hr", "codeblock"}:
            assert isinstance(payload, dict) and payload.get("id"), f"{name} card id missing"
        elif name == "board":
            validate_board(payload)

    summary = ", ".join(f"{name}={count}" for name, count in sorted(counts.items())) or "no cards"
    print(f"ok: {len(parser.ids)} element ids, {len(parser.cards)} cards ({summary})")


if __name__ == "__main__":
    main()
