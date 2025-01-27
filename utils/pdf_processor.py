import PyPDF2
import pandas as pd
import re
from datetime import datetime

def extract_transactions_from_pdf(pdf_file):
    """
    Extract transactions from PDF bank statement with improved pattern matching.

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
            text += page.extract_text() + "\n"

        # Enhanced patterns for different date formats
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY, MM/DD/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}',  # January 1, 2024
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}'     # 1 January 2024
        ]

        # Enhanced amount pattern
        amount_pattern = r'\$?\s*-?\d{1,3}(?:,\d{3})*\.\d{2}'

        # Split text into lines and process each line
        transactions = []
        lines = text.split('\n')

        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue

            # Try each date pattern
            date_found = None
            for pattern in date_patterns:
                dates = re.findall(pattern, line)
                if dates:
                    date_found = dates[0]
                    break

            # Find amounts
            amounts = re.findall(amount_pattern, line)

            if date_found and amounts:
                try:
                    # Parse date with multiple format attempts
                    date = None
                    date_formats = [
                        '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
                        '%B %d, %Y', '%d %B %Y',
                        '%b %d, %Y', '%d %b %Y'
                    ]

                    for fmt in date_formats:
                        try:
                            date = pd.to_datetime(date_found, format=fmt)
                            break
                        except:
                            continue

                    if date is None:
                        date = pd.to_datetime(date_found)

                    # Clean amount (remove $ and ,)
                    amount_str = amounts[-1].replace('$', '').replace(',', '')
                    amount = float(amount_str)

                    # Extract description (remove date and amount from line)
                    description = line.strip()
                    for pattern in date_patterns:
                        description = re.sub(pattern, '', description)
                    description = re.sub(amount_pattern, '', description)
                    description = ' '.join(description.split())  # Clean up whitespace

                    if description and date and amount:
                        transactions.append({
                            'date': date,
                            'description': description,
                            'amount': abs(amount)  # Store positive values
                        })
                except (ValueError, IndexError) as e:
                    print(f"Error processing line: {line}")
                    print(f"Error details: {str(e)}")
                    continue

        # Create DataFrame
        if transactions:
            df = pd.DataFrame(transactions)
            df = df.sort_values('date')
            # Remove any duplicate transactions
            df = df.drop_duplicates(subset=['date', 'description', 'amount'])
            return df

        return pd.DataFrame()

    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")