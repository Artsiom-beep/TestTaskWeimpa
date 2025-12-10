# src/main.py
import argparse
from pathlib import Path

from screenshoter import make_screenshot
from describer import describe_page_from_screenshot
from reporter import build_markdown_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Скрипт: скриншот страницы + описание через OpenAI + Markdown-отчёт",
    )
    parser.add_argument("url", help="URL страницы для анализа")
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Каталог для сохранения отчётов (по умолчанию: reports)",
    )
    parser.add_argument(
        "--screenshots-dir",
        default="screenshots",
        help="Каталог для сохранения скриншотов (по умолчанию: screenshots)",
    )
    parser.add_argument(
        "--comment",
        default="Комментарий ещё не добавлен. Заполните этот блок вручную после просмотра отчёта.",
        help="Краткий комментарий автора, будет добавлен в отчёт",
    )
    parser.add_argument(
        "--model",
        default="gpt-5",
        help="Модель OpenAI для анализа изображения (по умолчанию gpt-5)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    url = args.url
    reports_dir = Path(args.output_dir)
    screenshots_dir = Path(args.screenshots_dir)

    screenshots_dir.mkdir(parents=True, exist_ok=True)

    from reporter import _slug_from_url

    slug = _slug_from_url(url)
    screenshot_path = screenshots_dir / f"{slug}.png"

    print(f"[1/3] Делаю скриншот {url} -> {screenshot_path}")
    make_screenshot(url, screenshot_path)

    print(f"[2/3] Отправляю скриншот в OpenAI ({args.model})")
    ai_text = describe_page_from_screenshot(screenshot_path, model=args.model)

    print(f"[3/3] Собираю Markdown-отчёт в каталоге {reports_dir}")
    report_path = build_markdown_report(
        url=url,
        screenshot_path=screenshot_path,
        ai_text=ai_text,
        comment=args.comment,
        reports_dir=reports_dir,
    )

    print("Готово.")
    print(f"Отчёт:      {report_path}")
    print(f"Скриншот:   {screenshot_path}")


if __name__ == "__main__":
    main()
