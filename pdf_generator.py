#!/usr/bin/env python3
"""
Генератор PDF-чеков из CSV/JSON данных и HTML-шаблонов.

Положите шрифт DejaVu Sans или Roboto в папку fonts/:
  - fonts/DejaVuSans.ttf
  - fonts/Roboto-Regular.ttf
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

_GLIB_SKIP_MARKERS = (
    "GLib-GIO-WARNING",
    "Unexpectedly, UWP app",
)


def _install_glib_stderr_filter() -> None:
    """Фильтрует stderr на уровне FD — GLib пишет напрямую в fd 2, мимо sys.stderr."""
    read_fd, write_fd = os.pipe()
    original_stderr_fd = os.dup(2)

    try:
        os.dup2(write_fd, 2)
    finally:
        os.close(write_fd)

    sys.stderr = os.fdopen(2, "w", encoding="utf-8", errors="replace", closefd=False)

    def _forward_stderr() -> None:
        with os.fdopen(read_fd, "r", encoding="utf-8", errors="replace") as pipe_in:
            with os.fdopen(
                original_stderr_fd,
                "w",
                encoding="utf-8",
                errors="replace",
                closefd=False,
            ) as real_stderr:
                for line in pipe_in:
                    if any(marker in line for marker in _GLIB_SKIP_MARKERS):
                        continue
                    real_stderr.write(line)
                    real_stderr.flush()

    threading.Thread(
        target=_forward_stderr,
        daemon=True,
        name="glib-stderr-filter",
    ).start()


if platform.system() == "Windows":
    _install_glib_stderr_filter()

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
FONTS_DIR = BASE_DIR / "fonts"

DATA_EXTENSIONS = {".csv", ".json"}
TEMPLATE_EXTENSIONS = {".html", ".htm"}

FONT_CANDIDATES = [
    FONTS_DIR / "DejaVuSans.ttf",
    FONTS_DIR / "Roboto-Regular.ttf",
    FONTS_DIR / "Roboto.ttf",
]

if platform.system() == "Windows":
    FONT_CANDIDATES.extend(
        [
            Path(r"C:\Windows\Fonts\DejaVuSans.ttf"),
            Path(r"C:\Windows\Fonts\Roboto-Regular.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
        ]
    )
elif platform.system() == "Darwin":
    FONT_CANDIDATES.extend(
        [
            Path("/Library/Fonts/DejaVu Sans.ttf"),
            Path("/Library/Fonts/Roboto-Regular.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial.ttf"),
        ]
    )


def setup_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


def print_header(title: str) -> None:
    line = "-" * len(title)
    print(f"\n{title}\n{line}")


def print_numbered_list(items: list[str], empty_message: str) -> None:
    if not items:
        print(f"  {empty_message}")
        return
    for index, item in enumerate(items, start=1):
        print(f"  {index}. {item}")


def choose_from_list(prompt: str, items: list[str]) -> str | None:
    if not items:
        return None

    while True:
        print()
        choice = input(f"{prompt} (1-{len(items)}, 0 - выход): ").strip()
        if choice == "0":
            return None
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(items):
                return items[index - 1]
        print("Неверный выбор. Введите номер из списка.")


def find_font() -> Path:
    for path in FONT_CANDIDATES:
        if path.is_file():
            return path.resolve()

    raise FileNotFoundError(
        "Не найден шрифт с поддержкой кириллицы.\n"
        "Поместите DejaVuSans.ttf или Roboto-Regular.ttf в папку fonts/."
    )


def format_money(value: Any) -> str:
    number = float(value)
    if number.is_integer():
        return f"{int(number):,}".replace(",", " ")
    return f"{number:,.2f}".replace(",", " ")


def list_data_files() -> list[Path]:
    if not DATA_DIR.is_dir():
        return []
    files = [
        path
        for path in sorted(DATA_DIR.iterdir())
        if path.is_file() and path.suffix.lower() in DATA_EXTENSIONS
    ]
    return files


def list_template_files() -> list[Path]:
    if not TEMPLATES_DIR.is_dir():
        return []
    files = [
        path
        for path in sorted(TEMPLATES_DIR.iterdir())
        if path.is_file() and path.suffix.lower() in TEMPLATE_EXTENSIONS
    ]
    return files


def _normalize_invoice(raw: dict[str, Any]) -> dict[str, Any]:
    items = raw.get("items")
    if items is None:
        quantity = raw.get("quantity", 1)
        price = raw.get("price", 0)
        item_sum = raw.get("sum")
        if item_sum is None:
            item_sum = float(quantity) * float(price)
        items = [
            {
                "name": raw.get("item_name") or raw.get("name", ""),
                "quantity": quantity,
                "price": price,
                "sum": item_sum,
            }
        ]

    normalized_items = []
    for item in items:
        quantity = item.get("quantity", 1)
        price = item.get("price", 0)
        item_sum = item.get("sum")
        if item_sum is None:
            item_sum = float(quantity) * float(price)
        normalized_items.append(
            {
                "name": item.get("name", ""),
                "quantity": quantity,
                "price": price,
                "sum": item_sum,
            }
        )

    total = raw.get("total")
    if total is None:
        total = sum(float(item["sum"]) for item in normalized_items)

    return {
        "invoice_id": str(raw["invoice_id"]),
        "date": raw.get("date", ""),
        "customer_name": raw.get("customer_name", ""),
        "customer_address": raw.get("customer_address", ""),
        "items": normalized_items,
        "total": total,
    }


def load_json_invoices(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        if "invoices" in data:
            records = data["invoices"]
        else:
            records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError("JSON должен содержать объект или массив счетов.")

    return [_normalize_invoice(record) for record in records]


def load_csv_invoices(path: Path) -> list[dict[str, Any]]:
    df = pd.read_csv(path, encoding="utf-8")
    required = {"invoice_id", "customer_name"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"В CSV отсутствуют обязательные колонки: {', '.join(missing)}")

    grouped: dict[str, list[dict[str, Any]]] = {}
    meta: dict[str, dict[str, Any]] = {}

    for row in df.to_dict(orient="records"):
        invoice_id = str(row["invoice_id"])
        if invoice_id not in meta:
            meta[invoice_id] = {
                "invoice_id": invoice_id,
                "date": row.get("date", ""),
                "customer_name": row.get("customer_name", ""),
                "customer_address": row.get("customer_address", ""),
            }
        grouped.setdefault(invoice_id, []).append(row)

    invoices = []
    for invoice_id, rows in grouped.items():
        items = []
        for row in rows:
            quantity = row.get("quantity", 1)
            price = row.get("price", 0)
            item_sum = row.get("sum")
            if pd.isna(item_sum) if isinstance(item_sum, float) else item_sum is None:
                item_sum = float(quantity) * float(price)
            items.append(
                {
                    "name": row.get("item_name") or row.get("name", ""),
                    "quantity": quantity,
                    "price": price,
                    "sum": item_sum,
                }
            )
        invoice = {**meta[invoice_id], "items": items}
        invoices.append(_normalize_invoice(invoice))

    return invoices


def load_invoices(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json_invoices(path)
    if suffix == ".csv":
        return load_csv_invoices(path)
    raise ValueError(f"Неподдерживаемый формат файла: {suffix}")


def render_html(template_path: Path, invoice: dict[str, Any], font_path: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["format_money"] = format_money
    template = env.get_template(template_path.name)
    context = {
        **invoice,
        "font_url": font_path.as_uri(),
    }
    return template.render(**context)


def generate_pdf(html_content: str, output_path: Path) -> Path:
    """Сохраняет PDF и возвращает фактический путь к файлу."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        dir=OUTPUT_DIR,
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        HTML(string=html_content, base_url=str(TEMPLATES_DIR)).write_pdf(str(temp_path))

        candidates = [output_path]
        if output_path.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            candidates.append(output_path.with_name(f"{output_path.stem}_{stamp}.pdf"))

        for target in candidates:
            try:
                temp_path.replace(target)
                return target
            except PermissionError:
                continue

        raise PermissionError(
            f"Не удалось сохранить PDF в {OUTPUT_DIR}. "
            "Закройте открытый файл в просмотрщике PDF и повторите попытку."
        )
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def open_pdf(path: Path) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            import os

            os.startfile(str(path))  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except OSError as error:
        print(f"Не удалось открыть PDF автоматически: {error}")
        print(f"Файл сохранён: {path}")


def invoice_label(invoice: dict[str, Any]) -> str:
    customer = invoice.get("customer_name") or "-"
    return f"{invoice['invoice_id']} - {customer}"


def main() -> int:
    setup_console_encoding()
    print_header("PDF Generator - генератор чеков")

    data_files = list_data_files()
    template_files = list_template_files()

    print_header("Доступные файлы с данными")
    print_numbered_list(
        [path.name for path in data_files],
        "Файлы не найдены. Добавьте CSV или JSON в папку data/.",
    )

    print_header("Доступные HTML-шаблоны")
    print_numbered_list(
        [path.name for path in template_files],
        "Шаблоны не найдены. Добавьте HTML в папку templates/.",
    )

    if not data_files or not template_files:
        return 1

    selected_data_name = choose_from_list("Выберите файл данных", [p.name for p in data_files])
    if selected_data_name is None:
        print("Выход.")
        return 0

    selected_template_name = choose_from_list(
        "Выберите HTML-шаблон", [p.name for p in template_files]
    )
    if selected_template_name is None:
        print("Выход.")
        return 0

    data_path = DATA_DIR / selected_data_name
    template_path = TEMPLATES_DIR / selected_template_name

    try:
        invoices = load_invoices(data_path)
    except (ValueError, json.JSONDecodeError, OSError) as error:
        print(f"\nОшибка чтения данных: {error}")
        return 1

    if not invoices:
        print("\nВ выбранном файле нет счетов.")
        return 1

    print_header("Доступные чеки (invoice id)")
    labels = [invoice_label(invoice) for invoice in invoices]
    print_numbered_list(labels, "Счета не найдены.")

    selected_label = choose_from_list("Выберите чек для генерации PDF", labels)
    if selected_label is None:
        print("Выход.")
        return 0

    selected_index = labels.index(selected_label)
    invoice = invoices[selected_index]

    try:
        font_path = find_font()
    except FileNotFoundError as error:
        print(f"\n{error}")
        return 1

    html_content = render_html(template_path, invoice, font_path)
    output_name = f"{invoice['invoice_id']}.pdf"
    output_path = OUTPUT_DIR / output_name

    try:
        output_path = generate_pdf(html_content, output_path)
    except PermissionError as error:
        print(f"\nОшибка генерации PDF: {error}")
        return 1
    except Exception as error:
        print(f"\nОшибка генерации PDF: {error}")
        return 1

    print_header("Готово")
    if output_path.name != f"{invoice['invoice_id']}.pdf":
        print(
            f"  Предыдущий PDF был открыт в другой программе, "
            f"файл сохранён под новым именем."
        )
    print(f"  PDF сохранён: {output_path}")
    print(f"  Шрифт: {font_path.name}")

    open_pdf(output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
