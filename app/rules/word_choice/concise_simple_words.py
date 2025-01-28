import re
from app.utils import get_line_number

def check_concise_simple_words(content, doc, suggestions):
    """
    MSTP Guidance:
    1. Replace overly formal/verbose phrases with concise, simple alternatives.
    2. Detect unnecessary modifiers (e.g., 'very', 'quite', 'easily').
    3. Flag weak or vague verbs (e.g., 'be', 'have', 'make', 'do').
    4. Highlight ambiguous words that can confuse context (e.g., 'file', 'post', 'mark').
    """

    # 1. Replace overly formal or verbose phrases
    formal_phrases = {
        r"\butilize\b": "use",
        r"\bmake use of\b": "use",
        r"\bextract\b": "remove",
        r"\beliminate\b": "remove",
        r"\bin order to\b": "to",
        r"\bas a means to\b": "to",
        r"\bestablish connectivity\b": "connect",
        r"\blet know\b": "tell",
        r"\binform\b": "tell",
        r"\bin addition\b": "also",
        r"\bquite\b": "",  # Suggest removal
        r"\bvery\b": "",   # Suggest removal
    }

    for pattern, replacement in formal_phrases.items():
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            line_number = get_line_number(content, match.start())
            found_text = match.group()
            if replacement:
                suggestions.append(
                    f"Line {line_number}: Replace '{found_text}' with '{replacement}' for simplicity."
                )
            else:
                suggestions.append(
                    f"Line {line_number}: Consider removing '{found_text}' as it may not add value."
                )

    # 2. Detect unnecessary adverbs
    unnecessary_adverbs = r"\b(very|quite|easily|effectively|quickly)\b"
    matches = re.finditer(unnecessary_adverbs, content, flags=re.IGNORECASE)
    for match in matches:
        line_number = get_line_number(content, match.start())
        found_text = match.group()
        suggestions.append(
            f"Line {line_number}: Consider removing the adverb '{found_text}' unless it is essential."
        )

    # 3. Flag weak or vague verbs
    weak_verbs = r"\b(be|have|make|do)\b"
    matches = re.finditer(weak_verbs, content, flags=re.IGNORECASE)
    for match in matches:
        line_number = get_line_number(content, match.start())
        found_text = match.group()
        suggestions.append(
            f"Line {line_number}: Avoid the weak verb '{found_text}'. Replace it with a more specific action verb."
        )

    # 4. Highlight ambiguous words (e.g., 'file', 'mark', 'post', 'record', 'report')
    ambiguous_words = r"\b(file|post|mark|screen|record|report)\b"
    matches = re.finditer(ambiguous_words, content, flags=re.IGNORECASE)
    for match in matches:
        line_number = get_line_number(content, match.start())
        found_text = match.group()
        suggestions.append(
            f"Line {line_number}: The word '{found_text}' can be ambiguous. Ensure the context clarifies its meaning."
        )
