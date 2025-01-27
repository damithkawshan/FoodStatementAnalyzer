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

def extract_transactions_from_file(file):
    """
    Extract transactions from PDF bank statement or image with improved pattern matching.

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

        # Split text into lines and process each line
        transactions = []
        lines = text.split('\n')

        date_pattern = r'\d{2}/\d{2}/\d{4}'  # DD/MM/YYYY format
        amount_pattern = r'\d+\.\d{2}'  # Matches decimal amounts

        current_date = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for date
            dates = re.findall(date_pattern, line)
            if dates:
                try:
                    current_date = pd.to_datetime(dates[0], format='%d/%m/%Y')
                except:
                    continue

            # Look for amounts
            amounts = re.findall(amount_pattern, line)

            if current_date and amounts:
                try:
                    # Determine if it's withdrawal or deposit
                    amount_str = amounts[-1]
                    amount = float(amount_str)

                    # Extract description (remove date and amount)
                    description = line
                    description = re.sub(date_pattern, '', description)
                    description = re.sub(amount_pattern, '', description)
                    description = ' '.join(description.split())

                    # Skip header rows
                    if any(header in description.upper() for header in ['BALANCE', 'DATE', 'DESCRIPTION']):
                        continue

                    if description and amount > 0:
                        transactions.append({
                            'date': current_date,
                            'description': description.strip(),
                            'amount': amount
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