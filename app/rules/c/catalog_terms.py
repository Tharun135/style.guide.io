import re
from app.utils import get_line_number

def check_catalog_terms(content, doc, suggestions):
    """
    MSTP Rule: Use 'catalog' instead of 'catalogue'.
    Detects 'catalogue' and suggests using 'catalog' instead.
    """
    pattern = r'\bcatalogue\b'
    matches = re.finditer(pattern, content, flags=re.IGNORECASE)
    for match in matches:
        line_number = get_line_number(content, match.start())
        found_term = match.group()
        suggestions.append(
            f"Line {line_number}: Use 'catalog' instead of '{found_term}'."
        )
