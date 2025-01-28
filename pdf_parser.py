import streamlit as st
import plotly.express as px
import pandas as pd
import pdftotext as pdf
from utils.TransactionClassifier import TransactionClassifier as ta
import utils.BankConfig as bc
from utils.ExpenseAnalyser import ExpenseAnalyser as ea
import io

st.set_page_config(
    page_title="Food Expense Analyzer",
    page_icon="🍽️",
    layout="wide"
)


class BankStatementParser:
    """
    Handles the identification and parsing of bank statements.
    """
    def __init__(self):
        self.bank_configs = [
            bc.DBSBankConfig(),
            bc.CitiBankConfig()
        ]
        self.bank_name = None
        self.bank_config = None

    def detect_bank(self, first_page_text):
        for config in self.bank_configs:
            if config.company_reg_no in first_page_text:
                self.bank_name = config.name
                return config
        return None

    def parse_pdf(self, pdf_file):
        pdfstream = pdf.PDF(pdf_file, physical=True)
        first_page_text = pdfstream[0]
        self.bank_config = self.detect_bank(first_page_text)
        bank_metadata = self.bank_config.get_statement_metadata(pdf_file.name)
        # st.write(f"Bank Name: {bank_metadata['bank']}")
        # st.write(f"Company Reg No: {bank_metadata['compang_reg_no']}")
        # st.write(f"Statement Month: {bank_metadata['month']}")
        # st.write(f"Statement Year: {bank_metadata['year']}")

        if not self.bank_config:
            raise ValueError("Unable to detect bank from the statement.")

        transactions = []
        transaction_idx = 0
        for page in pdfstream:
            lines = page.split('\n')
            for line in lines:
                line = line.strip()
                transaction = self.bank_config.parse_transaction(line)
                if transaction:
                    transaction['transaction_idx'] = transaction_idx
                    transactions.append(transaction)
                    transaction_idx += 1

        return transactions
    
class ExtractTransactions:
    def __init__(self, transactions):
        self.transactions = transactions

    def extract_transactions(self):
        st.write("Upload your bank statement (PDF or Image) to analyze food-related expenses")

        uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

        if uploaded_file is not None:
            parser = BankStatementParser()

            try:
                # Parse the PDF and extract transactions
                transactions = parser.parse_pdf(uploaded_file)

                if transactions:
                    transactions_df = pd.DataFrame(transactions)

                    df_metadata = {"bank_id":parser.bank_config.company_reg_no,
                                   "year": parser.bank_config.year, 
                                   "month": parser.bank_config.month}
                    
                    st.subheader(f"Statement Data from {parser.bank_name} | {parser.bank_config.month} {parser.bank_config.year}")

                    analyzer = ta(transactions_df,df_metadata)
                    analyzer.render_streamlit_ui()

                else:
                    st.warning("No transactions detected in the uploaded file.")

            except Exception as e:
                st.error(f"Error processing the file: {str(e)}")
                st.write("Please make sure you've uploaded a valid bank statement file.")

def main():
    # Create tab for category wise analysis
    tab1, tab2 = st.tabs(["Category Analysis", "Transaction Details"])
    extractor = ExtractTransactions([])
    expense_analyser = ea()

    with tab1:
        st.subheader("Category Wise Analysis")
        extractor.extract_transactions()
        # st.write(category_summary)

    with tab2:
        st.subheader("Transaction Details")
        expense_analyser.get_transactions_df()

if __name__ == "__main__":
    main()