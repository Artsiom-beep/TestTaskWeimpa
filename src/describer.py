# src/describer.py
import base64
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from openai import OpenAI


PROMPT_TEMPLATE = """
Ты описываешь веб-страницу по её скриншотам. Пиши простым русским языком, чтобы понял ребёнок и пожилой человек.

У тебя может быть несколько скриншотов одной и той же страницы (например, разные слайды или экраны). Учитывай их все.

Структура ответа (используй Markdown):

1. Один-два предложения: что это за сайт и для кого он.
2. 1–3 основных действия, которые может сделать пользователь на этой странице.
3. Крупные блоки страницы в реальном порядке просмотра (сверху вниз или слева направо, если это слайдер).
4. Объяснение страницы в 5–10 очень простых предложениях, без сложных терминов.

Не добавляй ничего лишнего, не пиши про себя или про модель.
"""


def _load_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Переменная окружения OPENAI_API_KEY не задана")
    return OpenAI(api_key=api_key)


def _encode_image_to_data_url(image_path: Path) -> str:
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def describe_page_from_screenshots(image_paths: List[Path], model: str = "gpt-5") -> str:
    """
    Отправляет один или несколько скриншотов в OpenAI и возвращает текстовое описание страницы.
    """
    if not image_paths:
        raise ValueError("Список скриншотов пуст")

    client = _load_client()

    content = [
        {
            "type": "input_text",
            "text": PROMPT_TEMPLATE.strip(),
        }
    ]

    for path in image_paths:
        image_url = _encode_image_to_data_url(path)
        content.append(
            {
                "type": "input_image",
                "image_url": image_url,
            }
        )

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    try:
        return response.output_text
    except AttributeError:
        parts: list[str] = []
        for item in getattr(response, "output", []):
            if getattr(item, "type", None) == "message":
                for c in getattr(item, "content", []):
                    if getattr(c, "type", None) == "output_text":
                        parts.append(getattr(c, "text", ""))
        return "\n".join(parts).strip()
