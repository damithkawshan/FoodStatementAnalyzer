import streamlit as st
import plotly.express as px
import pandas as pd
from utils.pdf_processor import extract_transactions_from_file
from utils.expense_classifier import classify_food_expenses
import io

st.set_page_config(
    page_title="Food Expense Analyzer",
    page_icon="🍽️",
    layout="wide"
)

def save_transactions_to_file(transactions_df):
    """Save transactions to records.txt file."""
    with open('records.txt', 'w') as f:
        f.write("Food Expense Records\n")
        f.write("===================\n\n")

        for _, row in transactions_df.iterrows():
            f.write(f"Date: {row['date'].strftime('%d/%m/%Y')}\n")
            f.write(f"Description: {row['description']}\n")
            f.write(f"Amount: SGD {row['amount']:.2f}\n")
            if 'category' in row:
                f.write(f"Category: {row['category']}\n")
            f.write("-" * 50 + "\n")

def main():
    st.title("🍽️ Food Expense Analyzer")
    st.write("Upload your bank statement (PDF or Image) to analyze food-related expenses")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        try:
            # Read file content
            file_bytes = io.BytesIO(uploaded_file.read())

            with st.spinner("Extracting transactions..."):
                transactions_df = extract_transactions_from_file(file_bytes)

            if transactions_df is not None and not transactions_df.empty:
                # Classify food expenses
                food_expenses = classify_food_expenses(transactions_df)

                # Save transactions to file
                save_transactions_to_file(food_expenses)
                st.success("✅ Transactions saved to records.txt")

                # Display summary statistics
                st.subheader("📊 Summary Statistics")
                col1, col2, col3 = st.columns(3)

                total_food_expense = food_expenses['amount'].sum()
                avg_transaction = food_expenses['amount'].mean()
                transaction_count = len(food_expenses)

                col1.metric("Total Food Expenses", f"SGD {total_food_expense:.2f}")
                col2.metric("Average Transaction", f"SGD {avg_transaction:.2f}")
                col3.metric("Number of Food Transactions", transaction_count)

                # Display transactions
                st.subheader("🧾 Food-Related Transactions")
                # Format the amount column to show SGD
                display_df = food_expenses.copy()
                display_df['amount'] = display_df['amount'].apply(lambda x: f"SGD {x:.2f}")
                st.dataframe(display_df)

                # Visualizations
                st.subheader("📈 Visualizations")

                # Time series plot
                fig1 = px.line(food_expenses, x='date', y='amount',
                             title='Food Expenses Over Time',
                             labels={'amount': 'Amount (SGD)', 'date': 'Date'})
                st.plotly_chart(fig1, use_container_width=True)

                # Category breakdown if categories exist
                if 'category' in food_expenses.columns:
                    fig2 = px.pie(food_expenses, values='amount', names='category',
                                title='Food Expense Categories')
                    st.plotly_chart(fig2, use_container_width=True)

            else:
                st.error("No transactions found in the file. Please ensure it's a valid bank statement.")

        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")
            st.write("Please make sure you've uploaded a valid bank statement file.")

    # Instructions
    with st.sidebar:
        st.header("📖 Instructions")
        st.write("""
        1. Upload your bank statement (PDF or Image format)
        2. Wait for the analysis to complete
        3. View your food expense breakdown

        **Supported Formats:**
        - PDF bank statements
        - Image files (PNG, JPG)
        - Statements should contain transaction details

        **Privacy Note:**
        Your data is processed locally and is not stored or shared.

        **Export:**
        Transactions are automatically saved to 'records.txt'
        """)

if __name__ == "__main__":
    main()