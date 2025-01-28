import pandas as pd
import streamlit as st
import yaml

class ExpenseAnalyser:
    def __init__(self):
        self.transactions = None
        with open('attached_assets/categories_new.yaml', 'r') as file:
            self.classification_map = yaml.safe_load(file)
        self.known_types = list(self.classification_map.keys())

    def get_category_total(self, category):
        if self.transactions is None:
            return 0
        total = 0
        for transaction in self.transactions:
            if transaction['manual_type'] == category:
                total += transaction['amount']
        return total

    def get_transactions_df(self):
        uploaded_file = st.file_uploader("Choose a file", type=["csv"])
        if uploaded_file is not None:
            transactions_df = pd.read_csv(uploaded_file)
            #display only date	description	amount and manual type
            transactions_visual = transactions_df[['date', 'description', 'amount', 'manual_type']]
            def color_row(row):
                color = self.classification_map.get(row['manual_type'], {}).get('colorcode', '#FFFFFF')
                return ['background-color: {}'.format(color)] * len(row)

            transactions_visual = transactions_visual.style.apply(color_row, axis=1)
            st.dataframe(transactions_visual)
            self.transactions = transactions_df.to_dict('records')

            for category in self.known_types:
                total = self.get_category_total(category)
                st.write(f"Total {category}: {total}")
        else:
            st.warning("Please upload a CSV file to view transaction details.")

        return
