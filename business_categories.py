# business_categories.py

# Dictionary to store categories and their business types
categories = {
    "Financieel": ["Bank", "Verzekering", "Accountancy"],
    "Technologie": ["Software", "Hardware", "IT Consultancy"],
    "Gezondheidszorg": ["Ziekenhuis", "Apotheek", "Huisartsenpraktijk"],
    "Retail": ["Supermarkt", "Kledingwinkel", "Electronicawinkel"],
    "Onderwijs": ["Basisschool", "Middelbare school", "Universiteit"]
}

def get_categories():
    """Return all available categories."""
    return list(categories.keys())

def get_business_types(category):
    """Return all business types for a given category."""
    return categories.get(category, [])

def add_business_type(category, business_type):
    """Add a new business type to a category."""
    if category not in categories:
        categories[category] = []
    if business_type not in categories[category]:
        categories[category].append(business_type)
    else:
        raise ValueError(f"Business type '{business_type}' already exists in category '{category}'")