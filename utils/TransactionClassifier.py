import streamlit as st
import pandas as pd
import yaml
import os
import re

class TransactionClassifier:
    def __init__(self, df,df_metadata):
        self.df = df
        self.df_metadata = df_metadata
        with open('attached_assets/categories_new.yaml', 'r') as file:
            self.classification_map = yaml.safe_load(file)
        self.known_types = list(self.classification_map.keys())

    def classify_transaction(self, description):
        """Automatically classify transactions based on description keywords."""
        description = description.lower()
        for category, data in self.classification_map.items():
            keywords = data["items"]
            if any(keyword in description for keyword in keywords):
                return category
        return "Unclassified"

    def classify_dataframe(self):
        """Apply classification to the entire dataframe."""
        self.df["predicted_type"] = self.df["description"].apply(self.classify_transaction)


        
    # Save updated data to CSV
    def save_to_csv(self, file_path, editable_df):
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            combined_df = pd.concat([existing_df, editable_df]).drop_duplicates(subset=["bank_id", "transaction_idx"], keep="last")
            combined_df.to_csv(file_path, index=False)
        else:
            editable_df.to_csv(file_path, index=False)

    def render_streamlit_ui(self):
        """Render Streamlit UI."""
        # st.title("Transaction Analyzer")

        # Apply automatic classification
        self.classify_dataframe()

        # st.subheader("Classify Transactions")

        # Create a copy of the dataframe to avoid modifying the original one
        editable_df = self.df.copy()

        # Add a column for manual classification if it doesn't exist
        if "manual_type" not in editable_df.columns:
            editable_df["manual_type"] = "Unclassified"

        # Create an interactive table
        col1, col2, col3 = st.columns(3)

        # Apply custom CSS to change the background color of the select box
        def apply_custom_css():
            css = """
            <style>
            .stSelectbox div[data-baseweb="select"] > div {
                background-color: #FFDDC1; /* Default color */
            }
            """
            for category, color in {
                "transport": "#FFDDC1",
                "dining": "#C1FFD7",
                "shopping": "#C1D4FF",
                "Unclassified": "#FFD1DC"
            }.items():
                css += f"""
                .stSelectbox div[data-baseweb="select"] > div[aria-label="{category}"] {{
                    background-color: {color};
                }}
                """
            css += "</style>"
            st.markdown(css, unsafe_allow_html=True)

        apply_custom_css()

        editable_df["manual_type"] = editable_df.apply(
            lambda row: (
                col1 if row.name % 3 == 0 else col2 if row.name % 3 == 1 else col3
            ).selectbox(
                f"Transaction: {row['description']} - {row['amount']}",
                options=self.known_types + ["Unclassified"],
                index=self.known_types.index(row["predicted_type"])
                if row["predicted_type"] in self.known_types else len(self.known_types),
                key=f"type_{row.name}"
            ),
            axis=1
        )

        # Update the original dataframe with the manually classified types
        self.df["manual_type"] = editable_df["manual_type"]

        # Save Button
        if st.button("Save Updated Data"):
            csv_filename = "attached_assets/transactions_"+self.df_metadata['month']+"_"+self.df_metadata['year']+".csv"
            # self.df.to_csv(csv_filename, index=False)
            self.save_to_csv(csv_filename,editable_df)
            st.success("Updated transactions saved!")
