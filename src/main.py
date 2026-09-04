from pathlib import Path

from pdf_reader import extract_text_from_pdf
from ollama import chat
from pydantic import BaseModel


class InvoiceData(BaseModel):
    vendor_name: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    total_amount: float | None = None


# Folder containing invoices
invoice_folder = Path("invoices")

# Find all PDF files
pdf_files = list(invoice_folder.glob("*.pdf"))

print(f"\nFound {len(pdf_files)} invoice PDF(s).\n")


# Process each invoice
for pdf_path in pdf_files:

    print("=" * 60)
    print(f"Processing: {pdf_path.name}")
    print("=" * 60)

    # Extract text from PDF
    invoice_text = extract_text_from_pdf(pdf_path)

    # Create AI prompt
    prompt = f"""
You are an invoice data extraction assistant.

Extract these four fields from the invoice:

- vendor_name
- invoice_number
- invoice_date
- total_amount

Rules:
1. Extract only information actually present in the invoice.
2. Do not guess or invent information.
3. If a field is missing, return null.
4. Return only the requested structured data.

Invoice text:
{invoice_text}
"""

    # Ask Qwen for structured JSON
    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=InvoiceData.model_json_schema()
    )

    # Validate AI response
    invoice_data = InvoiceData.model_validate_json(
        response.message.content
    )

    # Display result
    print("\nInvoice Data:")

    print("Vendor Name   :", invoice_data.vendor_name)
    print("Invoice Number:", invoice_data.invoice_number)
    print("Invoice Date  :", invoice_data.invoice_date)
    print("Total Amount  :", invoice_data.total_amount)

    print("\nJSON:")
    print(invoice_data.model_dump_json(indent=4))

print("\nAll invoices processed successfully! ✅")