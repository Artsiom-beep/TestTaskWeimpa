import os
from pathlib import Path
from urllib.parse import urlparse


def _slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    host_part = parsed.netloc.replace(":", "_")
    path_part = parsed.path.strip("/").replace("/", "_")
    if path_part:
        return f"{host_part}__{path_part}"
    return host_part or "report"


def build_markdown_report(
    url: str,
    screenshot_path: Path,
    ai_text: str,
    comment: str | None,
    reports_dir: Path,
) -> Path:

    reports_dir.mkdir(parents=True, exist_ok=True)

    slug = _slug_from_url(url)
    report_path = reports_dir / f"{slug}.md"

    rel_screenshot_str = os.path.relpath(screenshot_path, start=report_path.parent)
    rel_screenshot = Path(rel_screenshot_str)

    comment_text = comment.strip() if comment else "Комментарий ещё не добавлен."

    content_lines = [
        f"# Отчёт по странице {url}",
        "",
        f"![Скриншот страницы]({rel_screenshot.as_posix()})",
        "",
        "## Описание от модели",
        "",
        ai_text.strip(),
        "",
        "## Краткий комментарий автора",
        "",
        comment_text,
        "",
    ]

    report_path.write_text("\n".join(content_lines), encoding="utf-8")
    return report_path