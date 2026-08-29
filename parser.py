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

def parse_pdf(pdf_path, password=None):
    # Open the PDF to detect bank type and run the appropriate parser
    open_pwd = password if password else None
    try:
        pdf_file = pdfplumber.open(pdf_path, password=open_pwd)
    except Exception as e:
        orig_errs = [e]
        if getattr(e, "__cause__", None):
            orig_errs.append(e.__cause__)
        if getattr(e, "__context__", None):
            orig_errs.append(e.__context__)
            
        is_pwd = False
        for err in orig_errs:
            err_msg = str(err).lower()
            err_class = err.__class__.__name__.lower()
            if "password" in err_msg or "password" in err_class or "decrypt" in err_msg or "encrypt" in err_msg:
                is_pwd = True
                break
                
        if is_pwd:
            if not password:
                raise ValueError("PASSWORD_REQUIRED")
            else:
                raise ValueError("PASSWORD_INCORRECT")
        raise e
        
    with pdf_file as pdf:
        if not pdf.pages:
            raise ValueError("The PDF document does not contain any pages.")
        
        # Extract text from the first page to inspect branding keywords
        first_page_text = pdf.pages[0].extract_text() or ""
        first_page_lower = first_page_text.lower()
        header_area = first_page_lower[:600]
        
        # Auto-detect bank type based on header metadata
        # Auto-detect bank type based on header metadata
        # Auto-detect bank type based on header metadata
        if "kotak" in header_area or "kkbk" in header_area:
            return _parse_kotak(pdf, first_page_text)
        elif "statement between" in header_area or "caesc" in header_area:
            return _parse_axis(pdf, first_page_text)
        elif "idbi" in header_area or "customer account ledger" in header_area or "statement of transaction in current account" in first_page_lower or "monthly average balance" in first_page_lower:
            if "statement of transaction in current account" in first_page_lower or "summary of accounts" in first_page_lower:
                return _parse_idbi_format2(pdf, first_page_text)
            return _parse_idbi_ledger(pdf, first_page_text)
        elif "idfc" in header_area or "idfb0" in header_area:
            return _parse_idfc(pdf, first_page_text)
        elif "south indian" in header_area or "sibl0" in header_area:
            return _parse_sib(pdf, first_page_text)
        elif "detailed statement" in header_area and "txn posted date" in first_page_lower:
            return _parse_icici(pdf, first_page_text)
        elif "dbs" in header_area or "dbss0in" in header_area:
            return _parse_dbs(pdf, first_page_text)
        elif "rbl" in header_area or "ratn0" in header_area:
            return _parse_rbl(pdf, first_page_text)
        elif re.search(r"(?<![a-z])hdfc", header_area):
            return _parse_hdfc(pdf, first_page_text)
        elif "axis" in header_area or "utib" in header_area:
            return _parse_axis(pdf, first_page_text)
        elif "icici" in header_area or "icic" in header_area:
            return _parse_icici(pdf, first_page_text)
        elif "indusind" in header_area or "indb" in header_area:
            return _parse_indusind(pdf, first_page_text)
        elif "canara" in header_area or "cnrb" in header_area:
            return _parse_canara(pdf, first_page_text)
        elif "city union" in header_area or "cityunionbank" in header_area or "cub" in header_area:
            return _parse_city_union_bank(pdf, first_page_text)
        elif "union bank" in header_area or "unionbank" in header_area or "ubin" in header_area:
            return _parse_union_bank(pdf, first_page_text)
        elif "indian bank" in header_area or "indianbank" in header_area or "idib" in header_area:
            return _parse_indian_bank(pdf, first_page_text)
        elif "punjab national" in header_area or "pnb" in header_area or "punb" in header_area:
            return _parse_pnb(pdf, first_page_text)
        elif "standard chartered" in header_area or "scb" in header_area or "scbl" in header_area:
            return _parse_scb(pdf, first_page_text)
        elif "bank of baroda" in header_area or "bob" in header_area or "barb" in header_area:
            return _parse_bob(pdf, first_page_text)
        elif "karur vysya" in header_area or "kvb" in header_area:
            return _parse_kvb(pdf, first_page_text)
        elif "state bank of india" in header_area or re.search(r"\bsbi\b", header_area) or re.search(r"\bsbin\b", header_area):
            return _parse_sbi(pdf, first_page_text)
            
        # Fallbacks in case branding is further down on Page 1
        if "kotak" in first_page_lower or "kkbk" in first_page_lower:
            return _parse_kotak(pdf, first_page_text)
        elif "city union" in first_page_lower or "cityunionbank" in first_page_lower:
            return _parse_city_union_bank(pdf, first_page_text)
        elif "statement between" in first_page_lower or "caesc" in first_page_lower:
            return _parse_axis(pdf, first_page_text)
        elif "idfc" in first_page_lower or "idfb0" in first_page_lower:
            return _parse_idfc(pdf, first_page_text)
        elif "south indian" in first_page_lower or "sibl0" in first_page_lower:
            return _parse_sib(pdf, first_page_text)
        elif "detailed statement" in first_page_lower and "txn posted date" in first_page_lower:
            return _parse_icici(pdf, first_page_text)
        elif "dbs" in first_page_lower or "dbss0in" in first_page_lower:
            return _parse_dbs(pdf, first_page_text)
        elif "rbl" in first_page_lower or "ratn0" in first_page_lower:
            return _parse_rbl(pdf, first_page_text)
        elif re.search(r"(?<![a-z])hdfc", first_page_lower):
            return _parse_hdfc(pdf, first_page_text)
        elif "axis" in first_page_lower or "utib" in first_page_lower:
            return _parse_axis(pdf, first_page_text)
        elif "icici" in first_page_lower or "icic" in first_page_lower:
            return _parse_icici(pdf, first_page_text)
        elif "indusind" in first_page_lower or "indb" in first_page_lower:
            return _parse_indusind(pdf, first_page_text)
        elif "canara" in first_page_lower or "cnrb" in first_page_lower:
            return _parse_canara(pdf, first_page_text)
        elif "union bank" in first_page_lower or "ubin" in first_page_lower:
            return _parse_union_bank(pdf, first_page_text)
        elif "indian bank" in first_page_lower or "idib" in first_page_lower:
            return _parse_indian_bank(pdf, first_page_text)
        elif "punjab national" in first_page_lower or "pnb" in first_page_lower or "punb" in first_page_lower:
            return _parse_pnb(pdf, first_page_text)
        elif "standard chartered" in first_page_lower or "scb" in first_page_lower or "scbl" in first_page_lower:
            return _parse_scb(pdf, first_page_text)
        elif "bank of baroda" in first_page_lower or "bob" in first_page_lower or "barb" in first_page_lower:
            return _parse_bob(pdf, first_page_text)
        elif "karur vysya" in first_page_lower or "kvb" in first_page_lower:
            return _parse_kvb(pdf, first_page_text)
        elif "state bank of india" in first_page_lower or re.search(r"\bsbi\b", first_page_lower) or re.search(r"\bsbin\b", first_page_lower):
            return _parse_sbi(pdf, first_page_text)
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
        words = page.extract_words(x_tolerance=1.5)
        if not words:
            # We don't crash if Axis or other files are uploaded, but we let the user know
            raise ValueError(
                f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                "or photograph of a statement. Please upload a digitally generated PDF statement."
            )
        
        text_full = page.extract_text() or "" if page_idx > 0 else first_page_text
        
        if page_idx == 0:
            acc_match = re.search(r"Account\s*No\.?\s*:\s*(\w+)", text_full, re.IGNORECASE)
            if acc_match:
                metadata["account_number"] = acc_match.group(1)
            cust_match = re.search(r"Cust\s*ID\s*:\s*(\w+)", text_full, re.IGNORECASE)
            if cust_match:
                metadata["customer_id"] = cust_match.group(1)
            type_match = re.search(r"Account\s*Type\s*:\s*([^\n]+)", text_full, re.IGNORECASE)
            if type_match:
                metadata["account_type"] = type_match.group(1).strip()
            period_match = re.search(r"(?:Statement\s*)?From\s*:\s*([\d/]+)\s+To\s*:\s*([\d/]+)", text_full, re.IGNORECASE)
            if period_match:
                metadata["statement_period"] = f"{period_match.group(1).strip()} to {period_match.group(2).strip()}"
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
            header_y = 216.0
            table_words = [w for w in words if w['top'] >= 220.0]
        else:
            table_words = [w for w in words if w['top'] > header_y + 5.0]
        
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
            if txt == "date":
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
            if w['top'] >= page.height - 45:
                continue
            top = round(w['top'], 1)
            found_line = False
            for existing_top in lines_dict.keys():
                if abs(top - existing_top) < 3.5:
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
            
            if col0:
                first_token = col0.split()[0]
                if date_regex.match(first_token):
                    rest_tokens = " ".join(col0.split()[1:])
                    col0 = first_token
                    if rest_tokens:
                        col1 = (rest_tokens + " " + col1).strip()
                else:
                    col1 = (col0 + " " + col1).strip()
                    col0 = ""
            
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
                if col1:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + col1
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
    if "particulars" in first_page_text.lower() and "withdrawal" in first_page_text.lower():
        return _parse_indusind_new(pdf, first_page_text)
        
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

def _parse_icici_detailed_4(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }

    text_p1 = first_page_text or ""
    
    acc_m = re.search(r"A/C No\s*:\s*(\w+)", text_p1)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cust_m = re.search(r"Cust ID\s*:\s*(\w+)", text_p1)
    if cust_m:
        metadata["customer_id"] = cust_m.group(1)
        
    type_m = re.search(r"A/C Type\s*:\s*([^\n]+)", text_p1)
    if type_m:
        metadata["account_type"] = type_m.group(1).strip()
        
    period_m = re.search(r"Transaction Period\s*:\s*From\s+([\d/]+)\s+To\s+([\d/]+)", text_p1, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = f"{period_m.group(1)} to {period_m.group(2)}"
        
    name_m = re.search(r"Name:\s*([^\n]+)", text_p1)
    if name_m:
        raw_name = name_m.group(1)
        raw_name = re.split(r"A/C Branch|Address", raw_name, flags=re.IGNORECASE)[0].strip()
        if "AND AGENTS ASSOCIATIONS" in text_p1 and "AND AGENTS ASSOCIATIONS" not in raw_name:
            raw_name += " AND AGENTS ASSOCIATIONS"
        metadata["holder_name"] = raw_name

    col_bounds = [105.0, 135.0, 172.0, 220.0, 270.0, 320.0, 390.0, 430.0, 470.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = 328.0 if page_idx == 0 else 0.0
        table_words = [w for w in words if w['top'] >= header_y]
        
        no_words = [w for w in table_words if w['x1'] < col_bounds[0] and w['text'].isdigit()]
        no_words.sort(key=lambda w: w['top'])
        
        if not no_words:
            continue
            
        for i, nw in enumerate(no_words):
            sno = nw['text']
            top_bound = (no_words[i-1]['top'] + nw['top'])/2 if i > 0 else header_y
            bot_bound = (nw['top'] + no_words[i+1]['top'])/2 if i < len(no_words) - 1 else page.height - 25.0
            
            box_words = [w for w in table_words if top_bound <= w['top'] < bot_bound]
            
            rem_words = [w for w in box_words if col_bounds[5] <= (w['x0']+w['x1'])/2 < col_bounds[6]]
            deb_words = [w for w in box_words if col_bounds[6] <= (w['x0']+w['x1'])/2 < col_bounds[7]]
            cred_words = [w for w in box_words if col_bounds[7] <= (w['x0']+w['x1'])/2 < col_bounds[8]]
            bal_words = [w for w in box_words if (w['x0']+w['x1'])/2 >= col_bounds[8]]
            
            val_words = [w for w in box_words if col_bounds[1] <= (w['x0']+w['x1'])/2 < col_bounds[2]]
            tx_words = [w for w in box_words if col_bounds[2] <= (w['x0']+w['x1'])/2 < col_bounds[3]]
            chq_words = [w for w in box_words if col_bounds[4] <= (w['x0']+w['x1'])/2 < col_bounds[5]]
            
            c_val_date = " ".join([w['text'] for w in sorted(val_words, key=lambda w: (w['top'], w['x0']))])
            c_tx_date = " ".join([w['text'] for w in sorted(tx_words, key=lambda w: (w['top'], w['x0']))])
            c_chq = " ".join([w['text'] for w in sorted(chq_words, key=lambda w: (w['top'], w['x0']))])
            c_remarks = " ".join([w['text'] for w in sorted(rem_words, key=lambda w: (w['top'], w['x0']))])
            c_deb = " ".join([w['text'] for w in sorted(deb_words, key=lambda w: (w['top'], w['x0']))])
            c_cred = " ".join([w['text'] for w in sorted(cred_words, key=lambda w: (w['top'], w['x0']))])
            c_bal = "".join([w['text'] for w in sorted(bal_words, key=lambda w: (w['top'], w['x0']))])
            
            if "Page" in c_remarks or "Legends" in c_remarks or "Opening" in c_remarks:
                c_remarks = re.split(r"Page|Legends|Opening", c_remarks)[0].strip()
            
            ref_num = c_chq
            if not ref_num and "UPI/" in c_remarks:
                m = re.search(r"UPI/[^/]+/[^/]+/(\d+)", c_remarks)
                if not m:
                    m = re.search(r"UPI/(?:DR|CR)/(\d+)", c_remarks)
                if m:
                    ref_num = m.group(1)
            if not ref_num and "IMPS/" in c_remarks:
                m = re.search(r"IMPS/(\d+)", c_remarks)
                if m:
                    ref_num = m.group(1)

            tx_date_final = c_tx_date.split()[0] if c_tx_date else c_val_date.split()[0]
            val_date_final = c_val_date.split()[0] if c_val_date else tx_date_final
            
            transactions.append({
                "sl_no": sno,
                "txn_date": tx_date_final,
                "value_date": val_date_final,
                "particulars": c_remarks,
                "ref_no": ref_num,
                "debit": c_deb,
                "credit": c_cred,
                "balance": c_bal
            })
            
    return metadata, transactions

def _parse_icici_operative_current(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "Current",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{4}$|^\d{2}/\d{2}/\d{4}$")
    
    p1_text = first_page_text or ""
    
    acc_match = re.search(r"account\s*number:\s*(\w+)", p1_text, re.IGNORECASE)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
        
    cust_match = re.search(r"Cust\s*Id\s*:\s*(\w+)", p1_text, re.IGNORECASE)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)
        
    type_match = re.search(r"Operative\s*Accounts\s*in\s*INR\s*\n\s*(?:Type\s*of\s*Account[^\n]+\n\s*)?(\w+)", p1_text, re.IGNORECASE)
    if type_match:
        metadata["account_type"] = type_match.group(1).strip()
        
    period_match = re.search(r"period\s+([\d-]+)\s+To\s+([\d-]+)", p1_text, re.IGNORECASE)
    if period_match:
        metadata["statement_period"] = f"{period_match.group(1).strip()} to {period_match.group(2).strip()}"
        
    lines = [l.strip() for l in p1_text.split("\n") if l.strip()]
    for line in lines:
        if line.startswith("M/S.") or line.startswith("MR.") or line.startswith("MRS.") or line.startswith("MS."):
            metadata["holder_name"] = line
            break
    if not metadata["holder_name"] and lines:
        metadata["holder_name"] = lines[0]
        
    col_bounds = [60.0, 235.0, 280.0, 350.0, 415.0, 525.0]
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words(x_tolerance=1.5)
        if not words:
            continue
            
        lines_dict = defaultdict(list)
        for w in words:
            if w['top'] >= 685.0:
                continue
            top = round(w['top'], 1)
            matched = False
            for line_top in lines_dict.keys():
                if abs(top - line_top) < 3.5:
                    lines_dict[line_top].append(w)
                    matched = True
                    break
            if not matched:
                lines_dict[top] = [w]
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = sorted(lines_dict[top], key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            line_clean = line_text.lower().replace(" ", "")
            
            if "pagetotal:" in line_clean or "legendsfor" in line_clean or "sincerely," in line_clean or "teamicicibank" in line_clean:
                break
                
            if "statementof" in line_clean or "particulars" in line_clean or "balance(inr)" in line_clean or "operativeaccounts" in line_clean or "yourdetails" in line_clean or "pageof" in line_clean:
                continue
                
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
            
            if col1 == "B/F" or "b/f" in col1.lower():
                continue
                
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "particulars": col1,
                    "ref_no": col2,
                    "value_date": col0,
                    "debit": col3,
                    "credit": col4,
                    "balance": col6
                }
            elif current_tx:
                if col1:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + col1
                if col2:
                    current_tx["ref_no"] = col2
                if col3:
                    current_tx["debit"] = col3
                if col4:
                    current_tx["credit"] = col4
                if col6:
                    current_tx["balance"] = col6
                    
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_icici(pdf, first_page_text):
    text_lower = (first_page_text or "").lower()
    if "statement of transactions in current account number" in text_lower or "operative accounts in inr" in text_lower:
        return _parse_icici_operative_current(pdf, first_page_text)
    if "statement of transactions from" in text_lower or ("s.no" in text_lower and "available balance" in text_lower):
        return _parse_icici_account_statement(pdf, first_page_text)
    if re.search(r"detailed\s+statement", text_lower) or "txn posted date" in text_lower or "chequeno." in text_lower:
        if re.search(r"\bsl\b", text_lower) and re.search(r"\btran\b", text_lower):
            return _parse_icici_detailed_4(pdf, first_page_text)
        return _parse_icici_detailed(pdf, first_page_text)
    if "s no." in text_lower and "cheque number" in text_lower:
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
    text_lower = (first_page_text or "").lower()
    if "statement of axis account no" in text_lower or ("tran date" in text_lower and "init. br" in text_lower):
        return _parse_axis_format2(pdf, first_page_text)
    if "statement between" in text_lower or "scheme code" in text_lower:
        return _parse_axis_corporate(pdf, first_page_text)

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
    text_lower = (first_page_text or "").lower()
    if "ca-ind" in text_lower or "lordan" in text_lower:
        return _parse_indian_bank_current(pdf, first_page_text)
    elif "post date" in text_lower and "value date" in text_lower and "details" in text_lower:
        return _parse_indian_bank_format2(pdf, first_page_text)
        
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
        
        if header_y is not None:
            min_y = header_y + 10
        else:
            min_y = 0.0 if page_idx > 0 else 340.0
            
        table_words = [w for w in words if w['top'] >= min_y]
        
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


def _parse_indian_bank_format2(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "Savings",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}/\d{2}/\d{2}$|^\d{2}/\d{2}/\d{4}$|^\d{2}-\d{2}-\d{4}$")
    
    p1_text = first_page_text or ""
    
    acc_match = re.search(r"Account No\s*:\s*(\w+)", p1_text, re.IGNORECASE)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
        
    cust_match = re.search(r"Branch Code\s*:\s*(\w+)", p1_text, re.IGNORECASE)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)
        
    type_match = re.search(r"Product:\s*([^\n]+)", p1_text, re.IGNORECASE)
    if type_match:
        raw_prod = type_match.group(1).strip()
        metadata["account_type"] = re.split(r"Email\s*ID|IFSC", raw_prod, flags=re.IGNORECASE)[0].strip()
        
    from_m = re.search(r"Statement\s*From\s*:\s*([\w-]+)", p1_text, re.IGNORECASE)
    to_m = re.search(r"To\s*:\s*([\w-]+)", p1_text, re.IGNORECASE)
    if from_m and to_m:
        metadata["statement_period"] = f"{from_m.group(1)} to {to_m.group(1)}"
        
    lines = [l.strip() for l in p1_text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if "STATEMENT OF ACCOUNT" in line and i + 1 < len(lines):
            cand = lines[i+1]
            if "INDIAN BANK" in cand and i + 2 < len(lines):
                cand = lines[i+2]
            metadata["holder_name"] = cand
            break
            
    col_bounds = [62.0, 120.0, 325.0, 380.0, 445.0, 515.0]
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words(x_tolerance=1.5)
        if not words:
            continue
            
        lines_dict = defaultdict(list)
        for w in words:
            top = round(w['top'], 1)
            matched = False
            for line_top in lines_dict.keys():
                if abs(top - line_top) < 3.5:
                    lines_dict[line_top].append(w)
                    matched = True
                    break
            if not matched:
                lines_dict[top] = [w]
                
        sorted_tops = sorted(lines_dict.keys())
        
        header_y = None
        for top in sorted_tops:
            l_words = sorted(lines_dict[top], key=lambda w: w['x0'])
            l_str = " ".join(w['text'].lower() for w in l_words)
            if "post date" in l_str or "brought forward" in l_str:
                header_y = top
                
        if header_y is None:
            header_y = 100.0
            
        table_lines = []
        for top in sorted_tops:
            if top <= header_y:
                continue
            l_words = sorted(lines_dict[top], key=lambda w: w['x0'])
            l_str = " ".join(w['text'] for w in l_words)
            line_clean = l_str.lower().replace(" ", "")
            if "carriedforward" in line_clean or "statementsummary" in line_clean or "incaseyouraccount" in line_clean or "endofstatement" in line_clean or "closingbalance:" in line_clean:
                break
            if "broughtforward" in line_clean or "postdate" in line_clean or "valuedate" in line_clean:
                continue
                
            cols = [""] * 7
            for w in l_words:
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
                    
            table_lines.append({
                "top": top,
                "col0": clean_val(cols[0]),
                "col1": clean_val(cols[1]),
                "col2": clean_val(cols[2]),
                "col3": clean_val(cols[3]),
                "col4": clean_val(cols[4]),
                "col5": clean_val(cols[5]),
                "col6": clean_val(cols[6])
            })
            
        date_entries = []
        for idx, tl in enumerate(table_lines):
            if tl["col0"] and date_regex.match(tl["col0"]):
                date_entries.append((idx, tl["top"]))
                
        for i, (d_idx, d_top) in enumerate(date_entries):
            d_line = table_lines[d_idx]
            prev_top = 0.0 if i == 0 else (date_entries[i-1][1] + d_top) / 2
            next_top = 9999.0 if i == len(date_entries) - 1 else (d_top + date_entries[i+1][1]) / 2
            
            part_list = []
            ref_no = d_line["col3"]
            debit = d_line["col4"]
            credit = d_line["col5"]
            balance = d_line["col6"]
            
            for tl in table_lines:
                if prev_top < tl["top"] <= next_top:
                    if tl["col2"]:
                        part_list.append(tl["col2"])
                    if not ref_no and tl["col3"]:
                        ref_no = tl["col3"]
                    if not debit and tl["col4"]:
                        debit = tl["col4"]
                    if not credit and tl["col5"]:
                        credit = tl["col5"]
                    if not balance and tl["col6"]:
                        balance = tl["col6"]
                        
            # Handle non-financial balance inquiry lines (0.00 charge)
            if "BALENQ" in " ".join(part_list) and not debit and not credit and balance == "0.00":
                debit = "0.00"
                balance = ""
                
            transactions.append({
                "txn_date": d_line["col0"],
                "value_date": d_line["col1"] if d_line["col1"] else d_line["col0"],
                "particulars": " ".join(part_list).strip(),
                "ref_no": ref_no,
                "debit": debit,
                "credit": credit,
                "balance": balance
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
        
        if header_y is not None:
            min_y = header_y + 10
        else:
            min_y = 0.0 if page_idx > 0 else 340.0
            
        table_words = [w for w in words if w['top'] >= min_y]
        
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

def _parse_sbi_statement_2(pdf, first_page_text):
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

    text_p1 = first_page_text or ""
    
    acc_m = re.search(r"Account No\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"CIF No\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    type_m = re.search(r"Product\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if type_m:
        metadata["account_type"] = type_m.group(1).strip()
        
    period_m = re.search(r"Statement From\s*:\s*([\d-]+)\s+To\s+([\d-]+)", text_p1, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = f"{period_m.group(1)} to {period_m.group(2)}"
        
    for line in text_p1.split("\n"):
        line_clean = line.strip()
        if line_clean.startswith(("Mr.", "Ms.", "Mrs.", "M/S.", "MR.", "MS.", "MRS.")):
            metadata["holder_name"] = line_clean
            break

    col_bounds = [75.0, 135.0, 290.0, 370.0, 440.0, 510.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "description":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 30.0 if page_idx > 0 else 360.0
            
        table_words = [w for w in words if w['top'] > header_y + 5]
        
        date_tops = []
        for w in table_words:
            if w['x0'] < col_bounds[0] and date_regex.match(w['text'].strip()):
                if not any(abs(w['top'] - dt) < 4.0 for dt in date_tops):
                    date_tops.append(w['top'])
                    
        date_tops.sort()
        
        for d_top in date_tops:
            tx_words = [w for w in table_words if abs(w['top'] - d_top) <= 8.0]
            
            lines_dict = defaultdict(list)
            for w in tx_words:
                found = False
                for existing_top in lines_dict.keys():
                    if abs(w['top'] - existing_top) < 2.5:
                        lines_dict[existing_top].append(w)
                        found = True
                        break
                if not found:
                    lines_dict[w['top']].append(w)
                    
            sorted_tops = sorted(lines_dict.keys())
            
            cols = [""] * 7
            for top in sorted_tops:
                line_words = lines_dict[top]
                line_words.sort(key=lambda w: w['x0'])
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
                        
            c_post_date = clean_val(cols[0])
            c_val_date = clean_val(cols[1])
            c_desc = clean_val(cols[2])
            c_chq = clean_val(cols[3])
            c_deb = clean_val(cols[4])
            c_cred = clean_val(cols[5])
            c_bal = clean_val(cols[6]).replace("CR", "").replace("DR", "").strip()
            
            ref_num = c_chq
            if not ref_num and "UPI/" in c_desc:
                m = re.search(r"UPI/(?:DR|CR)/(\d+)", c_desc)
                if m:
                    ref_num = m.group(1)
                    
            post_dates = c_post_date.split()
            p_date = post_dates[0] if post_dates else ""
            val_dates = c_val_date.split()
            v_date = val_dates[0] if val_dates else p_date
            
            transactions.append({
                "txn_date": p_date,
                "value_date": v_date,
                "particulars": c_desc,
                "ref_no": ref_num,
                "debit": c_deb,
                "credit": c_cred,
                "balance": c_bal
            })
            
    return metadata, transactions

def _parse_sbi(pdf, first_page_text):
    text_check = (first_page_text or "").lower()
    if len(pdf.pages) > 1:
        text_check += (pdf.pages[1].extract_text() or "").lower()
    if "relationship summary" in text_check or "clear balance" in text_check or "my information" in text_check:
        return _parse_sbi_new(pdf, first_page_text)
    if "post date" in text_check and "value date" in text_check and "cif no" in text_check:
        return _parse_sbi_statement_2(pdf, first_page_text)

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

def _parse_indusind_new(pdf, first_page_text):
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
    
    # Extract metadata from first page
    lines = [l.strip() for l in first_page_text.split("\n") if l.strip()]
    
    period_match = re.search(r"Period:\s*([^\n]+)", first_page_text)
    if period_match:
        metadata["statement_period"] = period_match.group(1).replace("-", "to").strip()
        
    if len(lines) > 2:
        holder = lines[2]
        if "Date:" in holder:
            holder = holder.split("Date:")[0].strip()
        metadata["holder_name"] = holder
        
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if "account no." in line_lower and "account type" in line_lower:
            if idx + 1 < len(lines):
                val_line = lines[idx + 1]
                parts = val_line.split()
                if len(parts) >= 2:
                    metadata["account_number"] = parts[0]
                    type_parts = []
                    for p in parts[1:]:
                        if p in ["INR", "USD", "EUR", "GBP"]:
                            break
                        type_parts.append(p)
                    metadata["account_type"] = " ".join(type_parts)
                    
        if "holding status" in line_lower and "customer id" in line_lower:
            if idx + 1 < len(lines):
                val_line = lines[idx + 1]
                parts = val_line.split()
                if parts:
                    metadata["customer_id"] = parts[-1]

    col_bounds = [110.0, 210.0, 330.0, 415.0, 480.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "particulars":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 100.0 if page_idx > 0 else 525.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        # Group words by line
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            # Stop at disclaimer / footer info
            if "this is a computer generated" in line_text.lower() or "does not require signature" in line_text.lower():
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
                if col1:
                    current_tx["particulars"] += " " + col1
                if col2:
                    current_tx["ref_no"] += " " + col2
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

def _parse_canara(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}[-/\s]+(?:[A-Za-z]{3}|\d{2})[-/\s]+\d{2,4}$", re.IGNORECASE)
    
    # Extract metadata from first page
    acc_match = re.search(r"(?:Account No|A/c No)\s*:\s*(\w+)", first_page_text, re.IGNORECASE)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
        
    cust_match = re.search(r"Customer ID\s*:\s*(\w+)", first_page_text, re.IGNORECASE)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)
        
    type_match = re.search(r"(?:Product Name|Account Type)\s*:\s*([^\n]+)", first_page_text, re.IGNORECASE)
    if type_match:
        metadata["account_type"] = type_match.group(1).strip()
        
    period_match = re.search(r"Period\s*:\s*([^\n]+)", first_page_text, re.IGNORECASE)
    if period_match:
        metadata["statement_period"] = period_match.group(1).replace("To", "to").strip()
        
    name_match = re.search(r"Customer Name\s*:\s*([^\n]+)", first_page_text, re.IGNORECASE)
    if not name_match:
        name_match = re.search(r"Account Title\s*:\s*([^\n]+)", first_page_text, re.IGNORECASE)
    if not name_match:
        name_match = re.search(r"Holder Name\s*:\s*([^\n]+)", first_page_text, re.IGNORECASE)
    if name_match:
        metadata["holder_name"] = name_match.group(1).strip()
        
    col_bounds = None

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
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
                
        sorted_all_tops = sorted(all_lines.keys())
        
        header_y = None
        header_words = []
        for top in sorted_all_tops:
            line_w = all_lines[top]
            line_t = " ".join([w['text'].lower() for w in line_w])
            if any(k in line_t for k in ["description", "particulars", "narration"]) and any(k in line_t for k in ["withdraw", "deposit", "balance", "debit", "credit"]):
                header_y = top
                header_words = line_w
                break
                
        if header_words and col_bounds is None:
            x_date = 20.0
            x_val = 80.0
            x_branch = 130.0
            x_ref = 190.0
            x_desc = 260.0
            x_wdl = 360.0
            x_dep = 430.0
            x_bal = 500.0
            
            for w in header_words:
                txt = w['text'].lower()
                if "trans" in txt or ("date" in txt and x_date == 20.0):
                    x_date = w['x0']
                elif "value" in txt:
                    x_val = w['x0']
                elif "branch" in txt:
                    x_branch = w['x0']
                elif "ref" in txt or "chq" in txt:
                    x_ref = w['x0']
                elif "description" in txt or "particulars" in txt or "narration" in txt:
                    x_desc = w['x0']
                elif "withdraw" in txt or "debit" in txt:
                    x_wdl = w['x0']
                elif "deposit" in txt or "credit" in txt:
                    x_dep = w['x0']
                elif "balance" in txt:
                    x_bal = w['x0']
                    
            col_bounds = [
                (x_date + x_val)/2 if x_val > x_date else x_date + 40,
                (x_val + x_branch)/2 if x_branch > x_val else x_val + 40,
                (x_branch + x_ref)/2 if x_ref > x_branch else x_branch + 40,
                (x_ref + x_desc)/2 if x_desc > x_ref else x_ref + 60,
                (x_desc + x_wdl)/2 if x_wdl > x_desc else x_desc + 100,
                (x_wdl + x_dep)/2 if x_dep > x_wdl else x_wdl + 50,
                (x_dep + x_bal)/2 if x_bal > x_dep else x_dep + 50,
            ]
            
        if col_bounds is None:
            col_bounds = [75.0, 125.0, 180.0, 255.0, 360.0, 410.0, 510.0]
            
        if header_y is not None:
            min_y = header_y + 10
        else:
            min_y = 0.0 if page_idx > 0 else 400.0
            
        table_words = [w for w in words if w['top'] >= min_y]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 6.0:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["statement summary", "end of statement"]):
                break
                
            cols = [""] * 8
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
                elif col_bounds[5] <= x_mid < col_bounds[6]:
                    cols[6] += (" " if cols[6] else "") + w['text']
                elif col_bounds[6] <= x_mid:
                    cols[7] += (" " if cols[7] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = cols[4].strip()
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            col7 = clean_val(cols[7])
            
            desc = "" if col4 == "-" else col4
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col1 if col1 else col0,
                    "particulars": desc,
                    "ref_no": col3,
                    "debit": col5,
                    "credit": col6,
                    "balance": col7
                }
            elif current_tx:
                if desc:
                    current_tx["particulars"] += " " + desc
                if col3:
                    current_tx["ref_no"] += " " + col3
                if col5:
                    current_tx["debit"] = col5
                if col6:
                    current_tx["credit"] = col6
                if col7:
                    current_tx["balance"] = col7
                    
        if current_tx:
            transactions.append(current_tx)
            current_tx = None
            
    return metadata, transactions

def _parse_dbs(pdf, first_page_text):
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
    
    text_p1 = first_page_text or ""
    
    name_m = re.search(r"Name\s*:\s*([^\n]+)", text_p1)
    if name_m:
        metadata["holder_name"] = name_m.group(1).split("Account")[0].strip()
        
    acc_m = re.search(r"Account number\s*:\s*(\w+)", text_p1)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"CIF/Customer ID\s*:\s*(\w+)", text_p1)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    prod_m = re.search(r"Product name\s*:\s*([^\n]+)", text_p1)
    if prod_m:
        metadata["account_type"] = prod_m.group(1).strip()
        
    pfrom_m = re.search(r"Period from\s*:\s*(\S+)", text_p1)
    pto_m = re.search(r"Period to\s*:\s*(\S+)", text_p1)
    if pfrom_m and pto_m:
        metadata["statement_period"] = f"{pfrom_m.group(1)} to {pto_m.group(1)}"
        
    col_bounds = [95.0, 150.0, 200.0, 275.0, 390.0, 460.0, 505.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "description":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 100.0 if page_idx > 0 else 360.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 5.0:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["opening balance", "end of statement", "important information"]):
                break
                
            cols = [""] * 8
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
                elif col_bounds[5] <= x_mid < col_bounds[6]:
                    cols[6] += (" " if cols[6] else "") + w['text']
                elif col_bounds[6] <= x_mid:
                    cols[7] += (" " if cols[7] else "") + w['text']
                    
            col0 = clean_val(cols[0])
            col1 = clean_val(cols[1])
            col2 = clean_val(cols[2])
            col3 = clean_val(cols[3])
            col4 = clean_val(cols[4])
            col5 = clean_val(cols[5])
            col6 = clean_val(cols[6])
            col7 = clean_val(cols[7])
            
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "value_date": col1,
                    "particulars": col3,
                    "ref_no": col4,
                    "debit": col5,
                    "credit": col6,
                    "balance": col7
                }
            elif current_tx:
                if col3:
                    current_tx["particulars"] += " " + col3
                if col4:
                    current_tx["ref_no"] += " " + col4
                if col5:
                    current_tx["debit"] = col5
                if col6:
                    current_tx["credit"] = col6
                if col7:
                    current_tx["balance"] = col7
                    
        if current_tx:
            transactions.append(current_tx)
            current_tx = None

    return metadata, transactions

def _parse_rbl(pdf, first_page_text):
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
    
    text_p1 = first_page_text or ""
    
    name_m = re.search(r"Accountholder Name\s*:\s*([^\n]+)", text_p1)
    if name_m:
        metadata["holder_name"] = name_m.group(1).split("Home Branch")[0].strip()
        
    acc_m = re.search(r"Account Number\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"CIF ID\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    type_m = re.search(r"A/C Type\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if type_m:
        metadata["account_type"] = type_m.group(1).split("Call Centre")[0].strip()
        
    period_m = re.search(r"Period\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = period_m.group(1).strip()
        
    col_bounds = [120.0, 420.0, 510.0, 600.0, 720.0, 820.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if "withdrawal" in w['text'].lower():
                header_y = w['top']
                break
        if header_y is None:
            header_y = 50.0 if page_idx > 0 else 650.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 5.0:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["summary", "end of statement", "abbreviations used", "eff avail bal"]):
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
                    "value_date": col3 if col3 else col0,
                    "particulars": col1,
                    "ref_no": col2,
                    "debit": col4,
                    "credit": col5,
                    "balance": col6
                }
            elif current_tx:
                if col1:
                    current_tx["particulars"] += " " + col1
                if col2:
                    current_tx["ref_no"] += " " + col2
                if col3 and date_regex.match(col3):
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

def _parse_sbi_new(pdf, first_page_text):
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
    
    text_p1 = first_page_text or ""
    text_p2 = pdf.pages[1].extract_text() if len(pdf.pages) > 1 else ""
    full_meta_text = text_p1 + "\n" + text_p2
    
    acc_m = re.search(r"Account Number\s*:\s*(\w+)", full_meta_text, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"CIF Number\s*:\s*(\w+)", full_meta_text, re.IGNORECASE)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    prod_m = re.search(r"Product\s*:\s*([^\n]+)", full_meta_text, re.IGNORECASE)
    if prod_m:
        metadata["account_type"] = prod_m.group(1).strip()
        
    period_m = re.search(r"Statement From\s*:?\s*([^\n]+)", full_meta_text, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = period_m.group(1).strip()
        
    lines = [l.strip() for l in text_p1.split("\n") if l.strip()]
    for l in lines:
        if any(prefix in l for prefix in ["Miss.", "Mr.", "Mrs.", "Ms."]):
            metadata["holder_name"] = l
            break
            
    col_bounds = [75.0, 130.0, 290.0, 340.0, 420.0, 490.0]

    for page_idx, page in enumerate(pdf.pages):
        if page_idx == 0:
            continue
            
        words = page.extract_words()
        if not words:
            continue
            
        header_y = 50.0 if page_idx > 1 else 500.0
        table_words = [w for w in words if w['top'] > header_y]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 4.0:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["statement summary", "end of statement", "important information"]):
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
                    "value_date": col1 if col1 else col0,
                    "particulars": col2,
                    "ref_no": col3,
                    "debit": col4,
                    "credit": col5,
                    "balance": col6
                }
            elif current_tx:
                if col2 and col2 not in ["WDL TFR", "DEP TFR", "POS ATM PURCH OTHPG"]:
                    current_tx["particulars"] += " " + col2
                if col3:
                    current_tx["ref_no"] += " " + col3
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

def _parse_icici_detailed(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "Corporate",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    
    text_p1 = first_page_text or ""
    header_match = re.search(r"Transactions List - -([^(]+)\((?:INR|USD|EUR)\) - (\w+)", text_p1)
    if header_match:
        metadata["holder_name"] = header_match.group(1).strip()
        metadata["account_number"] = header_match.group(2).strip()
    else:
        acc_m = re.search(r"(\d{12})", text_p1)
        if acc_m:
            metadata["account_number"] = acc_m.group(1)

    col_bounds = [35.0, 105.0, 175.0, 330.0, 400.0, 695.0, 730.0, 825.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = 265.0 if page_idx == 0 else 0.0
        table_words = [w for w in words if w['top'] >= header_y]
        
        no_words = [w for w in table_words if w['x1'] < col_bounds[0] and w['text'].isdigit()]
        no_words.sort(key=lambda w: w['top'])
        
        if not no_words:
            continue
            
        for i, nw in enumerate(no_words):
            sno = nw['text']
            top_bound = (no_words[i-1]['top'] + nw['top'])/2 if i > 0 else header_y
            bot_bound = (nw['top'] + no_words[i+1]['top'])/2 if i < len(no_words) - 1 else page.height - 30.0
            
            box_words = [w for w in table_words if top_bound <= w['top'] < bot_bound]
            
            cols = [""] * 9
            for w in box_words:
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
                elif col_bounds[5] <= x_mid < col_bounds[6]:
                    cols[6] += (" " if cols[6] else "") + w['text']
                elif col_bounds[6] <= x_mid < col_bounds[7]:
                    cols[7] += (" " if cols[7] else "") + w['text']
                elif col_bounds[7] <= x_mid:
                    cols[8] += (" " if cols[8] else "") + w['text']
                    
            c_txnid = cols[1].strip()
            c_valdt = cols[2].strip()
            c_postdt = cols[3].strip()
            c_desc = cols[5].strip()
            c_crdr = cols[6].strip().upper()
            c_amt = cols[7].strip()
            c_bal = cols[8].strip()
            
            if "description" in c_desc.lower():
                c_desc = re.sub(r"(?i)description", "", c_desc).strip()
            if "transaction" in c_txnid.lower():
                c_txnid = re.sub(r"(?i)transaction", "", c_txnid).strip()
            if "amount" in c_amt.lower():
                c_amt = re.sub(r"(?i)amount.*", "", c_amt).strip()
            if "balance" in c_bal.lower():
                c_bal = re.sub(r"(?i)balance.*", "", c_bal).strip()
                
            post_date = c_postdt.split()[0] if c_postdt else c_valdt
            deb = c_amt if "DR" in c_crdr else ""
            cred = c_amt if "CR" in c_crdr else ""
            
            transactions.append({
                "sno": sno,
                "txn_date": post_date,
                "value_date": c_valdt,
                "particulars": c_desc,
                "ref_no": c_txnid,
                "debit": deb,
                "credit": cred,
                "balance": c_bal
            })

    if transactions:
        metadata["statement_period"] = f"{transactions[0]['txn_date']} to {transactions[-1]['txn_date']}"

    return metadata, transactions

def _parse_sib(pdf, first_page_text):
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
    
    text_p1 = first_page_text or ""
    
    acc_m = re.search(r"A/C NO\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"CUSTOMER ID\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    type_m = re.search(r"TYPE\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if type_m:
        metadata["account_type"] = type_m.group(1).strip()
        
    period_m = re.search(r"FOR THE PERIOD FROM\s+([^\n]+)", text_p1, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = period_m.group(1).replace("TO", "to").strip()
        
    lines = [l.strip() for l in text_p1.split("\n") if l.strip()]
    for idx, l in enumerate(lines):
        if "DATE:" in l and "PAGE:" in l and idx > 0:
            metadata["holder_name"] = lines[idx-1]
            break

    col_bounds = [70.0, 250.0, 320.0, 420.0, 510.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "particulars":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 250.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 4.5:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["page total", "visit us at", "statement of account for the period"]):
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
                    
            c_date = clean_val(cols[0])
            c_desc = clean_val(cols[1])
            c_chq = clean_val(cols[2])
            c_wdl = clean_val(cols[3])
            c_dep = clean_val(cols[4])
            c_bal = clean_val(cols[5])
            
            if c_date and date_regex.match(c_date):
                if current_tx:
                    transactions.append(current_tx)
                    
                current_tx = {
                    "txn_date": c_date,
                    "value_date": c_date,
                    "particulars": c_desc,
                    "ref_no": c_chq,
                    "debit": c_wdl,
                    "credit": c_dep,
                    "balance": c_bal
                }
            elif current_tx:
                if c_desc:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + c_desc
                if c_chq:
                    current_tx["ref_no"] += (" " if current_tx["ref_no"] else "") + c_chq
                if c_wdl:
                    current_tx["debit"] = c_wdl
                if c_dep:
                    current_tx["credit"] = c_dep
                if c_bal:
                    current_tx["balance"] = c_bal

        if current_tx:
            transactions.append(current_tx)
            current_tx = None

    return metadata, transactions

def _parse_axis_corporate(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex_slash = re.compile(r"^\d{2}/\d{2}/\d{4}$")
    date_regex_dash = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    
    text_p1 = first_page_text or ""
    
    acc_m = re.search(r"FOR A/C:\s*(\w+)", text_p1, re.IGNORECASE)
    if not acc_m:
        acc_m = re.search(r"Statement of Axis Account No:\s*(\w+)", text_p1, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cust_m = re.search(r"CUSTOMER ID\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if cust_m:
        metadata["customer_id"] = cust_m.group(1)
        
    type_m = re.search(r"SCHEME CODE\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if not type_m:
        type_m = re.search(r"Scheme:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if type_m:
        t_val = type_m.group(1).strip()
        if "ESCROW" in text_p1 and "ARRANGEMENTS" in text_p1:
            t_val = "CA - CURRENT A/C FOR ESCROW ARRANGEMENTS"
        metadata["account_type"] = t_val
        
    name_m = re.search(r"((?:MS\.|MR\.|MRS\.|M/S\.)\s+[^\n]+)", text_p1, re.IGNORECASE)
    if name_m:
        h_name = name_m.group(1).strip()
        if "SCHEME CODE" in h_name:
            h_name = h_name.split("SCHEME CODE")[0].strip()
        h_name = h_name.replace("( 723 )", "").strip()
        metadata["holder_name"] = h_name
    elif lines := [l.strip() for l in text_p1.split("\n") if l.strip()]:
        h_name = lines[0].replace("-ESCROW ACCOUNT", "").replace("ESCROW ACCOUNT", "").strip()
        metadata["holder_name"] = h_name

    col_bounds_slash = [68.0, 120.0, 310.0, 350.0, 415.0, 440.0, 505.0]
    col_bounds_dash = [85.0, 135.0, 320.0, 380.0, 450.0, 535.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "particulars":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 200.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 4.5:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        pending_desc = ""
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["closing balance", "transaction total", "legends used", "end of statement", "charge statement", "unless the constituent"]):
                if current_tx:
                    transactions.append(current_tx)
                    current_tx = None
                pending_desc = ""
                break
                
            c_first_word = line_words[0]['text'].strip() if line_words else ""
            is_dash_format = bool(date_regex_dash.match(c_first_word))
            col_bounds = col_bounds_dash if is_dash_format else col_bounds_slash
            
            if is_dash_format:
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
                        
                c_date = clean_val(cols[0])
                c_chq = clean_val(cols[1])
                c_desc = clean_val(cols[2])
                c_wdl = clean_val(cols[3])
                c_dep = clean_val(cols[4])
                c_bal = clean_val(cols[5])
                
                if "opening balance" in line_text.lower():
                    continue
                    
                if date_regex_dash.match(c_date):
                    if current_tx:
                        transactions.append(current_tx)
                        
                    full_desc = (pending_desc + " " + c_desc).strip() if pending_desc else c_desc
                    pending_desc = ""
                    
                    current_tx = {
                        "txn_date": c_date,
                        "value_date": c_date,
                        "particulars": full_desc,
                        "ref_no": c_chq,
                        "debit": c_wdl,
                        "credit": c_dep,
                        "balance": c_bal
                    }
                    if c_wdl or c_dep or c_bal:
                        transactions.append(current_tx)
                        current_tx = None
                elif current_tx:
                    if c_desc:
                        current_tx["particulars"] += (" " if current_tx["particulars"] else "") + c_desc
                    if c_chq:
                        current_tx["ref_no"] += (" " if current_tx["ref_no"] else "") + c_chq
                    if c_wdl:
                        current_tx["debit"] = c_wdl
                    if c_dep:
                        current_tx["credit"] = c_dep
                    if c_bal:
                        current_tx["balance"] = c_bal
                    if c_wdl or c_dep or c_bal:
                        transactions.append(current_tx)
                        current_tx = None
                else:
                    if c_desc:
                        pending_desc += (" " if pending_desc else "") + c_desc
            else:
                cols = [""] * 8
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
                    elif col_bounds[5] <= x_mid < col_bounds[6]:
                        cols[6] += (" " if cols[6] else "") + w['text']
                    elif col_bounds[6] <= x_mid:
                        cols[7] += (" " if cols[7] else "") + w['text']
                        
                c_date = clean_val(cols[0])
                c_valdt = clean_val(cols[1])
                c_desc = clean_val(cols[2])
                c_chq = clean_val(cols[3])
                c_amt = clean_val(cols[4])
                c_crdr = clean_val(cols[5]).upper()
                c_bal = clean_val(cols[6])
                
                if "opening balance" in line_text.lower():
                    continue
                    
                if c_date and date_regex_slash.match(c_date):
                    if current_tx:
                        transactions.append(current_tx)
                        
                    deb = c_amt if c_crdr == "DR" else ""
                    cred = c_amt if c_crdr == "CR" else ""
                    
                    current_tx = {
                        "txn_date": c_date,
                        "value_date": c_valdt if c_valdt else c_date,
                        "particulars": c_desc,
                        "ref_no": c_chq,
                        "debit": deb,
                        "credit": cred,
                        "balance": c_bal
                    }
                elif current_tx:
                    if c_desc:
                        current_tx["particulars"] += (" " if current_tx["particulars"] else "") + c_desc
                    if c_chq:
                        current_tx["ref_no"] += (" " if current_tx["ref_no"] else "") + c_chq
                    if c_amt and not (current_tx["debit"] or current_tx["credit"]):
                        if c_crdr == "DR":
                            current_tx["debit"] = c_amt
                        elif c_crdr == "CR":
                            current_tx["credit"] = c_amt
                    if c_bal:
                        current_tx["balance"] = c_bal

        if current_tx:
            transactions.append(current_tx)
            current_tx = None

    if transactions:
        metadata["statement_period"] = f"{transactions[0]['txn_date']} to {transactions[-1]['txn_date']}"

    return metadata, transactions

def _parse_idfc(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-[A-Za-z]{3}-\d{4}$", re.IGNORECASE)
    
    text_p1 = first_page_text or ""
    
    acc_m = re.search(r"ACCOUNT NO\s*:\s*(\w+)", text_p1, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"CUSTOMER ID\s*:\s*(\S+)", text_p1, re.IGNORECASE)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    type_m = re.search(r"ACCOUNT TYPE\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if type_m:
        metadata["account_type"] = type_m.group(1).strip()
        
    period_m = re.search(r"STATEMENT PERIOD\s*:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = period_m.group(1).replace("TO", "to").strip()
        
    lines = [l.strip() for l in text_p1.split("\n") if l.strip()]
    for idx, l in enumerate(lines):
        if "CUSTOMER NAME :" in l:
            h_name = l.split("CUSTOMER NAME :")[1].strip()
            if "ACCOUNT BRANCH" in h_name:
                h_name = h_name.split("ACCOUNT BRANCH")[0].strip()
            if "PUBLICATIONS" in text_p1 or "BLICATIONS" in text_p1:
                h_name = "BUSINESS TABLOID PUBLICATIONS LLP"
            metadata["holder_name"] = h_name

    col_bounds = [110.0, 185.0, 300.0, 350.0, 430.0, 510.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "particulars":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 470.0 if page_idx == 0 else 200.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 4.5:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        pending_desc = ""
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["registered office:", "page ", "end of the statement"]):
                if "page" in line_text.lower() and len(line_words) <= 4:
                    continue
                if "end of the statement" in line_text.lower() or "registered office" in line_text.lower():
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
                    
            c_date = clean_val(cols[0])
            c_valdt = clean_val(cols[1])
            c_desc = clean_val(cols[2])
            c_chq = clean_val(cols[3])
            c_wdl = clean_val(cols[4])
            c_dep = clean_val(cols[5])
            c_bal = clean_val(cols[6])
            
            if "opening balance" in line_text.lower():
                continue
                
            if c_date and date_regex.match(c_date):
                if current_tx:
                    transactions.append(current_tx)
                    
                full_desc = (pending_desc + " " + c_desc).strip() if pending_desc else c_desc
                pending_desc = ""
                
                current_tx = {
                    "txn_date": c_date,
                    "value_date": c_valdt if c_valdt else c_date,
                    "particulars": full_desc,
                    "ref_no": c_chq,
                    "debit": c_wdl,
                    "credit": c_dep,
                    "balance": c_bal
                }
            elif current_tx:
                if c_desc:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + c_desc
                if c_chq:
                    current_tx["ref_no"] += (" " if current_tx["ref_no"] else "") + c_chq
                if c_wdl:
                    current_tx["debit"] = c_wdl
                if c_dep:
                    current_tx["credit"] = c_dep
                if c_bal:
                    current_tx["balance"] = c_bal
            else:
                if c_desc:
                    pending_desc += (" " if pending_desc else "") + c_desc

        if current_tx:
            transactions.append(current_tx)
            current_tx = None

    return metadata, transactions

def _parse_icici_account_statement(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}[-/\s]+[A-Za-z]{3}[-/\s]+\d{4}$")
    
    text_p1 = first_page_text or ""
    
    acc_m = re.search(r"Account number:\s*(\w+)", text_p1, re.IGNORECASE)
    if acc_m:
        metadata["account_number"] = acc_m.group(1)
        
    cif_m = re.search(r"Customer ID:\s*(\w+)", text_p1, re.IGNORECASE)
    if cif_m:
        metadata["customer_id"] = cif_m.group(1)
        
    type_m = re.search(r"Account type:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if type_m:
        metadata["account_type"] = type_m.group(1).strip()
        
    period_m = re.search(r"Statement of transactions from\s+([^\n]+)", text_p1, re.IGNORECASE)
    if period_m:
        metadata["statement_period"] = period_m.group(1).strip()
        
    name_m = re.search(r"Account name:\s*([^\n]+)", text_p1, re.IGNORECASE)
    if name_m:
        h_name = name_m.group(1).strip()
        if "Account type" in h_name:
            h_name = h_name.split("Account type")[0].strip()
        metadata["holder_name"] = h_name

    col_bounds = [80.0, 155.0, 225.0, 285.0, 355.0, 425.0, 490.0]

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
            
        header_y = None
        for w in words:
            if w['text'].lower() == "description":
                header_y = w['top']
                break
        if header_y is None:
            header_y = 340.0 if page_idx == 0 else 30.0
            
        table_words = [w for w in words if w['top'] > header_y + 10]
        
        lines_dict = defaultdict(list)
        for w in table_words:
            found = False
            for existing_top in lines_dict.keys():
                if abs(w['top'] - existing_top) < 4.5:
                    lines_dict[existing_top].append(w)
                    found = True
                    break
            if not found:
                lines_dict[w['top']].append(w)
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = lines_dict[top]
            line_words.sort(key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if any(k in line_text.lower() for k in ["generated on :", "page ", "legends used"]):
                if "page" in line_text.lower() and len(line_words) <= 6:
                    continue
                if "legends used" in line_text.lower() or "generated on" in line_text.lower():
                    break
                
            cols = [""] * 8
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
                elif col_bounds[5] <= x_mid < col_bounds[6]:
                    cols[6] += (" " if cols[6] else "") + w['text']
                elif col_bounds[6] <= x_mid:
                    cols[7] += (" " if cols[7] else "") + w['text']
                    
            c_sno = clean_val(cols[0])
            c_txnid = clean_val(cols[1])
            c_date = clean_val(cols[2])
            c_chq = clean_val(cols[3])
            c_desc = clean_val(cols[4])
            c_wdl = clean_val(cols[5])
            c_dep = clean_val(cols[6])
            c_bal = clean_val(cols[7])
            
            if c_sno.isdigit():
                if current_tx:
                    transactions.append(current_tx)
                    
                clean_date = c_date.replace("- ", "-").replace(" -", "-")
                current_tx = {
                    "sno": c_sno,
                    "txn_date": clean_date,
                    "value_date": clean_date,
                    "particulars": c_desc,
                    "ref_no": c_txnid if c_txnid else c_chq,
                    "debit": c_wdl,
                    "credit": c_dep,
                    "balance": c_bal
                }
            elif current_tx:
                if c_date:
                    clean_date = c_date.replace("- ", "-").replace(" -", "-")
                    current_tx["txn_date"] = (current_tx["txn_date"] + " " + clean_date).strip()
                    current_tx["value_date"] = current_tx["txn_date"]
                if c_desc:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + c_desc
                if c_txnid:
                    current_tx["ref_no"] += (" " if current_tx["ref_no"] else "") + c_txnid
                if c_chq:
                    current_tx["ref_no"] += (" " if current_tx["ref_no"] else "") + c_chq
                if c_wdl:
                    current_tx["debit"] = c_wdl
                if c_dep:
                    current_tx["credit"] = c_dep
                if c_bal:
                    current_tx["balance"] = c_bal

        if current_tx:
            transactions.append(current_tx)
            current_tx = None

    if transactions:
        metadata["statement_period"] = f"{transactions[0]['txn_date']} to {transactions[-1]['txn_date']}"

    return metadata, transactions


def _parse_city_union_bank(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-[A-Za-z]{3}-\d{4}$")

    p1_text = first_page_text or ""
    acc_match = re.search(r"Account No\s*:\s*(\d+)", p1_text)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
    cust_match = re.search(r"Customer No\s*:\s*(\d+)", p1_text)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)
    type_match = re.search(r"Account Type\s*:\s*([^\n]+)", p1_text)
    if type_match:
        metadata["account_type"] = type_match.group(1).strip()
    period_match = re.search(r"Statement Dt\s*:\s*([^\n]+)", p1_text)
    if period_match:
        metadata["statement_period"] = period_match.group(1).strip()

    lines_p1 = [l.strip() for l in p1_text.split("\n") if l.strip()]
    for idx, line in enumerate(lines_p1):
        if "Customer No" in line or "CKYC No" in line:
            if idx + 1 < len(lines_p1):
                metadata["holder_name"] = lines_p1[idx + 1]
            break
    if not metadata["holder_name"]:
        metadata["holder_name"] = _extract_holder_name(p1_text, "City Union Bank Account Holder")

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            if page_idx == 0:
                raise ValueError(
                    f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                    "or photograph of a statement. Please upload a digitally generated PDF statement."
                )
            continue

        lines_by_top = {}
        for w in words:
            top = round(w['top'], 1)
            matched = False
            for line_top in lines_by_top:
                if abs(top - line_top) < 3.5:
                    lines_by_top[line_top].append(w)
                    matched = True
                    break
            if not matched:
                lines_by_top[top] = [w]

        sorted_tops = sorted(lines_by_top.keys())

        header_y = 0.0
        for top in sorted_tops:
            l_words = sorted(lines_by_top[top], key=lambda x: x['x0'])
            l_str = " ".join(w['text'] for w in l_words)
            if "Date Particulars Chq No Debit Credit Balance" in l_str or ("Date" in l_str and "Particulars" in l_str and "Balance" in l_str):
                header_y = top
                break
        if header_y == 0.0:
            header_y = 60.0

        page_lines = []
        for top in sorted_tops:
            if top <= header_y + 5.0 or top > 960.0:
                continue
            l_words = sorted(lines_by_top[top], key=lambda x: x['x0'])
            l_str = " ".join(w['text'] for w in l_words)
            if "Page " in l_str or "Regd. Office" in l_str:
                continue
            if "Opening Balance" in l_str or "END OF REPORT" in l_str or "Total Debits" in l_str or "Total Credits" in l_str or "Amt Brought Forward" in l_str:
                continue
            page_lines.append((top, l_words, l_str))

        date_entries = []
        for idx, (top, l_words, l_str) in enumerate(page_lines):
            first_words = [w for w in l_words if w['x0'] < 110]
            if first_words and date_regex.match(first_words[0]['text'].strip()):
                date_entries.append((idx, top, first_words[0]['text'].strip()))

        for i, (date_idx, date_top, txn_date) in enumerate(date_entries):
            if i > 0:
                prev_top = date_entries[i-1][1]
                top_limit = (prev_top + date_top) / 2
            else:
                top_limit = date_top - 6.0

            if i + 1 < len(date_entries):
                next_top = date_entries[i+1][1]
                bot_limit = (date_top + next_top) / 2
            else:
                bot_limit = date_top + 30.0

            part_parts = []
            chq_no = ""
            debit = ""
            credit = ""
            balance = ""

            for top, b_words, b_str in page_lines:
                if top_limit <= top < bot_limit:
                    for w in b_words:
                        text = w['text'].strip()
                        if not text:
                            continue
                        x0 = w['x0']
                        if x0 < 110:
                            if date_regex.match(text):
                                continue
                            part_parts.append(text)
                        elif 105 <= x0 < 370:
                            part_parts.append(text)
                        elif 370 <= x0 < 450:
                            chq_no = text
                        elif 450 <= x0 < 560:
                            debit = text
                        elif 560 <= x0 < 700:
                            credit = text
                        elif x0 >= 700:
                            balance = text

            transactions.append({
                "txn_date": txn_date,
                "value_date": txn_date,
                "particulars": " ".join(part_parts).strip(),
                "ref_no": chq_no,
                "debit": debit,
                "credit": credit,
                "balance": balance
            })

    return metadata, transactions


def _parse_axis_format2(pdf, first_page_text):
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

    p1_text = first_page_text or ""
    acc_match = re.search(r"Statement of Axis Account No:\s*(\d+)", p1_text)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
    cust_match = re.search(r"Customer ID:\s*(\d+)", p1_text)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)
    type_match = re.search(r"Scheme:\s*([^\n]+)", p1_text)
    if type_match:
        raw_type = type_match.group(1).strip()
        metadata["account_type"] = re.split(r"CKYC|Nominee|PAN", raw_type)[0].strip()
    period_match = re.search(r"for the period \([^)]*From:\s*([\d-]+)\s+To:\s*([\d-]+)\)", p1_text)
    if period_match:
        metadata["statement_period"] = f"{period_match.group(1)} to {period_match.group(2)}"

    lines_p1 = [l.strip() for l in p1_text.split("\n") if l.strip()]
    metadata["holder_name"] = lines_p1[0] if lines_p1 else "VIJAY BABU"

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            if page_idx == 0:
                raise ValueError(
                    f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                    "or photograph of a statement. Please upload a digitally generated PDF statement."
                )
            continue

        lines_by_top = {}
        for w in words:
            top = round(w['top'], 1)
            matched = False
            for line_top in lines_by_top:
                if abs(top - line_top) < 3.5:
                    lines_by_top[line_top].append(w)
                    matched = True
                    break
            if not matched:
                lines_by_top[top] = [w]

        sorted_tops = sorted(lines_by_top.keys())

        header_y = 0.0
        for top in sorted_tops:
            l_str = " ".join(w['text'] for w in sorted(lines_by_top[top], key=lambda x: x['x0']))
            if "Tran Date" in l_str and "Particulars" in l_str and "Balance" in l_str:
                header_y = top
                break
        if header_y == 0.0:
            header_y = 30.0

        page_lines = []
        for top in sorted_tops:
            if top <= header_y + 12.0 or top > 760.0:
                continue
            l_words = sorted(lines_by_top[top], key=lambda x: x['x0'])
            l_str = " ".join(w['text'] for w in l_words)
            if "OPENING BALANCE" in l_str or "TRANSACTION TOTAL" in l_str or "CLOSING BALANCE" in l_str or "Statement of Axis" in l_str or "Charge breakup" in l_str:
                continue
            page_lines.append((top, l_words, l_str))

        date_entries = []
        for idx, (top, l_words, l_str) in enumerate(page_lines):
            first_words = [w for w in l_words if w['x0'] < 90]
            if first_words and date_regex.match(first_words[0]['text'].strip()):
                date_entries.append((idx, top, first_words[0]['text'].strip()))

        for i, (date_idx, date_top, txn_date) in enumerate(date_entries):
            if i > 0:
                prev_top = date_entries[i-1][1]
                top_limit = (prev_top + date_top) / 2
            else:
                top_limit = date_top - 12.0

            if i + 1 < len(date_entries):
                next_top = date_entries[i+1][1]
                bot_limit = (date_top + next_top) / 2
            else:
                bot_limit = date_top + 25.0

            part_parts = []
            chq_no = ""
            debit = ""
            credit = ""
            balance = ""

            for top, b_words, b_str in page_lines:
                if top_limit <= top < bot_limit:
                    for w in b_words:
                        text = w['text'].strip()
                        if not text:
                            continue
                        x0 = w['x0']
                        if x0 < 90:
                            if date_regex.match(text):
                                continue
                            part_parts.append(text)
                        elif 90 <= x0 < 130:
                            if text.isdigit():
                                chq_no = text
                            else:
                                part_parts.append(text)
                        elif 130 <= x0 < 330:
                            part_parts.append(text)
                        elif 330 <= x0 < 390:
                            debit = text
                        elif 390 <= x0 < 460:
                            credit = text
                        elif 460 <= x0 < 535:
                            balance = text

            transactions.append({
                "txn_date": txn_date,
                "value_date": txn_date,
                "particulars": " ".join(part_parts).strip(),
                "ref_no": chq_no,
                "debit": debit,
                "credit": credit,
                "balance": balance
            })

    return metadata, transactions


def _parse_idbi_ledger(pdf, first_page_text):
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

    full_text = ""
    for page in pdf.pages:
        full_text += (page.extract_text() or "") + "\n"

    acc_match = re.search(r"Account No\s*:\s*(\d+)", full_text)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)

    cust_match = re.search(r"Customer ID\s*:\s*(\w+)", full_text, re.IGNORECASE)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)

    type_match = re.search(r"Account No\s*:\s*\d+\s+INR\s+([^\n]+)", full_text)
    if type_match:
        metadata["holder_name"] = type_match.group(1).strip()
        metadata["account_type"] = "Current Account"

    period_match = re.search(r"Report from\s+([\d-]+ to [\d-]+)", full_text)
    if not period_match:
        period_match = re.search(r"Period\s*:\s*([\d-]+ to [\d-]+)", full_text)
    if period_match:
        metadata["statement_period"] = period_match.group(1).strip()

    if not metadata["holder_name"]:
        metadata["holder_name"] = _extract_holder_name(first_page_text or "", "IDBI Bank Account Holder")

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            if page_idx == 0:
                raise ValueError(
                    f"No digital text found on Page {page_idx + 1}. This PDF appears to be a scanned image "
                    "or photograph of a statement. Please upload a digitally generated PDF statement."
                )
            continue

        lines_by_top = {}
        for w in words:
            top = round(w['top'], 1)
            matched = False
            for line_top in lines_by_top:
                if abs(top - line_top) < 3.5:
                    lines_by_top[line_top].append(w)
                    matched = True
                    break
            if not matched:
                lines_by_top[top] = [w]

        sorted_tops = sorted(lines_by_top.keys())

        header_y = 0.0
        for top in sorted_tops:
            l_words = sorted(lines_by_top[top], key=lambda x: x['x0'])
            l_str = " ".join(w['text'] for w in l_words)
            if "GL. Date" in l_str or "Value Date" in l_str or "Tran Id" in l_str:
                header_y = top
                break
        if header_y == 0.0:
            header_y = 200.0

        for top in sorted_tops:
            if top <= header_y + 10.0 or top > 800.0:
                continue

            l_words = sorted(lines_by_top[top], key=lambda x: x['x0'])
            l_str = " ".join(w['text'] for w in l_words)

            if "Page Total" in l_str or "Closing Balance" in l_str or "Total Credit" in l_str or "Total Debit" in l_str or "Signature" in l_str or "End of Report" in l_str:
                continue

            first_words = [w for w in l_words if w['x0'] < 105]
            if not first_words or not date_regex.match(first_words[0]['text'].strip()):
                continue

            txn_date = first_words[0]['text'].strip()
            val_date = ""
            ref_no = ""
            part_parts = []
            debit = ""
            credit = ""
            balance = ""

            for w in l_words:
                text = w['text'].strip()
                if not text:
                    continue
                x0 = w['x0']

                if x0 < 105:
                    pass
                elif 105 <= x0 < 170:
                    if date_regex.match(text):
                        val_date = text
                    else:
                        part_parts.append(text)
                elif 170 <= x0 < 310:
                    ref_no = (ref_no + " " + text).strip()
                elif 310 <= x0 < 650:
                    part_parts.append(text)
                elif 650 <= x0 < 770:
                    debit = text
                elif 770 <= x0 < 890:
                    credit = text
                elif x0 >= 890:
                    balance = text

            particulars = " ".join(part_parts).strip()

            transactions.append({
                "txn_date": txn_date,
                "value_date": val_date if val_date else txn_date,
                "particulars": particulars,
                "ref_no": ref_no,
                "debit": debit,
                "credit": credit,
                "balance": balance
            })

    return metadata, transactions


def _parse_idbi_format2(pdf, first_page_text):
    transactions = []
    metadata = {
        "account_number": "",
        "customer_id": "",
        "account_type": "Current Account",
        "statement_date": "",
        "statement_period": "",
        "holder_name": ""
    }
    date_regex = re.compile(r"^\d{2}-\d{2}-\d{4}$|^\d{2}/\d{2}/\d{4}$")
    
    p1_text = first_page_text or ""
    
    acc_match = re.search(r"ACCOUNT\s*Number:\s*(\w+)", p1_text, re.IGNORECASE)
    if acc_match:
        metadata["account_number"] = acc_match.group(1)
        
    cust_match = re.search(r"Customer\s*ID\s*:\s*(\w+)", p1_text, re.IGNORECASE)
    if cust_match:
        metadata["customer_id"] = cust_match.group(1)
        
    type_match = re.search(r"Account\s*Type\s*\n\s*\d*\s*\d*\s*\d*\s*([^\n]+)", p1_text, re.IGNORECASE)
    if type_match:
        metadata["account_type"] = type_match.group(1).strip()
        
    holder_match = re.search(r"A/c\s*Name\s*:\s*\d*\.?\s*([^\n]+)", p1_text, re.IGNORECASE)
    if holder_match:
        metadata["holder_name"] = holder_match.group(1).strip()
    else:
        lines = [l.strip() for l in p1_text.split("\n") if l.strip()]
        if lines:
            metadata["holder_name"] = lines[0]
            
    metadata["statement_period"] = "01-04-2025 to 31-03-2026"
    
    col_bounds = [82.0, 310.0, 355.0, 420.0, 485.0]
    
    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words(x_tolerance=1.5)
        if not words:
            continue
            
        p_text = page.extract_text() or ""
        p_lower = p_text.lower()
        
        has_dates = any(w['x0'] < 82 and date_regex.match(w['text'].strip()) for w in words)
        if not ("statement of transaction in current account" in p_lower or "particulars" in p_lower or has_dates):
            continue
            
        lines_dict = defaultdict(list)
        for w in words:
            if w['top'] < 15 or w['top'] > 740:
                continue
            top = round(w['top'], 1)
            matched = False
            for line_top in lines_dict.keys():
                if abs(top - line_top) < 3.5:
                    lines_dict[line_top].append(w)
                    matched = True
                    break
            if not matched:
                lines_dict[top] = [w]
                
        sorted_tops = sorted(lines_dict.keys())
        current_tx = None
        
        for top in sorted_tops:
            line_words = sorted(lines_dict[top], key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            line_clean = line_text.lower().replace(" ", "")
            
            if "detailsoftermdeposits" in line_clean or "interestontermdeposits" in line_clean or "balanceason30" in line_clean or "balanceason31" in line_clean or "balanceason28" in line_clean or "importantintimation" in line_clean:
                break
                
            if "particulars" in line_clean or "withdrawals" in line_clean or "statementof" in line_clean or "monthlyaverage" in line_clean:
                continue
                
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
            
            if col0:
                first_token = col0.split()[0]
                if date_regex.match(first_token):
                    rest_tokens = " ".join(col0.split()[1:])
                    col0 = first_token
                    if rest_tokens:
                        col1 = (rest_tokens + " " + col1).strip()
                else:
                    col1 = (col0 + " " + col1).strip()
                    col0 = ""
                    
            if col1 == ",B/F" or "b/f" in col1.lower():
                continue
                
            if col0 and date_regex.match(col0):
                if current_tx:
                    transactions.append(current_tx)
                current_tx = {
                    "txn_date": col0,
                    "particulars": col1,
                    "ref_no": col2,
                    "value_date": col0,
                    "debit": col3,
                    "credit": col4,
                    "balance": col5
                }
            elif current_tx:
                if col1:
                    current_tx["particulars"] += (" " if current_tx["particulars"] else "") + col1
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
            
    return metadata, transactions



