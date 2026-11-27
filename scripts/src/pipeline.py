"""Joins the steps together for one file."""
import requests

from .extract import extract_text
from .llm import DEFAULT_MODEL, extract_fields


def process_file(name, pdf_file, model=DEFAULT_MODEL):
    try:
        result = extract_fields(extract_text(pdf_file), model=model)
        status = "Needs review" if result["problems"] else "OK"
    except requests.RequestException:
        raise  # Ollama problem: stop and tell the user
    except Exception as error:  # one bad PDF should not stop the batch
        result = {"data": {}, "problems": [str(error)], "attempts": 0}
        status = "Failed"
    return {"file": name, "status": status, **result}
