import os
import sys
import unittest

# Add project root to path to import local modules
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from parser import parse_pdf
from excel_generator import generate_excel

class TestKVBStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784459064141.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "1244013000000032")
        self.assertEqual(self.metadata.get("customer_id"), "34670247")
        self.assertEqual(self.metadata.get("account_type"), "KVB PREMIUM CA")
        self.assertEqual(self.metadata.get("holder_name"), "SRI LAKSHMI GANAPA")
        self.assertEqual(self.metadata.get("statement_period"), "01-Apr-2025 to 31-Mar-2026")

    def test_transaction_count(self):
        self.assertIsNotNone(self.transactions)
        self.assertEqual(len(self.transactions), 19)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertTrue(first_tx["txn_date"].startswith("01-APR-2025"))
        self.assertEqual(first_tx["value_date"], "01-APR-2025")
        self.assertEqual(first_tx["particulars"], "B/F...")
        self.assertEqual(first_tx["debit"], "")
        self.assertEqual(first_tx["credit"], "")
        self.assertEqual(first_tx["balance"], "0.00")

class TestIndianBankStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784461310792.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "7261975413")
        self.assertEqual(self.metadata.get("customer_id"), "IFSC: IDIB000N033")
        self.assertEqual(self.metadata.get("account_type"), "Savings")
        self.assertEqual(self.metadata.get("holder_name"), "Deepika R")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 19)

class TestIndianBankCurrentStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784543027238.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "7728926762")
        self.assertEqual(self.metadata.get("customer_id"), "IFSC: IDIB000N033")
        self.assertEqual(self.metadata.get("account_type"), "CA-IND GROW PROFESSIONAL-INR")
        self.assertEqual(self.metadata.get("holder_name"), "LORDAN INDUCTION KITCHEN EQUIPMENT LLP")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 18)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "16/05/25")
        self.assertEqual(first_tx["particulars"], "SMS_CHGS_MARCH-25_QT 00000000000098058 /SERVICE CHARGES")
        self.assertEqual(first_tx["debit"], "3.00")
        self.assertEqual(first_tx["balance"], "8138.20")

class TestUnionBankStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784462530804.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "166010100085567")
        self.assertEqual(self.metadata.get("customer_id"), "54695820")
        self.assertEqual(self.metadata.get("account_type"), "SB GENERAL")
        self.assertEqual(self.metadata.get("holder_name"), "MISSDEEPIKA R")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 970)

class TestHDFCStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784529946292.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("holder_name"), "M/S. SRIGURUDATTAMENSHOSTEL")
        self.assertEqual(self.metadata.get("statement_period"), "01/04/2025 to 31/03/2026")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 510)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "20/09/25")
        self.assertEqual(first_tx["ref_no"], "0000000000000006")
        self.assertEqual(first_tx["credit"], "100,000.00")
        self.assertEqual(first_tx["balance"], "100,000.00")

class TestIndusIndStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784529946297.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "259360036055")
        self.assertEqual(self.metadata.get("customer_id"), "68138236")
        self.assertEqual(self.metadata.get("account_type"), "Current Choice Account")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 742)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "01 Apr 2025")
        self.assertEqual(first_tx["credit"], "5.90")
        self.assertEqual(first_tx["balance"], "91,783.55")

class TestICICIStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784529946323.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "007701000347")
        self.assertEqual(self.metadata.get("customer_id"), "7721129")
        self.assertEqual(self.metadata.get("holder_name"), "MS.VIJAYASHRI PRASAD")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 638)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "01-04-2025")
        self.assertEqual(first_tx["balance"], "5,81,843.00")

class TestKotakStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784529946351.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "7947185807")
        self.assertEqual(self.metadata.get("customer_id"), "xxxxxx044")
        self.assertEqual(self.metadata.get("statement_period"), "01 Jun 2026 - 30 Jun 2026")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 124)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "01 Jun 2026")
        self.assertEqual(first_tx["ref_no"], "UPI-615218241984")
        self.assertEqual(first_tx["debit"], "70.00")
        self.assertEqual(first_tx["balance"], "900.69")

class TestAxisScannedPDF(unittest.TestCase):
    def test_scanned_pdf_error(self):
        pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784529946705.pdf"
        with self.assertRaises(ValueError) as context:
            parse_pdf(pdf_path)
        self.assertIn("No digital text found on Page 1", str(context.exception))

class TestPNBStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784533567506.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "1063102100000495")
        self.assertEqual(self.metadata.get("customer_id"), "IFSC: PUNB0106310")
        self.assertEqual(self.metadata.get("holder_name"), "KAMALAM GEETHALAYA APARTMENT FLAT OWNERS ASSOCIATION")
        self.assertEqual(self.metadata.get("statement_period"), "01-04-2025 to 31-03-2026")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 157)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "31-03-2026")
        self.assertEqual(first_tx["particulars"], "IMPS- IN/609142769931/971 0225000/PARAMAN")
        self.assertEqual(first_tx["credit"], "2,000.00")
        self.assertEqual(first_tx["balance"], "59,002.14")

class TestSCBStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784533567507.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "42611829874")
        self.assertEqual(self.metadata.get("holder_name"), "MS SWETHA SHARMA")
        self.assertEqual(self.metadata.get("statement_period"), "01 Jun 2026 to 30 Jun 2026")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 44)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "01 Jun 2026")
        self.assertEqual(first_tx["particulars"], "BALANCE FORWARD")
        self.assertEqual(first_tx["balance"], "154,403.00")

class TestSBIScannedPDF(unittest.TestCase):
    def test_scanned_pdf_error(self):
        # SBI is image/scanned only, should raise ValueError
        pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784533567672.pdf"
        with self.assertRaises(ValueError) as context:
            parse_pdf(pdf_path)
        self.assertIn("No digital text found on Page 1", str(context.exception))

class TestBoBStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784540144454.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "05640200030545")
        self.assertEqual(self.metadata.get("holder_name"), "M/S. OMEXA FORMULARY PRIVATE LIMITED")
        self.assertEqual(self.metadata.get("account_type"), "BARODA ADVANTAGE CURRENT")
        self.assertEqual(self.metadata.get("statement_period"), "24-10-2023 to 03-01-2024")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 23)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "24-10-23")
        self.assertEqual(first_tx["particulars"], "DIGITB-VADODAR")
        self.assertEqual(first_tx["balance"], "0")

class TestICICIHakkemStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784554625073.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "606901183459")
        self.assertEqual(self.metadata.get("holder_name"), "M SYED ABDUL HAKKEM")
        self.assertEqual(self.metadata.get("statement_period"), "April 1, 2025 to March 31, 2026")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 2507)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "01.04.2025")
        self.assertEqual(first_tx["particulars"], "Q035606811@ybl UPI/Q035606811@ybl/Payment from Ph/YES BANK LIMITE/622838492116/IBLed4439b413fe4534ae0a d00e2afb8433/")
        self.assertEqual(first_tx["debit"], "20.00")
        self.assertEqual(first_tx["balance"], "4876.87")

class TestICICIMultiPageStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784554809745.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "603301110156")
        self.assertEqual(self.metadata.get("statement_period"), "January 30, 2025 - January 29, 2026")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 817)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "30-01-2025")
        self.assertEqual(first_tx["particulars"], "B/F NEFT-HDFCN52025013029279369-EXCEL HR")
        self.assertEqual(first_tx["balance"], "10,008.83")

class TestPasswordProtectedPDF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__encrypted.pdf"

    def test_missing_password_raises_required(self):
        with self.assertRaises(ValueError) as context:
            parse_pdf(self.pdf_path)
        self.assertEqual(str(context.exception), "PASSWORD_REQUIRED")

    def test_incorrect_password_raises_incorrect(self):
        with self.assertRaises(ValueError) as context:
            parse_pdf(self.pdf_path, password="wrong_pwd")
        self.assertEqual(str(context.exception), "PASSWORD_INCORRECT")

    def test_correct_password_parses_successfully(self):
        metadata, transactions = parse_pdf(self.pdf_path, password="decrypt123")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.get("account_number"), "1244013000000032")
        self.assertEqual(len(transactions), 19)

class TestIndusIndNewStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784641803738.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "159840161447")
        self.assertEqual(self.metadata.get("customer_id"), "3XXXX386")
        self.assertEqual(self.metadata.get("account_type"), "INDUS MAXIMA")
        self.assertEqual(self.metadata.get("statement_period"), "01 Apr 2025 to 31 Mar 2026")
        self.assertEqual(self.metadata.get("holder_name"), "P VANI")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 439)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "31 Mar 2026")
        self.assertEqual(first_tx["particulars"], "159840161447:Int.Pd:01-0 1-2026 to 31-03-2026")
        self.assertEqual(first_tx["ref_no"], "S99894669")
        self.assertEqual(first_tx["credit"], "697.00")
        self.assertEqual(first_tx["balance"], "68742.17")

class TestCanaraStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784651065922.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "0908101053082")
        self.assertEqual(self.metadata.get("customer_id"), "116613867")
        self.assertEqual(self.metadata.get("account_type"), "CANARA SB GENERAL")
        self.assertEqual(self.metadata.get("statement_period"), "01-04-2025 to 31-03-2026")
        self.assertEqual(self.metadata.get("holder_name"), "Ms COMMANDERS COURT CONDOMINIUM O W A S S")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 106)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "01-APR-25")
        self.assertEqual(first_tx["particulars"], "B/F ...")
        self.assertEqual(first_tx["credit"], "865,868.00")
        self.assertEqual(first_tx["balance"], "865,868.00")

class TestKotakCurrentStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\media__1784651065924.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "7512114362")
        self.assertEqual(self.metadata.get("customer_id"), "xxxxxx218")
        self.assertEqual(self.metadata.get("account_type"), "Current")
        self.assertEqual(self.metadata.get("statement_period"), "30 Sep 2025 - 29 Oct 2025")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 13)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "30 Sep 2025")
        self.assertEqual(first_tx["particulars"], "NEFT ICIN427351127937 R P S CONSULTING PVT LTD IC")
        self.assertEqual(first_tx["ref_no"], "NEFTINW-1349690237")
        self.assertEqual(first_tx["credit"], "31,500.00")
        self.assertEqual(first_tx["balance"], "31,500.00")

class TestDBSStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1784789014825.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "0995322000000542")
        self.assertEqual(self.metadata.get("customer_id"), "2L7029805")
        self.assertEqual(self.metadata.get("account_type"), "SBOTH")
        self.assertEqual(self.metadata.get("statement_period"), "01/04/2025 to 31/03/2026")
        self.assertEqual(self.metadata.get("holder_name"), "VARSHA MENON")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 24)

    def test_first_transaction(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "02/04/2025")
        self.assertEqual(first_tx["debit"], "450.00")
        self.assertEqual(first_tx["balance"], "3,081.37")

class TestRBLStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1784789014833.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "409000651744")
        self.assertEqual(self.metadata.get("customer_id"), "20131094")
        self.assertEqual(self.metadata.get("account_type"), "CURRENT")
        self.assertEqual(self.metadata.get("holder_name"), "VM DESIGN WORKS")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 383)

class TestSBINewStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1784789014914.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "20304011511")
        self.assertEqual(self.metadata.get("customer_id"), "88512235835")
        self.assertEqual(self.metadata.get("account_type"), "REGULAR SB CHQ-INDIVIDUALS")
        self.assertEqual(self.metadata.get("holder_name"), "Miss. AYUSHI AISHWARYA")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 1916)

class TestICIDetailedStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1785065548665.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "080205019882")
        self.assertEqual(self.metadata.get("holder_name"), "CS EDUCATION AND RESEARCH FOUNDATION")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 596)

    def test_first_and_last_transactions(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["ref_no"], "S74208993")
        self.assertEqual(first_tx["credit"], "22,500.00")
        self.assertEqual(first_tx["balance"], "3,41,192.36")
        
        last_tx = self.transactions[-1]
        self.assertEqual(last_tx["ref_no"], "S83363498")
        self.assertEqual(last_tx["credit"], "3,500.00")
        self.assertEqual(last_tx["balance"], "1,60,300.39")

class TestICIDetailedStatement2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1785066865189.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "605705017059")
        self.assertEqual(self.metadata.get("holder_name"), "CS EDUCATION AND RESEARCH FOUNDATION")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 571)

    def test_first_and_last_transactions(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["ref_no"], "S75545851")
        self.assertEqual(first_tx["debit"], "9,412.00")
        self.assertEqual(first_tx["balance"], "4,77,491.52")
        
        last_tx = self.transactions[-1]
        self.assertEqual(last_tx["ref_no"], "S64530179")
        self.assertEqual(last_tx["debit"], "1,50,000.00")
        self.assertEqual(last_tx["balance"], "3,89,201.71")

class TestSIBStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1785152119756.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "0043053000012455")
        self.assertEqual(self.metadata.get("customer_id"), "A47524562")
        self.assertEqual(self.metadata.get("account_type"), "SAVINGS - GENERAL")
        self.assertEqual(self.metadata.get("holder_name"), "VIMAL RAJ R")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 586)

    def test_first_and_last_transactions(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "05-04-25")
        self.assertEqual(first_tx["credit"], "3,199.00")
        self.assertEqual(first_tx["balance"], "45,547.70Cr")
        
        last_tx = self.transactions[-1]
        self.assertEqual(last_tx["txn_date"], "01-04-26")
        self.assertEqual(last_tx["credit"], "2,50,000.00")
        self.assertEqual(last_tx["balance"], "3,47,178.92Cr")

class TestAxisCorporateStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1785170485411.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "921020001896963")
        self.assertEqual(self.metadata.get("customer_id"), "903901942")
        self.assertEqual(self.metadata.get("account_type"), "CA - CURRENT A/C FOR ESCROW ARRANGEMENTS")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 11)

    def test_first_and_last_transactions(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "19/02/2021")
        self.assertEqual(first_tx["credit"], "29400000.00")
        self.assertEqual(first_tx["balance"], "29400000.00")
        
        last_tx = self.transactions[-1]
        self.assertEqual(last_tx["txn_date"], "31/12/2021")
        self.assertEqual(last_tx["debit"], "591505.00")
        self.assertEqual(last_tx["balance"], "422622.00")

class TestIDFCStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1785241057136.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "10220287318")
        self.assertEqual(self.metadata.get("customer_id"), "65******62")
        self.assertEqual(self.metadata.get("account_type"), "Gold")
        self.assertEqual(self.metadata.get("holder_name"), "BUSINESS TABLOID PUBLICATIONS LLP")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 203)

    def test_first_and_last_transactions(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["txn_date"], "04-Apr-2025")
        self.assertEqual(first_tx["credit"], "10.00")
        self.assertEqual(first_tx["balance"], "50,010.00")
        
        last_tx = self.transactions[-1]
        self.assertEqual(last_tx["txn_date"], "21-Mar-2026")
        self.assertEqual(last_tx["debit"], "26,197.00")
        self.assertEqual(last_tx["balance"], "165.43")

class TestICIDetailedStatement3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = r"C:\Users\rtrpr\.gemini\antigravity\brain\798c510d-3f38-4457-8c71-0896ee2415ef\.user_uploaded\media__1785322159536.pdf"
        cls.metadata, cls.transactions = parse_pdf(cls.pdf_path)

    def test_metadata_extraction(self):
        self.assertIsNotNone(self.metadata)
        self.assertEqual(self.metadata.get("account_number"), "000105039062")
        self.assertEqual(self.metadata.get("customer_id"), "597491707")
        self.assertEqual(self.metadata.get("account_type"), "Current Account")
        self.assertEqual(self.metadata.get("holder_name"), "BEYOND REHAB")

    def test_transaction_count(self):
        self.assertEqual(len(self.transactions), 1741)

    def test_first_and_last_transactions(self):
        first_tx = self.transactions[0]
        self.assertEqual(first_tx["sno"], "1")
        self.assertEqual(first_tx["txn_date"], "15-Jul-2025")
        self.assertEqual(first_tx["credit"], "1400.00")
        self.assertEqual(first_tx["balance"], "178321.96")
        
        last_tx = self.transactions[-1]
        self.assertEqual(last_tx["sno"], "1741")
        self.assertEqual(last_tx["txn_date"], "15-Jul-2026")
        self.assertEqual(last_tx["credit"], "900.00")
        self.assertEqual(last_tx["balance"], "327405.27")

if __name__ == '__main__':
    unittest.main()
