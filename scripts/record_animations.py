"""Pass 3.0 cinematic animatie recordings: 7 varianten plus stills.

Output: docs/recordings/fase-2/puna-pass3-{dimensie}-{variant}.webm en
docs/screenshots/fase-2/puna-pass3-{dimensie}-{variant}-{frame}.png.

Playwright legt video vast in WebM (VP9). MP4-conversie zou ffmpeg vereisen,
WebM is browser-native en speelt op moderne systemen direct af.

Loopt tegen lopende Next.js dev-server op localhost:3000.
"""

import shutil
import urllib.request
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from playwright.sync_api import Page, sync_playwright

RECORD_DIR = Path("docs/recordings/fase-2")
RECORD_DIR.mkdir(parents=True, exist_ok=True)
SHOTS_DIR = Path("docs/screenshots/fase-2")
SHOTS_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORT_W, VIEWPORT_H = 1440, 900


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def url_for(query: str) -> str:
    base = "http://localhost:3000/"
    if query:
        return f"{base}?{query}#puna"
    return f"{base}#puna"


def goto_puna(page: Page, query: str) -> None:
    page.goto(url_for(query), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("h1", state="visible", timeout=15000)
    page.wait_for_function(
        "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
        timeout=30000,
    )
    # Scroll naar Puna VP1 zodat IntersectionObserver de in-view triggered.
    page.evaluate(
        "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
    )


def record(
    name: str,
    query: str,
    duration_ms: int,
    after_load: Optional[Callable[[Page], None]] = None,
) -> Path:
    """Capture sessie naar WebM. Animatie speelt zodra Puna in view komt."""
    tmp_dir = RECORD_DIR / "_tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    final_path = RECORD_DIR / f"{name}.webm"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            record_video_dir=str(tmp_dir),
            record_video_size={"width": VIEWPORT_W, "height": VIEWPORT_H},
        )
        page = context.new_page()
        goto_puna(page, query)

        if after_load is not None:
            after_load(page)
        else:
            page.wait_for_timeout(duration_ms)

        page.close()
        context.close()
        browser.close()

    videos = list(tmp_dir.glob("*.webm"))
    if videos:
        if final_path.exists():
            final_path.unlink()
        videos[0].rename(final_path)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    size_kb = final_path.stat().st_size / 1024 if final_path.exists() else 0
    print(f"[record:{name}] -> {final_path} ({size_kb:.0f} KB)")
    return final_path


def parallax_sweep(page: Page) -> None:
    # Wacht eerst tot intro compleet (intro A duurt ~800ms, marge naar 1500ms).
    page.wait_for_timeout(1500)
    steps = 25
    for i in range(steps):
        # Sweep over de rechter helft van viewport waar de cutout staat.
        x = VIEWPORT_W // 2 + (VIEWPORT_W // 3) * (i / (steps - 1))
        y = VIEWPORT_H * (0.3 + 0.4 * (i / (steps - 1)))
        page.mouse.move(x, y)
        page.wait_for_timeout(60)
    # Hold even op het eind.
    page.wait_for_timeout(400)


def scale_hover(page: Page) -> None:
    # Wacht tot intro compleet.
    page.wait_for_timeout(1500)
    # Hover in de section.
    page.mouse.move(VIEWPORT_W // 2 + 200, VIEWPORT_H // 2)
    page.wait_for_timeout(800)
    # Hover uit.
    page.mouse.move(20, 20)
    page.wait_for_timeout(700)
    # Hover terug in.
    page.mouse.move(VIEWPORT_W // 2 + 200, VIEWPORT_H // 2)
    page.wait_for_timeout(700)


def shot(
    name: str,
    query: str,
    wait_ms: int,
    after_scroll: Optional[Callable[[Page], None]] = None,
) -> Path:
    out = SHOTS_DIR / f"{name}.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        goto_puna(page, query)
        if after_scroll is not None:
            after_scroll(page)
        page.wait_for_timeout(wait_ms)
        page.screenshot(path=str(out), full_page=False)
        browser.close()
    size_kb = out.stat().st_size / 1024
    print(f"[shot:{name}] -> {out} ({size_kb:.0f} KB)")
    return out


def hover_then_settle(x: int, y: int) -> Callable[[Page], None]:
    def fn(page: Page) -> None:
        page.wait_for_timeout(1500)  # intro complete
        page.mouse.move(x, y)
    return fn


if __name__ == "__main__":
    prewarm()

    # Recordings per dimensie.
    record("puna-pass3-intro-A", "intro=A", 3000)
    record("puna-pass3-intro-B", "intro=B", 3000)
    record("puna-pass3-hover-none", "hover=none", 4000)
    record("puna-pass3-hover-parallax", "hover=parallax", 4000, after_load=parallax_sweep)
    record("puna-pass3-hover-scale", "hover=scale", 4000, after_load=scale_hover)
    record("puna-pass3-sig-clippath", "sig=clippath", 2500)
    record("puna-pass3-sig-fade", "sig=fade", 2500)

    # Stills: 3 frames per intro variant (start, mid, eind).
    for intro in ("A", "B"):
        for label, ms in (("start", 80), ("mid", 500), ("eind", 1500)):
            shot(f"puna-pass3-intro-{intro}-{label}", f"intro={intro}", ms)

    # Stills: 2 frames per hover variant (rust, hover).
    shot("puna-pass3-hover-none-rust", "hover=none", 1800)
    shot("puna-pass3-hover-parallax-rust", "hover=parallax", 1800)
    shot(
        "puna-pass3-hover-parallax-active",
        "hover=parallax",
        500,
        after_scroll=hover_then_settle(VIEWPORT_W * 3 // 4, VIEWPORT_H // 3),
    )
    shot("puna-pass3-hover-scale-rust", "hover=scale", 1800)
    shot(
        "puna-pass3-hover-scale-active",
        "hover=scale",
        800,
        after_scroll=hover_then_settle(VIEWPORT_W // 2 + 200, VIEWPORT_H // 2),
    )

    # Stills: 3 frames per sig variant (start, halfway, eind).
    for sig in ("clippath", "fade"):
        for label, ms in (("start", 100), ("mid", 600), ("eind", 1700)):
            shot(f"puna-pass3-sig-{sig}-{label}", f"sig={sig}", ms)
