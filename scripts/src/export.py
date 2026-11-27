"""Step 3: save results to an Excel report."""
import pandas as pd

INVOICE_COLUMNS = ["file", "status", "vendor", "invoice_number", "date",
                   "tax_amount", "total_amount", "attempts", "problems"]
ITEM_COLUMNS = ["file", "description", "quantity", "unit_price", "amount"]


def safe(value):
    """Stop text from a PDF being run as an Excel formula."""
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def to_tables(results):
    invoices, items = [], []
    for result in results:
        data = result["data"]
        row = {key: data.get(key) for key in INVOICE_COLUMNS}
        row.update(file=result["file"], status=result["status"],
                   attempts=result["attempts"],
                   problems="; ".join(result["problems"]))
        invoices.append({k: safe(v) for k, v in row.items()})
        for item in data.get("line_items") or []:
            line = {key: item.get(key) for key in ITEM_COLUMNS}
            line["file"] = result["file"]
            items.append({k: safe(v) for k, v in line.items()})
    return (pd.DataFrame(invoices, columns=INVOICE_COLUMNS),
            pd.DataFrame(items, columns=ITEM_COLUMNS))


def save_excel(results, target):
    """target can be a file path or an in-memory buffer."""
    invoices, items = to_tables(results)
    with pd.ExcelWriter(target, engine="openpyxl") as writer:
        invoices.to_excel(writer, sheet_name="Invoices", index=False)
        items.to_excel(writer, sheet_name="Line Items", index=False)
        for sheet in writer.sheets.values():
            for column in sheet.columns:
                width = max(len(str(c.value or "")) for c in column) + 2
                sheet.column_dimensions[column[0].column_letter].width = min(width, 50)
