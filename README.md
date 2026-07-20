# Bank Statement PDF-to-Excel Converter & Analyzer

A Python-based web application designed to convert bank statement PDF files into professionally styled Excel spreadsheets. The application includes a beautiful dark-themed dashboard where users can upload PDFs, edit parsed transactions in a live interactive grid, and export them.

## Features

- **Automated Parsing**: Uses `pdfplumber` to extract transaction details and metadata from borderless statement tables (highly calibrated for KVB and standardized layouts).
- **Interactive Live Preview**: Preview all transactions in a tabular format. You can:
  - Add new rows.
  - Delete existing rows.
  - Edit cell values (dates, descriptions, reference numbers, credits, debits, balance).
- **Real-time Calculations**: Summary statistics (Total credits, debits, net flow, ending balance) recalculate instantly on any edit.
- **Premium Excel Styling**: The exported spreadsheet uses a professional palette:
  - Title banner.
  - KPI boxes for summary statistics at the top.
  - Custom column sizes, zebra striping, and text wrapping.
  - Standard currency formatting for debit, credit, and balance columns.
  - Selected currency prefix support (₹, $, €, £, or none).

## Technologies Used

- **Backend**: Python 3.13, Flask, pdfplumber, pandas, openpyxl.
- **Frontend**: Vanilla HTML5, CSS3, JavaScript.

## Setup Instructions

1. Ensure Python 3.13+ is installed.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Running Tests

To run the automated test suite, execute:
```bash
python test_parser.py
```
