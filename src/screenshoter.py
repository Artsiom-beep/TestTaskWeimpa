from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def make_screenshot(
    url: str,
    output_path: Path,
    viewport_width: int = 1440,
    viewport_height: int = 900,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
        )

        ok = True
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except PlaywrightTimeoutError:
            ok = False

        page.wait_for_timeout(2000)

        page.screenshot(path=str(output_path), full_page=True)

        browser.close()

        if not ok:
            print("[FAIL] Страница не загрузилась полностью. Скриншот сделан по текущему состоянию.")
