#!/usr/bin/env python3
"""Small structural check for generated Yuque Lakeboard files."""

import json
import sys
from pathlib import Path


def main() -> None:
    path = Path(sys.argv[1])
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["format"] == "lakeboard"
    assert doc["type"] == "Board"
    body = doc["diagramData"]["body"]

    def descendants(item: dict):
        yield item
        for child in item.get("children", []):
            yield from descendants(child)

    all_items = [nested for item in body for nested in descendants(item)]
    ids = [item["id"] for item in all_items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    top_level = {item["id"] for item in body}
    for item in body:
        if item["type"] == "line":
            assert item["source"]["id"] in top_level, f"missing source: {item['id']}"
            assert item["target"]["id"] in top_level, f"missing target: {item['id']}"

    positioned = [
        item
        for item in body
        if all(isinstance(item.get(key), (int, float)) for key in ("x", "y"))
    ]
    boxes = [
        item
        for item in positioned
        if all(isinstance(item.get(key), (int, float)) for key in ("x", "y", "width", "height"))
    ]
    assert positioned, "no positioned items"
    bbox = doc["graphicsBBox"]
    assert bbox["x"] <= min(item["x"] for item in positioned)
    assert bbox["y"] <= min(item["y"] for item in positioned)
    assert bbox["x"] + bbox["width"] >= max(item["x"] for item in positioned)
    assert bbox["y"] + bbox["height"] >= max(item["y"] for item in positioned)
    if boxes:
        assert bbox["x"] + bbox["width"] >= max(item["x"] + item["width"] for item in boxes)
        assert bbox["y"] + bbox["height"] >= max(item["y"] + item["height"] for item in boxes)

    print(
        f"ok: {len(body)} items, "
        f"{sum(item['type'] == 'geometry' for item in body)} geometries, "
        f"{sum(item['type'] == 'line' for item in body)} lines"
    )


if __name__ == "__main__":
    main()
