# business_categories.py

categories = {
    "Financial": ["Bank", "Insurance", "Accounting"],
    "Technology": ["Software", "Hardware", "IT Consultancy"],
    "Healthcare": ["Hospital", "Pharmacy", "General Practice"],
    "Retail": ["Supermarket", "Clothing Store", "Electronics Store"],
    "Education": ["Primary School", "High School", "University"]
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