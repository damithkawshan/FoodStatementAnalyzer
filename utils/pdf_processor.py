import PyPDF2
import pandas as pd
import re
from datetime import datetime
from PIL import Image
import pytesseract
from io import BytesIO

def extract_text_from_image(image_file):
    """Extract text from image using OCR."""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def detect_statement_format(text):
    """
    Detect bank statement format based on content patterns.
    Returns a tuple of (format_name, currency_symbol, date_format)
    """
    text_lower = text.lower()

    # Singapore Bank Format
    if 'singapore dollar' in text_lower or 'sgd' in text_lower:
        return ('singapore', 'SGD', '%d/%m/%Y')

    # US Bank Format
    elif 'usd' in text_lower or '$' in text_lower:
        return ('us', 'USD', '%m/%d/%Y')

    # UK Bank Format
    elif 'gbp' in text_lower or '£' in text_lower:
        return ('uk', 'GBP', '%d/%m/%Y')

    # Default format
    return ('default', 'SGD', '%d/%m/%Y')

def extract_transactions_from_file(file):
    """
    Extract transactions from PDF bank statement or image with improved pattern matching.
    Supports multiple bank statement formats.

    Args:
        file: BytesIO object containing PDF or image data

    Returns:
        pandas DataFrame with transactions
    """
    try:
        # Try to determine if it's PDF or image
        try:
            PyPDF2.PdfReader(file)
            is_pdf = True
        except:
            is_pdf = False

        # Reset file pointer
        file.seek(0)

        # Extract text based on file type
        if is_pdf:
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join(page.extract_text() for page in pdf_reader.pages)
        else:
            text = extract_text_from_image(file)

        # Detect statement format
        format_name, currency, date_format = detect_statement_format(text)

        # Define format-specific patterns
        patterns = {
            'singapore': {
                'date': r'\d{2}/\d{2}/\d{4}',
                'amount': r'\d+\.\d{2}',
                'balance': r'Balance|SGD',
            },
            'us': {
                'date': r'\d{2}/\d{2}/\d{4}',
                'amount': r'\$?\s*\d{1,3}(?:,\d{3})*\.\d{2}',
                'balance': r'Balance|\$',
            },
            'uk': {
                'date': r'\d{2}/\d{2}/\d{4}',
                'amount': r'£?\s*\d{1,3}(?:,\d{3})*\.\d{2}',
                'balance': r'Balance|£',
            },
            'default': {
                'date': r'\d{2}/\d{2}/\d{4}',
                'amount': r'\d+\.\d{2}',
                'balance': r'Balance',
            }
        }

        current_patterns = patterns[format_name]

        # Split text into lines and process each line
        transactions = []
        lines = text.split('\n')

        current_date = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for date
            dates = re.findall(current_patterns['date'], line)
            if dates:
                try:
                    current_date = pd.to_datetime(dates[0], format=date_format)
                except:
                    continue

            # Look for amounts
            amounts = re.findall(current_patterns['amount'], line)

            if current_date and amounts:
                try:
                    # Clean amount string
                    amount_str = amounts[-1].replace(currency, '').replace(',', '').strip()
                    amount = float(amount_str)

                    # Extract description
                    description = line
                    description = re.sub(current_patterns['date'], '', description)
                    description = re.sub(current_patterns['amount'], '', description)
                    description = re.sub(current_patterns['balance'], '', description)
                    description = ' '.join(description.split())

                    # Skip header rows and balance lines
                    if any(header in description.upper() for header in ['BALANCE', 'DATE', 'DESCRIPTION', 'WITHDRAWAL', 'DEPOSIT']):
                        continue

                    if description and amount > 0:
                        transactions.append({
                            'date': current_date,
                            'description': description.strip(),
                            'amount': amount,
                            'currency': currency
                        })

                except (ValueError, IndexError) as e:
                    print(f"Error processing line: {line}")
                    print(f"Error details: {str(e)}")
                    continue

        # Create DataFrame
        if transactions:
            df = pd.DataFrame(transactions)
            df = df.sort_values('date')
            df = df.drop_duplicates(subset=['date', 'description', 'amount'])
            return df

        return pd.DataFrame()

    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")