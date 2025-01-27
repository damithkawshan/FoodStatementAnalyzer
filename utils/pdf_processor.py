import PyPDF2
import pandas as pd
import re
from datetime import datetime

def extract_transactions_from_pdf(pdf_file):
    """
    Extract transactions from PDF bank statement.
    
    Args:
        pdf_file: BytesIO object containing PDF data
    
    Returns:
        pandas DataFrame with transactions
    """
    try:
        # Read PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Regular expressions for common date and amount patterns
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        amount_pattern = r'\$?\s*\d+,?\d*\.\d{2}'
        
        # Split text into lines and process each line
        transactions = []
        lines = text.split('\n')
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Try to find date and amount
            dates = re.findall(date_pattern, line)
            amounts = re.findall(amount_pattern, line)
            
            if dates and amounts:
                try:
                    # Clean and parse date
                    date_str = dates[0]
                    date = pd.to_datetime(date_str)
                    
                    # Clean amount (remove $ and ,)
                    amount_str = amounts[-1].replace('$', '').replace(',', '')
                    amount = float(amount_str)
                    
                    # Get description (everything between date and amount)
                    description = line.strip()
                    
                    transactions.append({
                        'date': date,
                        'description': description,
                        'amount': amount
                    })
                except (ValueError, IndexError):
                    continue

        # Create DataFrame
        if transactions:
            df = pd.DataFrame(transactions)
            df = df.sort_values('date')
            return df
        
        return pd.DataFrame()

    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")
