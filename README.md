# Invoice PDF Extractor

An agent skill that converts text-based invoice PDFs into JSON and Excel using a local Ollama model.

## What you need
Python 3.10+, Ollama, the `llama3.2:3b` model, and the packages in `requirements.txt`.

## Use
Ask your agent: "Extract the invoices in my `invoices` folder to Excel."

Or run it yourself:

    python scripts/batch.py "path/to/invoices" --out "path/to/output"

## Limitations
- No OCR for scanned PDFs
- A small model can make mistakes, so verify important values
- Discounts or extra charges may cause "Needs review"
- Very long documents may not fit in the model's context
- Ambiguous dates are read as day/month/year

`examples/sample-output.json` shows the output format with fake data. It is an illustration, not a recorded model result.

## Author
Monil Patel: https://github.com/MONILPATEL13
