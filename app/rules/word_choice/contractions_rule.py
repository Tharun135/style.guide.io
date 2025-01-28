import re
from app.utils import get_line_number

def check_contractions(content, doc, suggestions):
    """
    MSTP Guidance: 
    1. Use common contractions (it's, you're, that's, don't) to create a friendly tone.
    2. Don't mix contractions and spelled-out equivalents in the same UI text (e.g., can’t and cannot).
    3. Never form a contraction from a noun and a verb (e.g., "Microsoft’s developing ...").
    4. Avoid ambiguous/awkward contractions (e.g. "there’d", "it’ll", "they’d").

    We'll do basic checks with regex for some rules. 
    Advanced logic might require spaCy or further context.
    """

    # 1. Encourage common contractions. 
    #    This is an optional message, not exactly a "warning," but let's handle it as an info suggestion if we detect 
    #    "it is", "you are", "that is", "do not" in a direct usage. 
    #    We can do a simple approach: find these spelled out forms and gently encourage the contraction.

    # We define pairs. We won't forcibly transform them, but we can suggest. 
    # We'll be conservative.
    spelled_out_contractions = {
        r"\bit is\b": "it’s",
        r"\byou are\b": "you’re",
        r"\bthat is\b": "that’s",
        r"\bdo not\b": "don’t",
    }

    for pattern, recommended in spelled_out_contractions.items():
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            line_number = get_line_number(content, match.start())
            found_str = match.group()
            suggestions.append(
                f"Line {line_number}: Consider using the common contraction '{recommended}' instead of '{found_str}'."
            )

    # 2. Don’t mix spelled-out forms (e.g. cannot) with contractions (e.g. can’t) in the same paragraph (UI text).
    #    We'll detect if a paragraph has both "cannot" and "can't" or e.g. "do not" and "don't".
    #    We'll do a naive approach that scans each paragraph. 
    paragraphs = content.split("\n\n")  # simplistic paragraph splitting

    # Pairs of spelled-out vs. contraction
    mixed_pairs = [
        ("cannot", "can't"),
        ("do not", "don't"),
        ("will not", "won't"),
        ("should not", "shouldn't"),
        # add more if needed
    ]

    start_idx = 0  # track overall content index to get line number
    for para in paragraphs:
        # For each pair, if we find both forms in the same paragraph, we flag it
        para_lower = para.lower()
        for spelled, contr in mixed_pairs:
            if spelled in para_lower and contr in para_lower:
                # find an approximate line number from start_idx
                line_no = get_line_number(content, start_idx + content[start_idx:].find(para))
                suggestions.append(
                    f"Line {line_no}: Don't mix '{spelled}' and '{contr}' in the same text. Choose one for consistency."
                )

        # move the start_idx forward
        start_idx += len(para) + 2  # +2 for the double newline we used

    # 3. Never form a contraction from a noun + verb (like "Microsoft’s developing ...").
    #    We'll detect pattern like "[ProperNoun]'s <verb>" with a naive approach. 
    #    We'll do a basic regex that might catch <Word>'s <word>ing, <Word>'s <word>ed, etc.
    #    This can produce false positives, so tune carefully.

    # Example pattern: ([A-Z][a-zA-Z]+)'s\s+(developing|running|launching|open\w+)
    # Instead, we'll do a generic check for `'s + (VB*)` using doc if you'd prefer spaCy, or we do a naive approach with regex.
    # We'll do a naive approach with spacy to see if preceding token is a proper noun and next token is a verb.
    # if doc is large, we might do partial, but let's do a doc-based approach for better accuracy.

    # We'll do a token-based approach:
    #   for each token in doc:
    #       if token.text.endswith("'s") and token.pos_ in [PROPN, NOUN]
    #         next token => if next token.pos_ == VERB => flagged
    # Because "Microsoft’s" => token might be separate "Microsoft’s" as one token. 
    # We'll check if there's a next token and see if it's a verb.

    for i, token in enumerate(doc):
        # check if token ends with "'s"
        # also check if the token is a PROPN or NOUN
        if token.text.lower().endswith("'s") and token.pos_ in ["PROPN", "NOUN"]:
            # check next token if it is a verb
            if i + 1 < len(doc):
                next_token = doc[i + 1]
                if next_token.pos_ in ["VERB", "AUX"]:
                    # we suspect a noun + verb contraction
                    line_number = get_line_number(content, token.idx)
                    suggestions.append(
                        f"Line {line_number}: Avoid forming contractions from a noun and a verb (e.g., \"{token.text} {next_token.text}\"). "
                        "Use a different phrasing like 'Microsoft is developing...' instead."
                    )

    # 4. Avoid ambiguous or awkward contractions (e.g. there’d, it’ll, they’d).
    #    We'll just do a regex search for these forms. 
    awkward_pattern = r"\b(there’d|it’ll|they’d)\b"
    matches = re.finditer(awkward_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        line_no = get_line_number(content, match.start())
        found_str = match.group()
        suggestions.append(
            f"Line {line_no}: Avoid ambiguous or awkward contraction '{found_str}'. Rephrase for clarity."
        )
