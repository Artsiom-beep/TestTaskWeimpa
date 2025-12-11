from pathlib import Path
from typing import List, Tuple, Dict

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Page,
)


def _detect_captcha(page: Page) -> bool:

    selectors = [
        'text="I am not a robot"',
        'text="I\'m not a robot"',
        'iframe[title*="captcha"]',
        'div[id*="cf-challenge"]',
        'text=/Cloudflare/i',
        'text=/Verification/i',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el is not None:
                return True
        except Exception:
            pass
    return False


def capture_page(
    url: str,
    screenshots_dir: Path,
    slug: str,
    horizontal_slides: int = 1,
) -> Tuple[List[Path], Dict[str, bool]]:
    """
    Делает один или несколько скриншотов страницы.

    horizontal_slides:
      1  -> один скрин
      >1 -> предполагаем горизонтальный слайдер; делаем N скринов, между ними жмём ArrowRight

    Возвращает:
      (список путей к скринам, diagnostics: { "load_ok": bool, "captcha_detected": bool })
    """
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    screenshot_paths: List[Path] = []
    diagnostics: Dict[str, bool] = {
        "load_ok": True,
        "captcha_detected": False,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1440, "height": 900},
        )

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except PlaywrightTimeoutError:
            diagnostics["load_ok"] = False

        page.wait_for_timeout(2000)

        diagnostics["captcha_detected"] = _detect_captcha(page)

        slides = max(1, horizontal_slides)

        for i in range(slides):
            if slides == 1:
                filename = f"{slug}.png"
            else:
                filename = f"{slug}_slide_{i+1}.png"

            output_path = screenshots_dir / filename
            page.screenshot(path=str(output_path), full_page=True)
            screenshot_paths.append(output_path)

            if i < slides - 1:
                try:
                    page.keyboard.press("ArrowRight")
                except Exception:
                    pass
                page.wait_for_timeout(1000)

        browser.close()

    return screenshot_paths, diagnostics
