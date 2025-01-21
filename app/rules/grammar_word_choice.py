import re
from app.utils import get_line_number
from app.utils import get_sentence_from_index

def check_grammar_word_choice(content, doc, suggestions):
    # Rule: Correct use of 'assure', 'ensure', 'insure'
    misuse_patterns = {
        r'\bassure\b': "Use 'assure' to mean 'to put someone's mind at ease'.",
        r'\bensure\b': "Use 'ensure' to mean 'to make certain'.",
        r'\binsure\b': "Use 'insure' only when referring to insurance."
    }
    for pattern, guidance in misuse_patterns.items():
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            line_number = get_line_number(content, match.start())
            suggestions.append(f"Line {line_number}: {guidance}")

    # Rule: Use 'ask' instead of 'request' if 'request' is used as a verb
    request_pattern = r'\brequest\b'
    matches = re.finditer(request_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Instead of doc[match.start()], we create a char_span
        start_char = match.start()
        end_char = match.end()
        span = doc.char_span(start_char, end_char)

        # If spaCy can't map these offsets to token boundaries, skip
        if span is None:
            continue

        # Check if any token in this char_span is used as a VERB
        if any(token.pos_ == "VERB" for token in span):
            line_number = get_line_number(content, start_char)
            suggestions.append(
                f"Line {line_number}: Use 'ask' instead of '{match.group()}' as a verb."
            )
    
    # Additional grammar rules can be added here as needed
    pass
