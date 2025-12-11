# src/main.py
import argparse
from pathlib import Path

from screenshoter import capture_page
from describer import describe_page_from_screenshots
from reporter import build_markdown_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Скрипт: скриншоты страницы + описание через OpenAI + Markdown-отчёт",
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
        required=True,
        help="Краткий комментарий автора к отчёту (обязательный параметр)",
    )
    parser.add_argument(
        "--model",
        default="gpt-5",
        help="Модель OpenAI для анализа изображений (по умолчанию gpt-5)",
    )
    parser.add_argument(
        "--horizontal-slides",
        type=int,
        default=1,
        help="Количество горизонтальных слайдов для захвата (например, для weimpa.com)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    url = args.url
    reports_dir = Path(args.output_dir)
    screenshots_dir = Path(args.screenshots_dir)

    screenshots_dir.mkdir(parents=True, exist_ok=True)

    from reporter import _slug_from_url

    slug = _slug_from_url(url)

    print(f"[1/3] Делаю скриншоты {url} -> {screenshots_dir}/{slug}_*.png")

    screenshot_paths, diagnostics = capture_page(
        url=url,
        screenshots_dir=screenshots_dir,
        slug=slug,
        horizontal_slides=args.horizontal_slides,
    )

    has_captcha = diagnostics.get("captcha_detected", False)

    print(f"[2/3] Отправляю скриншоты в OpenAI ({args.model})")

    if has_captcha:
        ai_text = (
            "Не удалось полноценно проанализировать содержимое страницы.\n\n"
            "Причина: при загрузке появляется защита (CAPTCHA / проверка «я не робот»), "
            "которая блокирует автоматический доступ к контенту. Скриншот(ы) в отчёте "
            "показывают страницу проверки, а не целевой контент сайта."
        )
    else:
        ai_text = describe_page_from_screenshots(screenshot_paths, model=args.model)

    print(f"[3/3] Собираю Markdown-отчёт в каталоге {reports_dir}")
    main_screenshot = screenshot_paths[0]

    report_path = build_markdown_report(
        url=url,
        screenshot_path=main_screenshot,
        ai_text=ai_text,
        comment=args.comment,
        reports_dir=reports_dir,
    )

    print("Готово.")
    print(f"Отчёт:      {report_path}")
    print(f"Скриншоты:  {', '.join(str(p) for p in screenshot_paths)}")


if __name__ == "__main__":
    main()
