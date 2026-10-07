"""Live-clock page check (web/live-clock/).

    python tools/check-web.py

- system.css and system.js are exactly what tools/build-web.py would generate from tokens.json
- every pack image the page references exists
- page structure: lang, title, viewport, skip link to #main, exactly one <h1>, alt on every <img>,
  the time slider has role/aria values, live regions exist, no <audio>/<video> autoplay with sound
- no third-party scripts (only Google Fonts stylesheets are external)
Contrast for every persona's text pairs is covered by check-contrast.py (same tokens).
"""

import importlib.util
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

WEB = tk.ROOT / "web" / "live-clock"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def main():
    r = Report("check-web", "Live-clock page check", "Static checks for `web/live-clock/`. Visual review is done with screenshots.")
    index = WEB / "index.html"
    if not index.exists():
        r.add("INFO", "live-clock page", "not built yet")
        return r.finish()
    spec = importlib.util.spec_from_file_location("build_web", Path(__file__).parent / "build-web.py")
    bw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bw)
    res = tk.resolve_all(tk.load())
    r.ok((WEB / "system.css").read_text(encoding="utf-8") == bw.css(res), "system.css matches tokens.json (run tools/build-web.py)")
    js = (WEB / "system.js").read_text(encoding="utf-8")
    import json
    data = json.loads(js[js.index("{"):js.rindex("}") + 1])
    r.ok(data == json.loads(json.dumps(bw.data(res))), "system.js matches tokens.json (run tools/build-web.py)")
    missing = [p["product"]["image"] for p in data["personas"] if not (WEB / p["product"]["image"]).exists()]
    r.ok(not missing, "every pack image the page uses exists", ", ".join(missing) or f"{len(data['personas'])} packs")

    page = Page()
    page.feed(index.read_text(encoding="utf-8"))
    tags = page.tags
    attrs_of = lambda name: [a for t, a in tags if t == name]
    html = attrs_of("html")
    r.ok(html and html[0].get("lang"), "html has a lang attribute", html[0].get("lang") if html else "")
    r.ok(bool(re.search(r"<title>[^<]+</title>", index.read_text(encoding="utf-8"))), "page has a title")
    r.ok(any(a.get("name") == "viewport" for a in attrs_of("meta")), "viewport meta present (responsive)")
    r.ok(any(a.get("href") == "#main" for a in attrs_of("a")) and any(a.get("id") == "main" for a in attrs_of("main")),
         "skip link targets <main id=\"main\">")
    r.ok(len(attrs_of("h1")) == 1, "exactly one h1", str(len(attrs_of("h1"))))
    imgs = attrs_of("img")
    r.ok(all("alt" in a for a in imgs), "every <img> has an alt attribute (set to the pack description at runtime)",
         f"{len(imgs)} images")
    slider = [a for t, a in tags if a.get("role") == "slider"]
    r.ok(slider and all(k in slider[0] for k in ("aria-valuemin", "aria-valuemax", "aria-valuenow", "aria-valuetext", "tabindex")),
         "time slider exposes role, value and keyboard focus")
    r.ok(sum(1 for _, a in tags if a.get("aria-live")) >= 2, "live regions for persona changes and sound captions")
    media = [a for t, a in tags if t in ("audio", "video")]
    r.ok(not any("autoplay" in a and "muted" not in a for a in media), "no media autoplays with sound")
    scripts = [a.get("src", "") for a in attrs_of("script")]
    r.ok(all(s and not s.startswith(("http:", "https:", "//")) for s in scripts), "only first-party scripts", ", ".join(scripts))
    css_links = [a.get("href", "") for a in attrs_of("link") if a.get("rel") == "stylesheet"]
    ext = [h for h in css_links if h.startswith("http") and "fonts.googleapis.com" not in h]
    r.ok(not ext, "external stylesheets limited to Google Fonts", ", ".join(ext))
    app = (WEB / "app.js").read_text(encoding="utf-8")
    r.ok("prefers-reduced-motion" in app and "prefers-reduced-motion" in (WEB / "styles.css").read_text(encoding="utf-8"),
         "reduced motion honoured in script and styles")
    r.ok("motion-paused" in app, "visible pause control for looping motion (WCAG 2.2.2)")
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
