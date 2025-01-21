# app/rules/css_terms.py

import re
from app.utils import get_line_number

def check_css_terms(content, doc, suggestions):
    """
    Checks for proper usage of 'Cascading Style Sheets (CSS)' vs. references to style sheets.

    Guidelines:
    1. Capitalize references to the technique: Cascading Style Sheets (CSS).
    2. Spell out unless the abbreviation CSS is familiar to the audience.
    3. Lowercase references to style sheets created using the technique.
    4. Don't use 'CSS' to refer to a specific cascading style sheet. Use 'the CSS file', 'the cascading style sheet', or 'the style sheet'.
    """

    # Rule 1: Check if "Cascading Style Sheets" is capitalized properly
    # We'll look for references like "Cascading style sheets" or "cascading style sheets"
    # and suggest correct capitalization
    css_technique_pattern = r'\bcascading\s+style\s+sheets\b'
    matches = re.finditer(css_technique_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        correct_form = "Cascading Style Sheets"
        line_number = get_line_number(content, match.start())
        suggestions.append(
            f"Line {line_number}: Capitalize references to the technique as '{correct_form}' "
            f"(e.g., 'Cascading Style Sheets (CSS)')."
        )

    # Rule 2: Check references to 'CSS' in situations where it might be referencing
    # a specific file or style sheet
    # We want to avoid using 'CSS' to refer to a specific file
    # Instead, use 'the CSS file' or 'the style sheet'
    # We'll attempt a context check around 'CSS'
    css_pattern = r'\bCSS\b'
    for match in re.finditer(css_pattern, content):
        line_number = get_line_number(content, match.start())
        # We'll grab a small context to see if it's referencing a file
        context_window = 40
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        snippet = content[start:end]

        # Heuristic: If "CSS" is directly followed or preceded by "file", "sheet", or "style sheet"
        # we suggest clarifying usage
        if re.search(r'(file|sheet)', snippet, flags=re.IGNORECASE):
            suggestions.append(
                f"Line {line_number}: Don't use 'CSS' to refer to a specific style sheet. "
                "Use 'the CSS file', 'the cascading style sheet', or 'the style sheet' instead."
            )

    # Rule 3: Lowercase references to style sheets if you see something like 'Style Sheet' or 'Style Sheets'
    # that appears to be referencing the actual file and not the technique
    style_sheet_pattern = r'\b[Ss]tyle\s+[Ss]heet(s)?\b'
    for match in re.finditer(style_sheet_pattern, content):
        line_number = get_line_number(content, match.start())
        # If "Style Sheet" is capitalized, we want to suggest lowercasing it when referring to a file
        # We'll see if the matched text is actually capitalized
        matched_text = match.group()
        # We only raise a suggestion if the matched text starts with uppercase (except for the first letter 'S')
        # or if it's fully uppercase
        # This is a heuristic—feel free to refine
        if matched_text != matched_text.lower():
            suggestions.append(
                f"Line {line_number}: Lowercase references to style sheets when referring to the file. "
                f"Use 'style sheet' instead of '{matched_text}'."
            )

    # Additional logic could check if "Cascading Style Sheets" has been spelled out once
    # before using "CSS" if the audience is not guaranteed to be familiar with it
    # That can be more advanced (tracking first mention, etc.), depending on your needs.
