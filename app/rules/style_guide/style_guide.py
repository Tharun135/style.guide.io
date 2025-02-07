import re
from app.utils import get_line_number, get_sentence_from_index

def check_style_guide(content, doc, suggestions):
    # Rule 1: Avoid weak expressions like 'There is', 'It is'
    weak_expressions = [r'\bThere is\b', r'\bThere are\b', r'\bIt is\b']
    for pattern in weak_expressions:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            line_number = get_line_number(content, match.start())
            suggestions.append(f"Line {line_number}: Avoid weak expressions like '{match.group()}'. Consider rewording for clarity.")

    # Rule 2: Ensure UI elements are in double quotes
    ui_pattern = r'\bClick on ([A-Za-z0-9]+)\b'
    matches = re.finditer(ui_pattern, content)
    for match in matches:
        line_number = get_line_number(content, match.start())
        suggestions.append(f"Line {line_number}: UI elements should be enclosed in double quotes, e.g., \"{match.group(1)}\".")

    # Rule 3: Prevent use of 'please' unless necessary
    please_pattern = r'\bplease\b'
    matches = re.finditer(please_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        line_number = get_line_number(content, match.start())
        suggestions.append(f"Line {line_number}: Avoid using 'please' unless it refers to an inconvenience or unplanned event.")

    # Rule 4: Enforce active voice
    passive_voice_patterns = [
        r'\b(is|was|were|been) [a-z]+ed\b',  # Common passive voice structures
        r'\bby the user\b'
    ]
    for pattern in passive_voice_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            line_number = get_line_number(content, match.start())
            suggestions.append(f"Line {line_number}: Convert passive voice to active voice where possible.")

    # Rule 5: Check for word/phrase violations
    avoid_words = {
        "therefore": "Consider simplifying or removing 'therefore'.",
        "furthermore": "Consider simplifying or removing 'furthermore'.",
        "master/slave": "Avoid using 'master/slave'. Consider alternative terms like 'primary/secondary'."
    }
    for word, message in avoid_words.items():
        pattern = rf'\b{word}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            line_number = get_line_number(content, match.start())
            suggestions.append(f"Line {line_number}: {message}")

    pass
