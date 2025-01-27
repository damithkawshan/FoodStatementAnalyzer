import streamlit as st
import plotly.express as px
import pandas as pd
import pdftotext as pdf
import re
from utils.expense_classifier import classify_food_expenses
import io

st.set_page_config(
    page_title="Food Expense Analyzer",
    page_icon="🍽️",
    layout="wide"
)

class BankConfig:
    """
    Base class for bank configurations.
    Each subclass should implement its own parsing logic.
    """
    def __init__(self, name, company_reg_no, pattern):
        self.name = name
        self.company_reg_no = company_reg_no
        self.pattern = pattern


class DBSBankConfig(BankConfig):
    def __init__(self):
        super().__init__(
            name="DBS Bank Ltd",
            company_reg_no="Co. Reg. No. 196800306E",
            pattern=r"^\s*(\d{2} \w{3}) (.+?) (\d+\.\d{2}) (DB)$"
        )
    
    def parse_transaction(self, line):
        match = re.match(self.pattern, line)
        if match:
            return {
                "date": match.group(1),
                "description": match.group(2),
                "amount": float(match.group(3)),
                "type": match.group(4)
            }
        return None

class CitiBankConfig(BankConfig):
    def __init__(self):
        super().__init__(
            name="Citi Bank Singapore Ltd",
            company_reg_no="Co Reg No: 200309485K",
            pattern=r"^\s*(\d{2} \w{3}) (.+?) (\d+\.\d{2})$"
        )
    
    def parse_transaction(self, line):
        match = re.match(self.pattern, line)
        if match:
            description = re.sub(r"\b(SINGAPORE|SG)\b", "", match.group(2), flags=re.IGNORECASE).strip()
            return {
                "date": match.group(1),
                "description": description,
                "amount": float(match.group(3))
            }
        return None

class BankStatementParser:
    """
    Handles the identification and parsing of bank statements.
    """
    def __init__(self):
        self.bank_configs = [
            DBSBankConfig(),
            CitiBankConfig()
        ]
        self.bank_name = None

    def detect_bank(self, first_page_text):
        for config in self.bank_configs:
            if config.company_reg_no in first_page_text:
                self.bank_name = config.name
                return config
        return None

    def parse_pdf(self, pdf_file):
        pdfstream = pdf.PDF(pdf_file, physical=True)
        first_page_text = pdfstream[0]
        bank_config = self.detect_bank(first_page_text)

        if not bank_config:
            raise ValueError("Unable to detect bank from the statement.")

        transactions = []
        for page in pdfstream:
            lines = page.split('\n')
            for line in lines:
                line = line.strip()
                transaction = bank_config.parse_transaction(line)
                if transaction:
                    transactions.append(transaction)

        return transactions

def main():
    st.title("🍽️ Food Expense Analyzer")
    st.write("Upload your bank statement (PDF or Image) to analyze food-related expenses")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

    if uploaded_file is not None:
        parser = BankStatementParser()

        try:
            # Parse the PDF and extract transactions
            transactions = parser.parse_pdf(uploaded_file)

            if transactions:
                transactions_df = pd.DataFrame(transactions)
                st.subheader(f"Expenses : {parser.bank_name}")
                st.dataframe(transactions_df)
            else:
                st.warning("No transactions detected in the uploaded file.")

        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")
            st.write("Please make sure you've uploaded a valid bank statement file.")

if __name__ == "__main__":
    main()