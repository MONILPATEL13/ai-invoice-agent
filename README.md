# AI Invoice Processing Agent

An AI-powered invoice processing system built with Python, Ollama, Qwen3, PyMuPDF, and Pydantic.

The system automatically reads multiple invoice PDFs from a folder, extracts important invoice information using a local AI model, validates the extracted data, and returns structured JSON.

## Features

- Process multiple invoice PDFs automatically
- Extract text from PDF invoices
- Use local AI with Ollama and Qwen3
- Extract:
  - Vendor name
  - Invoice number
  - Invoice date
  - Total amount
- Convert AI output into structured JSON
- Validate extracted data using Pydantic
- Handle missing invoice fields without inventing data
- Completely local AI processing

## Tech Stack

- Python
- Ollama
- Qwen3:4b
- PyMuPDF
- Pydantic
- OpenPyXL

## Project Structure

```text
ai-invoice-agent/
├── src/
│   ├── main.py
│   └── pdf_reader.py
├── invoices/
├── output/
├── requirements.txt
├── .gitignore
└── README.md