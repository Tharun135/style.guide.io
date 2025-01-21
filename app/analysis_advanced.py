import re
import spacy
import textstat

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def get_readability_scores(text):
    """
    Calculate various readability metrics from 'textstat'.

    :param text: (str) The paragraph or content block to analyze.
    :return: (dict) a dictionary of readability metrics. e.g.:
             {
               'flesch_reading_ease': 53.21,
               'gunning_fog': 11.2,
               'smog_index': 8.5,
               'automated_readability_index': 10.0
             }
    """
    scores = {}
    # Example metrics, expand or reduce as needed:
    scores["flesch_reading_ease"] = textstat.flesch_reading_ease(text)
    scores["gunning_fog"] = textstat.gunning_fog(text)
    scores["smog_index"] = textstat.smog_index(text)
    scores["automated_readability_index"] = textstat.automated_readability_index(text)
    return scores

def detect_passive_voice(paragraph):
    """
    Use spaCy to detect potential passive voice in a paragraph.

    :param paragraph: (str) The text to analyze for passive voice.
    :return: (list) A list of sentences that appear to be in passive voice.
                   This approach is naive and may produce false positives/negatives.
    """
    doc = nlp(paragraph)
    passive_sentences = []
    for sent in doc.sents:
        # 'auxpass' is a typical sign of passive voice in English grammar.
        if any(token.dep_ == "auxpass" for token in sent):
            passive_sentences.append(sent.text.strip())
    return passive_sentences

def identify_long_sentences(paragraph, max_length=25):
    """
    Identify sentences that exceed a specified token length, suggesting they might be too
    complex or wordy.

    :param paragraph: (str) The paragraph text to analyze.
    :param max_length: (int) The threshold above which a sentence is flagged as 'long/complex'.
    :return: (list) A list of sentences that exceed 'max_length' tokens.
    """
    doc = nlp(paragraph)
    long_sents = []
    for sent in doc.sents:
        if len(sent) > max_length:
            long_sents.append(sent.text.strip())
    return long_sents

def compute_quality_score(readability_scores, paragraph_feedback):
    """
    Compute a simplistic 'quality score' for a paragraph, based on:
      - Readability (Flesch Reading Ease)
      - Number of feedback/warnings

    :param readability_scores: (dict) the dictionary from get_readability_scores()
    :param paragraph_feedback: (list) array of string feedback items
    :return: (float) A 0-100 numeric rating, naive approach.
    """
    # We'll base it primarily on Flesch Reading Ease, with a penalty for each feedback item.
    flesch = readability_scores.get("flesch_reading_ease", 60.0)
    # clamp flesch between 0 and 100
    if flesch > 100:
        flesch = 100
    elif flesch < 0:
        flesch = 0

    # 5 points penalty per feedback
    penalty = len(paragraph_feedback) * 5

    base_score = flesch - penalty
    if base_score < 0:
        base_score = 0

    return base_score

def color_for_quality(q_score):
    """
    Return a color code (red, orange, green) for the gauge circle,
    based on the paragraph or overall quality score.

    :param q_score: (float) a 0-100 rating
    :return: (str) 'red', 'orange', or 'green'
    """
    if q_score < 30:
        return "red"
    elif q_score < 70:
        return "orange"
    else:
        return "green"

def remove_line_prefix(msg):
    """
    If MSTP or grammar rule suggestions contain something like "Line 10: ...",
    remove that prefix. We only want the raw suggestion text.

    :param msg: (str) the suggestion text.
    :return: (str) cleaned suggestion without "Line X:" prefix.
    """
    lower_msg = msg.lower()
    if lower_msg.startswith("line "):
        colon_index = msg.find(":")
        if colon_index != -1:
            return msg[colon_index + 1 :].strip()
    return msg

def advanced_paragraph_analysis(paragraph):
    """
    Perform advanced analysis on a single paragraph:
      1. Detect passive voice
      2. Identify long sentences
      3. Compute readability
      4. Combine these into a list of textual feedback
      5. Compute a quality score

    :param paragraph: (str) The paragraph text
    :return: (dict) containing 'feedback', 'readabilityScores', 'qualityScore'
    """
    # Passive voice detection
    passive_sents = detect_passive_voice(paragraph)
    passive_feedback = []
    for ps in passive_sents:
        passive_feedback.append(f"Passive sentence: '{ps}' - consider rewriting.")

    # Identify long/complex sentences
    long_sents = identify_long_sentences(paragraph, max_length=25)
    complexity_feedback = []
    for ls in long_sents:
        complexity_feedback.append(f"Long/complex sentence: '{ls}' - consider splitting or simplifying.")

    # Readability scores
    r_scores = get_readability_scores(paragraph)

    # Summarize local feedback
    combined_feedback = []
    combined_feedback.extend(passive_feedback)
    combined_feedback.extend(complexity_feedback)

    # Quality score
    q_score = compute_quality_score(r_scores, combined_feedback)

    return {
        "feedback": combined_feedback,
        "readabilityScores": r_scores,
        "qualityScore": q_score
    }

def analyze_paragraphs_with_advanced_features(paragraphs, mstp_suggestions_func):
    """
    For each paragraph:
      - run MSTP suggestions
      - run advanced analysis (passive voice, readability, complexity)
      - combine feedback, removing 'Line X:' prefix
      - compute paragraph-level quality
    Then produce an aggregated overall report (avgQualityScore, color, wordCount, etc.)

    :param paragraphs: (list) of paragraph texts
    :param mstp_suggestions_func: (function) that takes paragraph text -> array of suggestions
    :return: (paragraph_data, aggregated_report)
       where paragraph_data = [
         {
           "paragraphNumber": i,
           "text": "...",
           "feedback": [...],
           "readabilityScores": {...},
           "qualityScore": float
         },
         ...
       ]
       aggregated_report = {
         "avgQualityScore": float,
         "color": "red"/"orange"/"green",
         "paragraphCount": int,
         "totalWords": int,
         "message": "..."
       }
    """
    paragraph_data = []
    total_score = 0.0
    total_words = 0
    paragraph_count = len(paragraphs)

    for i, para_text in enumerate(paragraphs, start=1):
        # 1. MSTP suggestions
        mstp_suggestions = mstp_suggestions_func(para_text)
        # Remove "Line X:" prefix from each suggestion
        cleaned_mstp = [remove_line_prefix(sugg) for sugg in mstp_suggestions]

        # 2. advanced analysis
        adv = advanced_paragraph_analysis(para_text)
        adv_feedback = adv["feedback"]
        readability = adv["readabilityScores"]
        q_score = adv["qualityScore"]

        # merge feedback arrays
        final_feedback = cleaned_mstp + adv_feedback

        # accumulate word count
        words = para_text.split()
        total_words += len(words)

        # accumulate quality
        total_score += q_score

        paragraph_data.append({
            "paragraphNumber": i,
            "text": para_text.strip(),
            "feedback": final_feedback,
            "readabilityScores": readability,
            "qualityScore": q_score
        })

    # Overall / aggregated
    if paragraph_count > 0:
        avg_q = total_score / paragraph_count
    else:
        avg_q = 0

    color = color_for_quality(avg_q)

    # Optionally a message
    if avg_q >= 70:
        msg = "Great job! Your content is fairly strong."
    elif avg_q >= 30:
        msg = "Your content is okay, but could use improvements."
    else:
        msg = "Your content needs significant revision."

    aggregated_report = {
        "avgQualityScore": round(avg_q, 1),
        "color": color,
        "paragraphCount": paragraph_count,
        "totalWords": total_words,
        "message": msg
    }

    return paragraph_data, aggregated_report
