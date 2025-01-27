import streamlit as st
import plotly.express as px
import pandas as pd
from utils.pdf_processor import extract_transactions_from_pdf
from utils.expense_classifier import classify_food_expenses
import io

st.set_page_config(
    page_title="Food Expense Analyzer",
    page_icon="🍽️",
    layout="wide"
)

def main():
    st.title("🍽️ Food Expense Analyzer")
    st.write("Upload your bank statement (PDF) to analyze food-related expenses")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        try:
            # Read PDF content
            pdf_bytes = io.BytesIO(uploaded_file.read())
            
            with st.spinner("Extracting transactions..."):
                transactions_df = extract_transactions_from_pdf(pdf_bytes)
                
            if transactions_df is not None and not transactions_df.empty:
                # Classify food expenses
                food_expenses = classify_food_expenses(transactions_df)
                
                # Display summary statistics
                st.subheader("📊 Summary Statistics")
                col1, col2, col3 = st.columns(3)
                
                total_food_expense = food_expenses['amount'].sum()
                avg_transaction = food_expenses['amount'].mean()
                transaction_count = len(food_expenses)
                
                col1.metric("Total Food Expenses", f"${total_food_expense:.2f}")
                col2.metric("Average Transaction", f"${avg_transaction:.2f}")
                col3.metric("Number of Food Transactions", transaction_count)

                # Display transactions
                st.subheader("🧾 Food-Related Transactions")
                st.dataframe(food_expenses)

                # Visualizations
                st.subheader("📈 Visualizations")
                
                # Time series plot
                fig1 = px.line(food_expenses, x='date', y='amount',
                             title='Food Expenses Over Time')
                st.plotly_chart(fig1)

                # Category breakdown if categories exist
                if 'category' in food_expenses.columns:
                    fig2 = px.pie(food_expenses, values='amount', names='category',
                                title='Food Expense Categories')
                    st.plotly_chart(fig2)

            else:
                st.error("No transactions found in the PDF. Please ensure it's a valid bank statement.")

        except Exception as e:
            st.error(f"Error processing the PDF: {str(e)}")
            st.write("Please make sure you've uploaded a valid bank statement PDF.")

    # Instructions
    with st.sidebar:
        st.header("📖 Instructions")
        st.write("""
        1. Upload your bank statement in PDF format
        2. Wait for the analysis to complete
        3. View your food expense breakdown
        
        **Supported Formats:**
        - Most common bank statement PDFs
        - Statements should contain transaction details
        
        **Privacy Note:**
        Your data is processed locally and is not stored or shared.
        """)

if __name__ == "__main__":
    main()
