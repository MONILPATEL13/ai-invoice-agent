"""Step 2: ask a local LLM for the fields, check the answer, retry if needed."""
import json
import os
import re
from datetime import datetime

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

NUMBER_OR_NULL = {"type": ["number", "null"]}
TEXT_OR_NULL = {"type": ["string", "null"]}

# The shape of the JSON we want back.
SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": TEXT_OR_NULL,
        "invoice_number": TEXT_OR_NULL,
        "date": TEXT_OR_NULL,
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": NUMBER_OR_NULL,
                    "unit_price": NUMBER_OR_NULL,
                    "amount": NUMBER_OR_NULL,
                },
                "required": ["description", "quantity", "unit_price", "amount"],
            },
        },
        "tax_amount": NUMBER_OR_NULL,
        "total_amount": NUMBER_OR_NULL,
    },
    "required": ["vendor", "invoice_number", "date", "line_items",
                 "tax_amount", "total_amount"],
}

PROMPT = """You extract data from invoices.
Rules:
- Use only information written in the document. If a value is missing, use null.
- vendor is the company that issued the invoice, not the customer.
- date is the invoice date, copied exactly as written. Do not reformat it.
- Amounts are plain numbers without currency symbols or commas.
- total_amount is the final amount to pay, including tax.

Document:
{text}
"""


def ask_ollama(messages, model):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": messages,
            "format": SCHEMA,
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192},
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y",
                "%d-%m-%y", "%d %b %Y", "%d %B %Y", "%d-%b-%Y",
                "%b %d, %Y", "%B %d, %Y"]


def normalize_date(value):
    """Convert to YYYY-MM-DD. Numeric dates are read as day/month/year."""
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), date_format).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return value


def fix_date(data, text):
    """Python converts the date, so the model cannot swap day and month."""
    raw = data.get("date")
    if not raw or not isinstance(raw, str):
        return []
    if not re.search(rf"(?<!\d){re.escape(raw)}(?!\d)", text):
        return ["date is not copied exactly as written in the document"]
    data["date"] = normalize_date(raw)
    return []


def validate(data):
    """Return a list of problems. An empty list means all checks passed."""
    problems = []
    if not data.get("vendor"):
        problems.append("vendor is missing")

    try:
        datetime.strptime(data.get("date") or "", "%Y-%m-%d")
    except (ValueError, TypeError):
        problems.append("date is missing or not a recognised date")

    total = data.get("total_amount")
    if not is_number(total):
        problems.append("total_amount is missing")

    items = data.get("line_items") or []
    if not items:
        problems.append("line_items is empty")
    elif any(not is_number(i.get("amount")) for i in items):
        problems.append("a line item has no amount")
    elif is_number(total):
        tax = data.get("tax_amount") or 0
        expected = sum(i["amount"] for i in items) + tax
        if abs(expected - total) > 1:
            problems.append(
                f"line items plus tax = {expected:.2f}, but total_amount = {total:.2f}"
            )
    return problems


def extract_fields(text, model=DEFAULT_MODEL, max_attempts=3, ask=ask_ollama):
    """Agent loop: extract -> check -> send the problems back -> try again."""
    messages = [{"role": "user", "content": PROMPT.format(text=text)}]
    best = None

    for attempt in range(1, max_attempts + 1):
        reply = ask(messages, model)
        try:
            data = json.loads(reply)
            date_problems = fix_date(data, text)
            problems = date_problems + validate(data)
        except (json.JSONDecodeError, AttributeError, TypeError):
            data, problems = {}, ["reply was not valid invoice JSON"]

        if best is None or len(problems) < len(best["problems"]):
            best = {"data": data, "problems": problems}
        best["attempts"] = attempt
        if not problems:
            break

        messages += [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": "Your answer has these problems: "
             + "; ".join(problems)
             + ". Read the document again and return corrected JSON. "
               "Do not invent values."},
        ]
    return best
