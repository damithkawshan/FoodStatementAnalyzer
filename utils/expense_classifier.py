import pandas as pd

def classify_food_expenses(df):
    """
    Classify transactions as food-related expenses.
    
    Args:
        df: pandas DataFrame with transactions
    
    Returns:
        pandas DataFrame with only food-related expenses
    """
    # Common food-related keywords
    food_keywords = [
        # Restaurants and Fast Food
        'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'mcdonald',
        'subway', 'wendy', 'taco', 'kfc', 'chipotle', 'starbucks',
        'dunkin', 'donut', 'deli', 'grill', 'kitchen', 'bistro',
        
        # Grocery Stores
        'grocery', 'market', 'food', 'trader joe', 'whole foods',
        'safeway', 'kroger', 'albertsons', 'aldi', 'costco', 'walmart',
        'target', 'supermarket',
        
        # Delivery Services
        'uber eats', 'doordash', 'grubhub', 'postmates', 'seamless',
        'deliveroo', 'instacart',
        
        # Generic Food Terms
        'bakery', 'butcher', 'seafood', 'sushi', 'bbq', 'steakhouse',
        'pizzeria', 'dining', 'eatery'
    ]
    
    # Create regex pattern
    pattern = '|'.join(food_keywords)
    
    # Filter transactions
    food_expenses = df[df['description'].str.lower().str.contains(pattern, na=False)]
    
    # Attempt to categorize expenses
    def categorize_expense(description):
        desc_lower = description.lower()
        
        if any(keyword in desc_lower for keyword in ['grocery', 'market', 'supermarket', 'trader', 'whole foods']):
            return 'Groceries'
        elif any(keyword in desc_lower for keyword in ['doordash', 'uber eats', 'grubhub', 'postmates']):
            return 'Food Delivery'
        elif any(keyword in desc_lower for keyword in ['coffee', 'starbucks', 'dunkin']):
            return 'Coffee Shops'
        else:
            return 'Restaurants/Other'
    
    food_expenses['category'] = food_expenses['description'].apply(categorize_expense)
    
    return food_expenses
