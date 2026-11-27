# Output format

`invoices.json` is a list with one entry per PDF.

| Field | Meaning |
|---|---|
| `file` | PDF file name |
| `status` | `OK`, `Needs review` or `Failed` |
| `data` | Extracted invoice fields (empty if reading failed) |
| `problems` | Checks that did not pass |
| `attempts` | Number of model attempts |

## Fields inside `data`

| Field | Type |
|---|---|
| `vendor` | text or null |
| `invoice_number` | text or null |
| `date` | `YYYY-MM-DD` or null. Ambiguous dates are read as day/month/year |
| `line_items` | list of `description`, `quantity`, `unit_price`, `amount` |
| `tax_amount` | number or null |
| `total_amount` | number or null |

`invoices.xlsx` has two sheets: `Invoices` and `Line Items`.
