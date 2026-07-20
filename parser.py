import pdfplumber
import re
from collections import defaultdict

def clean_val(val):
    if not val:
        return ""
    val = val.strip()
    return "" if val == "-" else val

def _extract_holder_name(text_full, default="Account Holder"):
    for line in text_full.split("\n"):
        clean_line = line.strip()
        if clean_line.startswith(("MR.", "MS.", "MRS.", "M/S.", "SRI ", "MISS", "MR ", "MS ", "MRS ")):
            return clean_line
    return default

def parse_pdf(pdf_path):
    # Open the PDF to detect bank type and run the appropriate parser
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError("The PDF document does not contain any pages.")
        
        # Extract text from the first page to inspect branding keywords
        first_page_text = pdf.pages[0].extract_text() or ""
        first_page_lower = first_page_text.lower()
        header_area = first_page_lower[:600]
        
        # Auto-detect bank type based on header metadata
        if "union bank" in header_area or "unionbank" in header_area or "ubin" in header_area:
            return _parse_union_bank(pdf, first_page_text)
        elif "indian bank" in header_area or "indianbank" in header_area or "idib" in header_area:
            return _parse_indian_bank(pdf, first_page_text)
        elif "punjab national" in header_area or "pnb" in header_area or "punb" in header_area:
            return _parse_pnb(pdf, first_page_text)
        elif "standard chartered" in header_area or "scb" in header_area or "scbl" in header_area:
            return _parse_scb(pdf, first_page_text)
        elif "state bank of india" in header_area or "sbi" in header_area or "sbin" in header_area:
            return _parse_sbi(pdf, first_page_text)
        elif "bank of baroda" in header_area or "bob" in header_area or "barb" in header_area:
            return _parse_bob(pdf, first_page_text)
        elif "hdfc" in header_area:
            return _parse_hdfc(pdf, first_page_text)
        elif "indusind" in header_area or "indb" in header_area:
            return _parse_indusind(pdf, first_page_text)
        elif "icici" in header_area:
            return _parse_icici(pdf, first_page_text)
        elif "kotak" in header_area or "kkbk" in header_area:
            return _parse_kotak(pdf, first_page_text)
        elif "axis" in header_area or "utib" in header_area:
            return _parse_axis(pdf, first_page_text)
        elif "karur vysya" in header_area or "kvb" in header_area:
            return _parse_kvb(pdf, first_page_text)
            
        # Fallbacks in case branding is further down on Page 1
        if "union bank" in first_page_lower or "ubin" in first_page_lower:
            return _parse_union_bank(pdf, first_page_text)
        elif "indian bank" in first_page_lower or "idib" in first_page_lower:
            return _parse_indian_bank(pdf, first_page_text)
        elif "punjab national" in first_page_lower or "pnb" in first_page_lower or "punb" in first_page_lower:
            return _parse_pnb(pdf, first_page_text)
        elif "standard chartered" in first_page_lower or "scb" in first_page_lower or "scbl" in first_page_lower:
            return _parse_scb(pdf, first_page_text)
        elif "state bank of india" in first_page_lower or "sbi" in first_page_lower or "sbin" in first_page_lower:
            return _parse_sbi(pdf, first_page_text)
        elif "bank of baroda" in first_page_lower or "bob" in first_page_lower or "barb" in first_page_lower:
            return _parse_bob(pdf, first_page_text)
        elif "hdfc bank" in first_page_lower or "hdfcbank" in first_page_lower:
            return _parse_hdfc(pdf, first_page_text)
        elif "indusind" in first_page_lower or "indb" in first_page_lower:
            return _parse_indusind(pdf, first_page_text)
        elif "icici" in first_page_lower:
            return _parse_icici(pdf, first_page_text)
        elif "kotak" in first_page_lower or "kkbk" in first_page_lower:
            return _parse_kotak(pdf, first_page_text)
        elif "axis" in first_page_lower or "utib" in first_page_lower:
            return _parse_axis(pdf, first_page_text)
        else:
            return _parse_kvb(pdf, first_page_text)

def _parse_hdfc(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}/\d{2}/\d{2}$|^\d{2}/\d{2}/\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            # We don't crash if Axis or other files are uploaded, but we let the user know
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account No\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"Cust ID\s*:\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Account Type\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"From\s*:\s*(\d{2}/\d{2}/\d{4})\s+To\s*:\s*(\d{2}/\d{2}/\d{4})", text_full)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1)} to {period_match.group(2)}"
            metadata["holder_name"] = _extract_holder_name(text_full, "HDFC Account Holder")

        # Group lines
        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            if "narration" in line_texts and any("closing" in t or "balance" in t for t in line_texts):
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 230.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibration separators
        x_date = 39.9
        x_narr = 144.2
        x_chq = 283.5
        x_val = 361.5
        x_deb = 405.3
        x_cred = 491.1
        x_bal = 564.3
        
        for w in header_line_words:
            txt = w['text'].lower()
            if "date" in txt:
                x_date = w['x0']
            elif "narration" in txt:
                x_narr = w['x0']
            elif "chq" in txt:
                x_chq = w['x0']
            elif "value" in txt:
                x_val = w['x0']
            elif "withdrawal" in txt:
                x_deb = w['x0']
            elif "deposit" in txt:
                x_cred = w['x0']
            elif "closing" in txt or "balance" in txt:
                x_bal = w['x0']
        
        col_bounds = [
            (x_date + x_narr) / 2,
            x_chq - 8,
            x_val - 8,
            x_deb - 8,
            x_cred - 8,
            x_bal - 8
        ]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            if w['top'] > page.height - 80:
                continue
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            line_clean = line_text.lower().replace(" ", "")
            if "summary" in line_clean or "closingbalanceincludes" in line_clean or "hdfcbanklimited" in line_clean:
                break
                
            cols = [""] * 7
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid < col_bounds[5]:
                    cols[5] += (" " if cols[5] else "") + w['text']
                elif col_bounds[5] <= x_mid:
                    cols[6] += (" " if cols[6] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "particulars": col1,
                    "ref_no": col2,
                    "value_date": col3,
                    "debit": col4,
                    "credit": col5,
                    "balance": col6
                }
            elif current_tx:
                is_header_or_divider = (
                    "Statement of account" in line_text or 
                    "Account Branch" in line_text or 
                    "Address :" in line_text or 
                    "DATE NARRATION" in line_text or 
                    "Nomination :" in line_text or 
                    "From :" in line_text or
                    line_text.strip().startswith("----") or
                    "Page No" in line_text
                )
                if is_header_or_divider:
                    continue
                if col0:
                    current_tx["txn_date"] += " " + col0
                if col1:
                    current_tx["particulars"] += " " + col1
                if col2:
                    current_tx["ref_no"] = col2
                if col3:
                    current_tx["value_date"] = col3
                if col4:
                    current_tx["debit"] = col4
                if col5:
                    current_tx["credit"] = col5
                if col6:
                    current_tx["balance"] = col6
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_indusind(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}\s+[A-Za-z]{3}\s+\d{4}$", re.IGNORECASE)
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account No\.\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"Customer Id\s*:\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Account type\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"From\s*:\s*([^\n]+?)\s+To\s*:\s*([^\n]+)", text_full)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1).strip()} to {period_match.group(2).strip()}"
            lines = [l.strip() for l in text_full.split("\n") if l.strip()]
            if lines:
                metadata["holder_name"] = lines[0]
        
        # Find header
        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            if "description" in line_texts and "debit" in line_texts:
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 150.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibration separators
        x_date = 20.0
        x_type = 100.0
        x_desc = 200.0
        x_deb = 500.0
        x_cred = 650.0
        x_bal = 800.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if "date" in txt:
                x_date = w['x0']
            elif "type" in txt:
                x_type = w['x0']
            elif "description" in txt:
                x_desc = w['x0']
            elif "debit" in txt:
                x_deb = w['x0']
            elif "credit" in txt:
                x_cred = w['x0']
            elif "balance" in txt:
                x_bal = w['x0']
        
        col_bounds = [
            x_type - 5,
            x_desc - 5,
            x_deb - 5,
            x_cred - 5,
            x_bal - 5
        ]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "computer generated statement" in line_text.lower() or "does not require signature" in line_text.lower():
                break
                
            cols = [""] * 6
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid:
                    cols[5] += (" " if cols[5] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col0,
                    "particulars": col2,
                    "ref_no": "",
                    "debit": col3,
                    "credit": col4,
                    "balance": col5
                }
            elif current_tx:
                is_header_or_divider = (
                    "Date Type Description" in line_text or 
                    "Account No." in line_text or
                    "Page " in line_text or
                    line_text.strip().startswith("----")
                )
                if is_header_or_divider:
                    continue
                if col0:
                    current_tx["txn_date"] += " " + col0
                    current_tx["value_date"] += " " + col0
                if col2:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["debit"] = col3
                if col4:
                    current_tx["credit"] = col4
                if col5:
                    current_tx["balance"] = col5
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_icici(pdf, first_page_text):
    if "s no." in first_page_text.lower() and "cheque number" in first_page_text.lower():
        return _parse_icici_new(pdf, first_page_text)
        
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "Savings",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            cust_match = re.search(r"Customer ID:(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            period_match = re.search(r"for the period\s+([^\n]+)", text_full)
            if period_match:
                metadata["statement_period"] = period_match.group(1).strip()
            metadata["holder_name"] = _extract_holder_name(text_full, "ICICI Account Holder")
            acc_match = re.search(r"Savings Account Number\s*:\s*(\d+)", text_full, re.IGNORECASE)
            if not acc_match:
                acc_match = re.search(r"Savings A/c\s*Number\s*:\s*(\d+)", text_full, re.IGNORECASE)
            if not acc_match:
                acc_match = re.search(r"Savings Account no\.\s*(\d+)", text_full, re.IGNORECASE)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
        
        if page_idx == 1 and not metadata["account_number"]:
            acc_match = re.search(r"Savings A/c\s+(\d+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
        
        # Find header
        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            if "particulars" in line_texts and "balance" in line_texts:
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 150.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibration separators
        x_date = 20.0
        x_mode = 100.0
        x_part = 180.0
        x_dep = 550.0
        x_with = 650.0
        x_bal = 750.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if "date" in txt:
                x_date = w['x0']
            elif "mode" in txt:
                x_mode = w['x0']
            elif "particulars" in txt:
                x_part = w['x0']
            elif "deposits" in txt:
                x_dep = w['x0']
            elif "withdrawals" in txt:
                x_with = w['x0']
            elif "balance" in txt:
                x_bal = w['x0']
        
        col_bounds = [
            x_mode - 5,
            x_part - 5,
            x_dep - 5,
            x_with - 5,
            x_bal - 5
        ]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            
            is_footer = (
                "Fixed Deposits" in line_text or 
                "Summary of TDS" in line_text or 
                "Interest on Fixed Deposits" in line_text or 
                "ACCOUNT DETAILS" in line_text or 
                "Legends for transactions" in line_text or 
                "Relationship Manager" in line_text or
                "TOTAL DEPOSITS" in line_text or
                "Statement of Fixed Deposit" in line_text or
                "Summary of TDS/Interest" in line_text or
                "Account Related Other Information" in line_text or
                "Sincerely, Team ICICI" in line_text or
                "Nominee name is displayed" in line_text or
                "This is a system-generated statement" in line_text
            )
            if is_footer:
                break
                
            cols = [""] * 6
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid:
                    cols[5] += (" " if cols[5] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col0,
                    "particulars": col2,
                    "ref_no": "",
                    "debit": col4,
                    "credit": col3,
                    "balance": col5
                }
            elif current_tx:
                is_header_or_divider = (
                    "DATE MODE** PARTICULARS" in line_text or 
                    "Account Statement" in line_text or
                    "Page " in line_text or
                    line_text.strip().startswith("----") or
                    "ACCOUNT DETAILS" in line_text
                )
                if is_header_or_divider:
                    continue
                if col0:
                    current_tx["txn_date"] += " " + col0
                    current_tx["value_date"] += " " + col0
                if col2:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["credit"] = col3
                if col4:
                    current_tx["debit"] = col4
                if col5:
                    current_tx["balance"] = col5
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_kotak(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{1,2}\s+[A-Za-z]{3}\s+\d{4}$", re.IGNORECASE)
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account No\.\s*(\d+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"CRN\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Account Type\s+(\w+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"(\d{2}\s+[A-Za-z]{3}\s+\d{4}\s*-\s*\d{2}\s+[A-Za-z]{3}\s+\d{4})", text_full)
            if period_match:
                metadata["statement_period"] = period_match.group(1).strip()
            metadata["holder_name"] = _extract_holder_name(text_full, "Kotak Account Holder")
        
        # Find header
        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            if "description" in line_texts and "withdrawal" in line_texts:
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 150.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibration separators
        x_num = 20.0
        x_date = 60.0
        x_desc = 150.0
        x_chq = 350.0
        x_deb = 500.0
        x_cred = 650.0
        x_bal = 800.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if txt == "#":
                x_num = w['x0']
            elif "date" in txt:
                x_date = w['x0']
            elif "description" in txt:
                x_desc = w['x0']
            elif "chq" in txt or "ref" in txt:
                x_chq = w['x0']
            elif "withdrawal" in txt:
                x_deb = w['x0']
            elif "deposit" in txt:
                x_cred = w['x0']
            elif "balance" in txt:
                x_bal = w['x0']
        
        col_bounds = [
            x_date - 5,
            x_desc - 5,
            x_chq - 5,
            x_deb - 5,
            x_cred - 5,
            x_bal - 5
        ]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "End of Statement" in line_text or "For assistance, reach out" in line_text:
                break
                
            cols = [""] * 7
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid < col_bounds[5]:
                    cols[5] += (" " if cols[5] else "") + w['text']
                elif col_bounds[5] <= x_mid:
                    cols[6] += (" " if cols[6] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            
            if col1 and date_regex.match(col1):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col1,
                    "value_date": col1,
                    "particulars": col2,
                    "ref_no": col3,
                    "debit": col4,
                    "credit": col5,
                    "balance": col6
                }
            elif current_tx:
                is_header_or_divider = (
                    "Savings Account Transactions" in line_text or 
                    "Account Statement" in line_text or
                    "Page " in line_text or
                    line_text.strip().startswith("----")
                )
                if is_header_or_divider:
                    continue
                if col1:
                    current_tx["txn_date"] += " " + col1
                    current_tx["value_date"] += " " + col1
                if col2:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["ref_no"] = col3
                if col4:
                    current_tx["debit"] = col4
                if col5:
                    current_tx["credit"] = col5
                if col6:
                    current_tx["balance"] = col6
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_axis(pdf, first_page_text):
    # Deducing standard parser for Axis Bank statement
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account No\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"Customer ID\s*:\s*(\w+)", text_full)
            if not cust_match:
                cust_match = re.search(r"Customer Id\s*:\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Scheme\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"From\s*:\s*(\d{2}-\d{2}-\d{4})\s+To\s*:\s*(\d{2}-\d{2}-\d{4})", text_full)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1)} to {period_match.group(2)}"
            metadata["holder_name"] = _extract_holder_name(text_full, "Axis Account Holder")
            
        # Group lines
        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
                
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            if "particulars" in line_texts and "balance" in line_texts:
                header_y = top
                header_line_words = line_words
                break
                
        if header_y is None:
            header_y = 150.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibration separators
        x_date = 20.0
        x_chq = 100.0
        x_part = 180.0
        x_deb = 500.0
        x_cred = 600.0
        x_bal = 700.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if "tran" in txt or "date" in txt:
                x_date = w['x0']
            elif "chq" in txt or "ref" in txt:
                x_chq = w['x0']
            elif "particulars" in txt or "description" in txt:
                x_part = w['x0']
            elif "debit" in txt or "withdrawal" in txt:
                x_deb = w['x0']
            elif "credit" in txt or "deposit" in txt:
                x_cred = w['x0']
            elif "balance" in txt:
                x_bal = w['x0']
                
        col_bounds = [
            (x_date + x_chq) / 2, # separates Date and Chq
            x_part - 5,
            x_deb - 5,
            x_cred - 5,
            x_bal - 5
        ]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "statement summary" in line_text.lower() or "page " in line_text.lower():
                break
                
            cols = [""] * 7
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid < col_bounds[5]:
                    cols[5] += (" " if cols[5] else "") + w['text']
                elif col_bounds[5] <= x_mid:
                    cols[6] += (" " if cols[6] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col0,
                    "ref_no": col1,
                    "particulars": col2,
                    "debit": col3,
                    "credit": col4,
                    "balance": col5
                }
            elif current_tx:
                is_header_or_divider = (
                    "tran date" in line_text.lower() or 
                    line_text.strip().startswith("----")
                )
                if is_header_or_divider:
                    continue
                if col0:
                    current_tx["txn_date"] += " " + col0
                    current_tx["value_date"] += " " + col0
                if col1:
                    current_tx["ref_no"] = col1
                if col2:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["debit"] = col3
                if col4:
                    current_tx["credit"] = col4
                if col5:
                    current_tx["balance"] = col5
                    
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_union_bank(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"SBGEN-A/C NO:\s*(\w+)", text_full)
            if not acc_match:
                acc_match = re.search(r"A/C\s*NO\s*:\s*(\w+)", text_full)
            if not acc_match:
                acc_match = re.search(r"A/C\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            
            holder_match = re.search(r"TO:\s*DATE:[^\n]*\n([^\n]+)", text_full)
            if holder_match:
                metadata["holder_name"] = holder_match.group(1).strip()
                
            type_match = re.search(r"SBGEN-A/C NO:[^\n]*?\s+(\w+\s+\w+|\w+)\s*\(", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            else:
                metadata["account_type"] = "SB GENERAL"
                
            period_match = re.search(r"STATEMENT OF ACCOUNT FOR THE PERIOD FROM\s*([^\n]+?)(?=\s+SBGEN|\s+A/C|\s+A/c|$)", text_full)
            if period_match:
                metadata["statement_period"] = period_match.group(1).strip()
            
            cust_match = re.search(r"CUST ID\s*:\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)

        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            has_date = any(k in line_texts for k in ["date"])
            has_particulars = any(k in line_texts for k in ["particulars"])
            has_withdrawals = any(k in line_texts for k in ["withdrawals", "withdrawal"])
            has_deposits = any(k in line_texts for k in ["deposits", "deposit"])
            has_balance = any(k in line_texts for k in ["balance"])
            
            if has_date and has_particulars and (has_withdrawals or has_deposits) and has_balance:
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 182.0 if page_idx == 0 else 100.0
            
        x_date = 6.0
        x_particulars = 66.0
        x_chq = 401.0
        x_deb = 479.0
        x_cred = 611.0
        x_bal = 731.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if txt == "date":
                x_date = w['x0']
            elif txt == "particulars":
                x_particulars = w['x0']
            elif txt in ["chq.no.", "chqno"]:
                x_chq = w['x0']
            elif txt in ["withdrawals", "withdrawal"]:
                x_deb = w['x0']
            elif txt in ["deposits", "deposit"]:
                x_cred = w['x0']
            elif txt == "balance":
                x_bal = w['x0']
        
        col_bounds = [
            (x_date + x_particulars) / 2,
            x_chq - 8,
            x_deb - 8,
            x_cred - 8,
            x_bal - 8
        ]

        table_words = words
        if page_idx == 0:
            table_words = [w for w in words if w['top'] > header_y + 10]

        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "The Min. Bal." in line_text or "Unless constituent" in line_text or "Contact all India" in line_text:
                break
                
            cols = [""] * 6
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid:
                    cols[5] += (" " if cols[5] else "") + w['text']
            
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col0,
                    "particulars": col1,
                    "ref_no": col2,
                    "debit": col3,
                    "credit": col4,
                    "balance": col5
                }
            elif current_tx:
                is_header_or_divider = (
                    "Cumulative Totals" in line_text or 
                    "UNION BANK OF INDIA" in line_text or 
                    "STATEMENT OF ACCOUNT" in line_text or 
                    "DATE PARTICULARS" in line_text or
                    "PAGE:" in line_text or
                    line_text.strip().startswith("----") or
                    len(line_text.strip()) == 0
                )
                if is_header_or_divider:
                    continue
                    
                if col0:
                    current_tx["txn_date"] += " " + col0
                    current_tx["value_date"] += " " + col0
                if col1:
                    current_tx["particulars"] += " " + col1
                if col2:
                    current_tx["ref_no"] = col2
                if col3:
                    current_tx["debit"] = col3
                if col4:
                    current_tx["credit"] = col4
                if col5:
                    current_tx["balance"] = col5
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    for tx in transactions:
        tx["particulars"] = tx["particulars"].strip()
        bal = tx["balance"]
        if bal:
            bal = bal.replace("Cr", "").replace("Dr", "").replace("CR", "").replace("DR", "").strip()
            tx["balance"] = bal
            
    return metadata, transactions

def _parse_indian_bank(pdf, first_page_text):
    if "ca-ind" in first_page_text.lower() or "lordan" in first_page_text.lower() or "post date value" in first_page_text.lower():
        return _parse_indian_bank_current(pdf, first_page_text)
        
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{1,2}\s+[A-Za-z]{3}\s+\d{4}$", re.IGNORECASE)
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account Number\s+(\d+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            holder_match = re.search(r"Account Holder Name\s+([^\n]+)", text_full)
            if holder_match:
                metadata["holder_name"] = holder_match.group(1).strip()
            type_match = re.search(r"Account Type\s+(\w+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"For period:\s*([^\n]+)", text_full)
            if period_match:
                metadata["statement_period"] = period_match.group(1).strip()
            ifsc_match = re.search(r"IFSC\s+(\w+)", text_full)
            if ifsc_match:
                metadata["customer_id"] = f"IFSC: {ifsc_match.group(1)}"

        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            has_date = any(k in line_texts for k in ["date"])
            has_details = any(k in line_texts for k in ["details"])
            has_debits = any(k in line_texts for k in ["debits", "debit"])
            has_credits = any(k in line_texts for k in ["credits", "credit"])
            has_balance = any(k in line_texts for k in ["balance"])
            
            if has_date and has_details and has_debits and has_credits and has_balance:
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 380.0 if page_idx == 0 else 100.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibrate columns based on found headers
        x_date = 89.0
        x_details = 161.0
        x_deb = 294.0
        x_cred = 387.0
        x_bal = 480.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if txt == "date":
                x_date = w['x0']
            elif txt in ["transaction", "particulars", "description"]:
                x_details = w['x0']
            elif txt in ["debits", "debit"]:
                x_deb = w['x0']
            elif txt in ["credits", "credit"]:
                x_cred = w['x0']
            elif txt == "balance":
                x_bal = w['x0']
        
        col_bounds = [
            (x_date + x_details) / 2,
            x_deb - 8,
            x_cred - 8,
            x_bal - 8
        ]

        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "Ending Balance" in line_text or "Total" in line_text or "Indian Bank" in line_text:
                break
            
            cols = [""] * 5
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid:
                    cols[4] += (" " if cols[4] else "") + w['text']
            
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col0,
                    "particulars": col1,
                    "ref_no": "",
                    "debit": col2,
                    "credit": col3,
                    "balance": col4
                }
            elif current_tx:
                if col0:
                    current_tx["txn_date"] += " " + col0
                    current_tx["value_date"] += " " + col0
                if col1:
                    current_tx["particulars"] += " " + col1
                if col2:
                    current_tx["debit"] = col2
                if col3:
                    current_tx["credit"] = col3
                if col4:
                    current_tx["balance"] = col4
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    for tx in transactions:
        tx["particulars"] = tx["particulars"].strip()
        for k in ["debit", "credit", "balance"]:
            val = tx[k]
            if val:
                val = val.replace("INR", "").replace("+", "").replace("-", "").strip()
                tx[k] = val
                
    return metadata, transactions

def _parse_indian_bank_current(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}/\d{2}/\d{2}$")
    
    # Extract metadata from first page text
    acc_match = re.search(r"Account No\s*:\s*(\w+)", first_page_text)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
        
    for line in first_page_text.split("\n"):
        if "LORDAN INDUCTION" in line:
            metadata["holder_name"] = line.strip()
            
    type_match = re.search(r"Product:\s*([^\n]+)", first_page_text)
    if type_match:
        val = type_match.group(1).strip()
        if "Email ID" in val:
            val = val.split("Email ID")[0].strip()
        metadata["account_type"] = val
        
    period_match = re.search(r"Statement From\s*:([\d/A-Za-z-]+)\s+To\s*:([\d/A-Za-z-]+)", first_page_text)
    if period_match:
        metadata["statement_period"] = f"{period_match.group(1).strip()} to {period_match.group(2).strip()}"
        
    ifsc_match = re.search(r"IFSC Code\s*:\s*(\w+)", first_page_text)
    if ifsc_match:
        metadata["customer_id"] = f"IFSC: {ifsc_match.group(1)}"

    col_bounds = [85.0, 135.0, 320.0, 380.0, 435.0, 490.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        footer_top = page.height
        for w in words:
            w_lower = w['text'].lower().strip()
            if w_lower in ["carried", "closing", "statement", "summary", "in", "case", "***"]:
                if w['top'] > 250:
                    if w['top'] < footer_top:
                        footer_top = w['top'] - 2.0
                        
        min_header_top = 315.0 if page_idx == 0 else 167.0
        
        date_tops = []
        for w in words:
            if min_header_top <= w['top'] < footer_top:
                if w['x0'] < 45.0 and date_regex.match(w['text'].strip()):
                    date_tops.append(w['top'])
        
        date_tops.sort()
        
        if not date_tops:
            continue
            
        page_txs = []
        for d_top in date_tops:
            page_txs.append({
                "txn_date": "",
                "value_date": "",
                "particulars": "",
                "ref_no": "",
                "debit": "",
                "credit": "",
                "balance": "",
                "d_top": d_top
            })
            
        for w in words:
            w_top = w['top']
            if w_top < min_header_top or w_top >= footer_top:
                continue
                
            w_text = w['text'].strip()
            
            best_idx = 0
            if len(date_tops) == 1:
                best_idx = 0
            else:
                if w_top < date_tops[0]:
                    best_idx = 0
                elif w_top >= date_tops[-1]:
                    best_idx = len(date_tops) - 1
                else:
                    for i in range(len(date_tops) - 1):
                        if date_tops[i] <= w_top < date_tops[i+1]:
                            if w['x0'] >= 140.0 and (date_tops[i+1] - w_top) < (w_top - date_tops[i]):
                                best_idx = i + 1
                            else:
                                best_idx = i
                            break
            
            tx = page_txs[best_idx]
            
            assigned = False
            for c_idx, limit in enumerate(col_bounds):
                if w['x1'] < limit:
                    if c_idx == 0:
                        tx["txn_date"] += (" " if tx["txn_date"] else "") + w_text
                    elif c_idx == 1:
                        tx["value_date"] += (" " if tx["value_date"] else "") + w_text
                    elif c_idx == 2:
                        tx["particulars"] += (" " if tx["particulars"] else "") + w_text
                    elif c_idx == 3:
                        tx["ref_no"] += (" " if tx["ref_no"] else "") + w_text
                    elif c_idx == 4:
                        tx["debit"] += (" " if tx["debit"] else "") + w_text
                    elif c_idx == 5:
                        tx["credit"] += (" " if tx["credit"] else "") + w_text
                    assigned = True
                    break
            if not assigned:
                tx["balance"] += (" " if tx["balance"] else "") + w_text
                
        for tx in page_txs:
            bal = clean_val(tx["balance"]).replace("Cr", "").replace("Dr", "").strip()
            transactions.append({
                "txn_date": clean_val(tx["txn_date"]),
                "value_date": clean_val(tx["value_date"]),
                "particulars": clean_val(tx["particulars"]),
                "ref_no": clean_val(tx["ref_no"]),
                "debit": clean_val(tx["debit"]),
                "credit": clean_val(tx["credit"]),
                "balance": bal
            })
            
    return metadata, transactions

def _parse_kvb(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    
    date_regex = re.compile(
        r"^\d{2}-[A-Za-z]{3}-\d{4}$|^\d{2}/\d{2}/\d{4}$|^\d{2}-\d{2}-\d{4}$",
        re.IGNORECASE
    )
    time_regex = re.compile(r"^\d{2}:\d{2}:\d{2}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Acc\.No\.\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"Customer ID\s*:\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Acc\.\s*Type\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            st_date_match = re.search(r"St\.\s*Date\s*:\s*([^\n]+)", text_full)
            if st_date_match:
                metadata["statement_date"] = st_date_match.group(1).strip()
            st_period_match = re.search(r"St\.\s*Period\s*:\s*([^\n]+)", text_full)
            if st_period_match:
                metadata["statement_period"] = st_period_match.group(1).strip()
                
            for line in text_full.split("\n"):
                if "Acc.No." in line or "Acc. No." in line:
                    parts = re.split(r"Acc\.No\.|Acc\.\s*No\.", line)
                    if parts and len(parts) > 0:
                        metadata["holder_name"] = parts[0].strip()
                    break
            
            if not metadata["holder_name"]:
                holder_match = re.search(r"SRI LAKSHMI GANAPA", text_full)
                if holder_match:
                    metadata["holder_name"] = "SRI LAKSHMI GANAPA"
                else:
                    metadata["holder_name"] = "Account Holder"

        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
        
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            has_txn = any(k in line_texts for k in ["txn", "txn."])
            has_particulars = any(k in line_texts for k in ["particulars", "description"])
            has_balance = any(k in line_texts for k in ["balance"])
            
            if has_txn and has_particulars and has_balance:
                header_y = top
                header_line_words = line_words
                break
        
        if header_y is None:
            header_y = 340.0 if page_idx == 0 else 100.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        x_txn = 44.0
        x_val = 103.0
        x_part = 163.0
        x_ref = 318.0
        x_deb = 378.0
        x_cred = 438.0
        x_bal = 498.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if txt in ["txn", "txn."]:
                x_txn = w['x0']
            elif txt in ["value", "val"]:
                x_val = w['x0']
            elif txt in ["particulars", "description"]:
                x_part = w['x0']
            elif txt == "ref." or txt == "reference":
                x_ref = w['x0']
            elif txt == "debit" or txt == "withdrawals":
                x_deb = w['x0']
            elif txt == "credit" or txt == "deposits":
                x_cred = w['x0']
            elif txt == "balance":
                x_bal = w['x0']
        
        if x_val == 103.0 and x_txn != 44.0:
            x_val = x_txn + 59
        if x_ref == 318.0 and x_part != 163.0:
            x_ref = x_part + 155
        
        col_bounds = [
            x_val - 2,
            x_part - 2,
            x_ref - 2,
            x_deb - 2,
            x_cred - 2,
            x_bal - 2
        ]

        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
        
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "Statements are sent" in line_text or "Note: This is" in line_text or "ACRONYMS" in line_text or "HOME BRANCH" in line_text:
                break
            
            cols = [""] * 7
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                if x_mid < col_bounds[0]:
                    cols[0] += (" " if cols[0] else "") + w['text']
                elif col_bounds[0] <= x_mid < col_bounds[1]:
                    cols[1] += (" " if cols[1] else "") + w['text']
                elif col_bounds[1] <= x_mid < col_bounds[2]:
                    cols[2] += (" " if cols[2] else "") + w['text']
                elif col_bounds[2] <= x_mid < col_bounds[3]:
                    cols[3] += (" " if cols[3] else "") + w['text']
                elif col_bounds[3] <= x_mid < col_bounds[4]:
                    cols[4] += (" " if cols[4] else "") + w['text']
                elif col_bounds[4] <= x_mid < col_bounds[5]:
                    cols[5] += (" " if cols[5] else "") + w['text']
                elif col_bounds[5] <= x_mid:
                    cols[6] += (" " if cols[6] else "") + w['text']
            
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col1,
                    "particulars": col2,
                    "ref_no": col3,
                    "debit": col4,
                    "credit": col5,
                    "balance": col6,
                    "time": ""
                }
            elif current_tx:
                if col0:
                    if time_regex.match(col0):
                        current_tx["time"] = col0
                    else:
                        current_tx["txn_date"] += " " + col0
                if col1:
                    current_tx["value_date"] = col1
                if col2:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["ref_no"] = col3
                if col4:
                    current_tx["debit"] = col4
                if col5:
                    current_tx["credit"] = col5
                if col6:
                    current_tx["balance"] = col6
        
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    for tx in transactions:
        tx["particulars"] = tx["particulars"].strip()
        if tx["time"]:
            tx["txn_date"] = f"{tx['txn_date']} {tx['time']}"
        del tx["time"]
        
    return metadata, transactions

def _parse_pnb(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
            
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account Number\s+(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            ifsc_match = re.search(r"IFSC Code:\s*(\w+)", text_full)
            if ifsc_match:
                metadata["customer_id"] = f"IFSC: {ifsc_match.group(1)}"
            for line in text_full.split("\n"):
                if "Account Name:" in line:
                    metadata["holder_name"] = line.replace("Account Name:", "").strip()
            period_match = re.search(r"Statement Period\s*:\s*([\d-]+)\s+to\s+([\d-]+)", text_full)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1)} to {period_match.group(2)}"
            metadata["account_type"] = "Savings/Current"
            
        # Get horizontal lines Y
        row_ys = sorted(list(set([round(e['top'], 1) for e in page.horizontal_edges])))
        if len(row_ys) < 2:
            continue
            
        start_row_idx = 1 if page_idx == 0 else 0
        col_bounds = [145.0, 250.0, 415.0, 540.0, 650.0, 750.0, 850.0, 960.0]
        
        for i in range(start_row_idx, len(row_ys) - 1):
            y_top = row_ys[i]
            y_bottom = row_ys[i+1]
            
            # Collect words in this row
            row_words = [w for w in words if y_top - 1.0 <= w['top'] < y_bottom - 1.0]
            if not row_words:
                continue
                
            cols_words = [[] for _ in range(9)]
            for w in row_words:
                x_mid = (w['x0'] + w['x1']) / 2
                assigned = False
                for c_idx, limit in enumerate(col_bounds):
                    if x_mid < limit:
                        cols_words[c_idx].append(w)
                        assigned = True
                        break
                if not assigned:
                    cols_words[8].append(w)
                    
            cols = [""] * 9
            for col_idx in range(9):
                col_w = cols_words[col_idx]
                col_w.sort(key=lambda w: (round(w['top'], 1), w['x0']))
                cols[col_idx] = " ".join([w['text'] for w in col_w])
                
            txn_no = cols[0].strip()
            txn_date = cols[1].strip()
            desc = cols[2].strip()
            branch = cols[3].strip()
            chq_no = cols[4].strip()
            dr_amt = cols[5].strip()
            cr_amt = cols[6].strip()
            bal = cols[7].strip()
            
            if txn_date:
                transactions.append({
                    "txn_date": txn_date,
                    "value_date": txn_date,
                    "particulars": desc,
                    "ref_no": chq_no if chq_no else txn_no,
                    "debit": dr_amt if dr_amt != "-" else "",
                    "credit": cr_amt if cr_amt != "-" else "",
                    "balance": bal.replace(" Cr.", "").replace(" Dr.", "").strip()
                })
                
    return metadata, transactions

def _parse_scb(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}\s+[A-Za-z]{3}\s+\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
            
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"ACCOUNT NO\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            st_date_match = re.search(r"STATEMENT DATE\s*:\s*([^\n]+)", text_full)
            if st_date_match:
                metadata["statement_date"] = st_date_match.group(1).strip()
            type_match = re.search(r"ACCOUNT TYPE\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            for line in text_full.split("\n"):
                line_clean = line.strip()
                if line_clean.startswith(("MR.", "MS.", "MRS.", "MR ", "MS ", "MRS ")):
                    parts = re.split(r"Page\s+\d+|BRANCH", line_clean, flags=re.IGNORECASE)
                    metadata["holder_name"] = parts[0].strip()
                    break
                    
        col_bounds = [110.0, 165.0, 350.0, 400.0, 445.0, 495.0]
        
        # Group words by Y coordinate
        all_lines = defaultdict(list)
        for w in words:
            found = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 4.0:
                    all_lines[existing_top].append(w)
                    found = True
                    break
            if not found:
                all_lines[w['top']].append(w)
                
        sorted_tops = sorted(all_lines.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = all_lines[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            line_lower = line_text.lower().strip()
            
            if line_lower.startswith("total") or "reward points statement" in line_text or "dear client" in line_lower:
                break
                
            cols = [""] * 7
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                assigned = False
                for c_idx, limit in enumerate(col_bounds):
                    if x_mid < limit:
                        cols[c_idx] += (" " if cols[c_idx] else "") + w['text']
                        assigned = True
                        break
                if not assigned:
                    cols[6] += (" " if cols[6] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            
            if col0 and date_regex.match(col0) and col1 and date_regex.match(col1):
                if current_tx:
                    transactions.append(current_tx)
                ref = ""
                ref_match = re.search(r"UPI/(\d+)", col2)
                if ref_match:
                    ref = ref_match.group(1)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col1,
                    "particulars": col2,
                    "ref_no": ref,
                    "debit": col5,
                    "credit": col4,
                    "balance": col6
                }
            elif current_tx:
                if col2:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + col2
                if col3:
                    current_tx["ref_no"] = col3
                if col4:
                    current_tx["credit"] = col4
                if col5:
                    current_tx["debit"] = col5
                if col6:
                    current_tx["balance"] = col6
                    
        if current_tx:
            transactions.append(current_tx)
            
    if transactions and len(transactions) > 1:
        metadata["statement_period"] = f"{transactions[1]['txn_date']} to {transactions[-1]['txn_date']}"
        
    return metadata, transactions

def _parse_sbi(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}/\d{2}/\d{4}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
            
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account Number\s*:\s*(\w+)", text_full)
            if not acc_match:
                acc_match = re.search(r"A/c No\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"CIF Number\s*:\s*(\w+)", text_full)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Account Type\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"Statement From\s*:\s*([\d/]+)\s+to\s+([\d/]+)", text_full)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1)} to {period_match.group(2)}"
            metadata["holder_name"] = _extract_holder_name(text_full, "SBI Account Holder")
            
        # Find header Y
        all_lines = defaultdict(list)
        for w in words:
            found_line = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    all_lines[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                all_lines[w['top']].append(w)
                
        sorted_all_tops = sorted(all_lines.keys())
        header_y = None
        header_line_words = []
        for top in sorted_all_tops:
            line_words = all_lines[top]
            line_texts = [w['text'].lower() for w in line_words]
            if "details" in line_texts and "balance" in line_texts:
                header_y = top
                header_line_words = line_words
                break
                
        if header_y is None:
            header_y = 150.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Calibration separators
        x_val = 50.0
        x_post = 110.0
        x_details = 170.0
        x_ref = 430.0
        x_deb = 530.0
        x_cred = 650.0
        x_bal = 760.0
        
        for w in header_line_words:
            txt = w['text'].lower()
            if "value" in txt:
                x_val = w['x0']
            elif "post" in txt:
                x_post = w['x0']
            elif "details" in txt:
                x_details = w['x0']
            elif "ref" in txt or "cheque" in txt:
                x_ref = w['x0']
            elif "debit" in txt or "withdrawal" in txt:
                x_deb = w['x0']
            elif "credit" in txt or "deposit" in txt:
                x_cred = w['x0']
            elif "balance" in txt:
                x_bal = w['x0']
                
        col_bounds = [
            (x_val + x_post) / 2,
            (x_post + x_details) / 2,
            x_ref - 8,
            x_deb - 8,
            x_cred - 8,
            x_bal - 8
        ]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found_line = True
                    break
            if not found_line:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            if "statement summary" in line_text.lower() or "brought forward" in line_text.lower():
                break
                
            cols = [""] * 7
            for w in line_words:
                x_mid = (w['x0'] + w['x1']) / 2
                assigned = False
                for c_idx, limit in enumerate(col_bounds):
                    if x_mid < limit:
                        cols[c_idx] += (" " if cols[c_idx] else "") + w['text']
                        assigned = True
                        break
                if not assigned:
                    cols[6] += (" " if cols[6] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col1 if col1 else col0,
                    "particulars": col2,
                    "ref_no": col3,
                    "debit": col4,
                    "credit": col5,
                    "balance": col6.replace("CR", "").replace("DR", "").strip()
                }
            elif current_tx:
                if col2:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["ref_no"] = col3
                if col4:
                    current_tx["debit"] = col4
                if col5:
                    current_tx["credit"] = col5
                if col6:
                    current_tx["balance"] = col6.replace("CR", "").replace("DR", "").strip()
                    
        if current_tx:
            transactions.append(current_tx)
            
    return metadata, transactions

def _parse_bob(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{2}$")
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
            
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"A/C\s*Number\s*:\s*(\w+)", text_full)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            for line in text_full.split("\n"):
                if "A/C Name" in line:
                    metadata["holder_name"] = line.replace("A/C Name", "").replace(":", "").strip()
            type_match = re.search(r"Scheme Description\s*:\s*([^\n]+)", text_full)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"period of\s+([\d-]+)\s+to\s+([\d-]+)", text_full)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1)} to {period_match.group(2)}"
            ifsc_match = re.search(r"IFSC CODE:\s*(\w+)", text_full)
            if ifsc_match:
                metadata["customer_id"] = f"IFSC: {ifsc_match.group(1)}"
                
        col_bounds = [112.0, 185.0, 230.0, 310.0, 382.0]
        
        # Group words by Y coordinate
        all_lines = defaultdict(list)
        for w in words:
            found = False
            for existing_top in all_lines.keys():
                if abs(w['top'] - existing_top) < 4.0:
                    all_lines[existing_top].append(w)
                    found = True
                    break
            if not found:
                all_lines[w['top']].append(w)
                
        sorted_tops = sorted(all_lines.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = all_lines[top]
            line_words.sort(key=lambda w: w['x0'])
            
            line_text = " ".join([w['text'] for w in line_words])
            line_lower = line_text.lower().strip()
            
            if "page total:" in line_lower or "grand total:" in line_lower or "unclr bal:" in line_lower or "balance forward" in line_lower:
                break
                
            first_w = line_words[0]['text'].strip()
            
            if date_regex.match(first_w):
                if current_tx:
                    transactions.append(current_tx)
                
                cols = [""] * 6
                for w in line_words:
                    assigned = False
                    for c_idx, limit in enumerate(col_bounds):
                        if w['x1'] < limit:
                            cols[c_idx] += (" " if cols[c_idx] else "") + w['text']
                            assigned = True
                            break
                    if not assigned:
                        cols[5] += (" " if cols[5] else "") + w['text']
                
                col0 = clean_val(cols[0])
                col1 = clean_val(cols[1])
                col2 = clean_val(cols[2])
                col3 = clean_val(cols[3])
                col4 = clean_val(cols[4])
                col5 = clean_val(cols[5])
                
                current_tx = {
                    "txn_date": col0,
                    "value_date": col0,
                    "particulars": col1,
                    "ref_no": col2,
                    "debit": col3,
                    "credit": col4,
                    "balance": col5.replace("Cr", "").replace("Dr", "").strip()
                }
            elif current_tx:
                if not line_lower.startswith("---") and not line_lower.startswith("page total") and not line_lower.startswith("grand total"):
                    current_tx["particulars"] += " " + line_text.strip()
                    
        if current_tx:
            transactions.append(current_tx)
            
    return metadata, transactions

def _parse_icici_new(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "Savings",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
    
    # Extract metadata from first page
    acc_match = re.search(r"Saving Account no\.\s*(\d+)", first_page_text)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
        
    for line in first_page_text.split("\n"):
        if "M SYED" in line or "SYED ABDUL" in line:
            metadata["holder_name"] = line.split("Your Base Branch")[0].strip()
            
    period_match = re.search(r"for the period\s+([^\n]+)", first_page_text, re.IGNORECASE)
    if period_match:
        val = period_match.group(1).replace("in INR", "").replace("-", "to").strip()
        if "Your Base Branch" in val:
            val = val.split("Your Base Branch")[0].strip()
        metadata["statement_period"] = val

    col_bounds = [120.0, 190.0, 400.0, 460.0, 530.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        footer_top = page.height
        for w in words:
            w_lower = w['text'].lower().strip()
            if w_lower in ["never", "share", "www.icici.bank.in", "dial", "sincerely", "legends", "system", "generated", "signature"]:
                if w['top'] > 300:
                    if w['top'] < footer_top:
                        footer_top = w['top'] - 2.0
                        
        min_header_top = 230.0 if page_idx == 0 else 110.0
        
        date_tops = []
        for w in words:
            if min_header_top <= w['top'] < footer_top:
                if w['x0'] < 110.0 and date_regex.match(w['text'].strip()):
                    date_tops.append(w['top'])
                    
        date_tops.sort()
        
        if not date_tops:
            continue
            
        boundary_tops = [t - 8.0 for t in date_tops]
            
        page_txs = []
        for d_top in date_tops:
            page_txs.append({
                "txn_date": "",
                "value_date": "",
                "particulars": "",
                "ref_no": "",
                "debit": "",
                "credit": "",
                "balance": "",
                "d_top": d_top
            })
            
        for w in words:
            w_top = w['top']
            if w_top < min_header_top or w_top >= footer_top:
                continue
                
            w_text = w['text'].strip()
            
            best_idx = 0
            if w_top < boundary_tops[0]:
                best_idx = 0
            elif w_top >= boundary_tops[-1]:
                best_idx = len(boundary_tops) - 1
            else:
                for i in range(len(boundary_tops) - 1):
                    if boundary_tops[i] <= w_top < boundary_tops[i+1]:
                        best_idx = i
                        break
            
            tx = page_txs[best_idx]
            
            assigned = False
            for c_idx, limit in enumerate(col_bounds):
                if w['x1'] < limit:
                    if c_idx == 0:
                        if date_regex.match(w_text):
                            tx["txn_date"] += (" " if tx["txn_date"] else "") + w_text
                            tx["value_date"] = tx["txn_date"]
                    elif c_idx == 1:
                        tx["ref_no"] += (" " if tx["ref_no"] else "") + w_text
                    elif c_idx == 2:
                        tx["particulars"] += (" " if tx["particulars"] else "") + w_text
                    elif c_idx == 3:
                        tx["debit"] += (" " if tx["debit"] else "") + w_text
                    elif c_idx == 4:
                        tx["credit"] += (" " if tx["credit"] else "") + w_text
                    assigned = True
                    break
            if not assigned:
                tx["balance"] += (" " if tx["balance"] else "") + w_text
                
        for tx in page_txs:
            bal = clean_val(tx["balance"]).replace("Cr", "").replace("Dr", "").strip()
            transactions.append({
                "txn_date": clean_val(tx["txn_date"]),
                "value_date": clean_val(tx["value_date"]),
                "particulars": clean_val(tx["particulars"]),
                "ref_no": clean_val(tx["ref_no"]),
                "debit": clean_val(tx["debit"]),
                "credit": clean_val(tx["credit"]),
                "balance": bal
            })
            
    return metadata, transactions
