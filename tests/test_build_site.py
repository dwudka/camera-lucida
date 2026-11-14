import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_site as bs  # noqa: E402


def page(root: Path, name: str, **meta) -> None:
    d = root / name
    d.mkdir(parents=True)
    (d / "index.html").write_text("<h1>page</h1>")
    (d / "meta.json").write_text(json.dumps(meta))


def test_empty_site(tmp_path):
    root, out = tmp_path / "root", tmp_path / "out"
    root.mkdir()
    assert bs.build(root, out) == []
    text = (out / "index.html").read_text()
    assert "Nothing posted yet." in text and bs.DISCLAIMER in text
    assert (out / "404.html").exists()
    ET.fromstring((out / "feed.xml").read_text())


def test_lists_pages_newest_first_and_escapes(tmp_path):
    root, out = tmp_path / "root", tmp_path / "out"
    page(root, "2026-12-01-older", title="Older <read>", kind="long-read", description="A & B")
    page(root, "2026-12-08-newer", title="Newer", kind="interactive")
    (root / "scripts").mkdir()
    (root / "2026-12-09-no-meta").mkdir()
    items = bs.build(root, out)
    assert [m["slug"] for m in items] == ["2026-12-08-newer", "2026-12-01-older"]
    text = (out / "index.html").read_text()
    assert text.index("Newer") < text.index("Older &lt;read&gt;") and "A &amp; B" in text
    assert "Long read" in text and "Interactive" in text and "Dec 8, 2026" in text
    assert (out / "2026-12-01-older" / "index.html").exists() and not (out / "scripts").exists()
    feed = ET.fromstring((out / "feed.xml").read_text())
    assert [i.findtext("title") for i in feed.iter("item")] == ["Newer", "Older <read>"]
