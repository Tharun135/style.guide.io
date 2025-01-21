from flask import Blueprint, request, jsonify, render_template
import os
import subprocess
import markdown
import PyPDF2
from docx import Document

# Import your advanced analysis & MSTP logic
from .analysis_advanced import analyze_paragraphs_with_advanced_features
from .mstp_rules import analyze_content  # Your existing MSTP grammar/spelling/consistency rules

main = Blueprint('main', __name__)

############################
# PARSING HELPERS
############################

def improved_pdf_paragraph_split(raw_text):
    """
    Attempt to produce multiple paragraphs from PDF text instead of everything in a single block.
    We'll split on blank lines or double newlines to chunk the text.
    Adjust logic as needed for better PDF segmentation.
    """
    lines = raw_text.split("\n")
    paragraphs = []
    buffer = []
    for line in lines:
        line_stripped = line.strip()
        # If line is blank, end a paragraph
        if not line_stripped:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
        else:
            buffer.append(line_stripped)
    # flush remainder
    if buffer:
        paragraphs.append(" ".join(buffer))
    # combine them with double newline so we can do a second pass if desired
    joined_paras = "\n\n".join(paragraphs)
    return joined_paras

def split_into_paragraphs(text):
    """
    Generic approach: split on double newlines to get paragraph chunks.
    You can refine if needed for .docx or PDF logic.
    """
    text = text.strip()
    if not text:
        return []
    return text.split("\n\n")

def parse_docx(file_stream):
    """
    Use python-docx to extract paragraphs from a .docx file.
    Return a single big string joined by double newlines for consistent paragraph splitting.
    """
    doc = Document(file_stream)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n\n".join(paragraphs)

def parse_doc(file_stream):
    """
    For older .doc, we rely on 'antiword' (system utility).
    Must create a temp file, run antiword, get text, remove temp file.
    """
    temp_path = "temp_upload_doc.doc"
    file_stream.save(temp_path)
    try:
        cmd = ["antiword", temp_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error reading .doc file: {result.stderr}"
    except FileNotFoundError:
        return "Error: 'antiword' not in PATH or not installed."
    except Exception as e:
        return f"Error reading .doc file: {str(e)}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def parse_pdf(file_stream):
    """
    Extract text from PDF using PyPDF2, then do an improved approach for paragraph chunking.
    """
    try:
        reader = PyPDF2.PdfReader(file_stream)
        all_text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            all_text.append(page_text)
        raw_text = "\n".join(all_text)

        # Convert it into paragraphs
        improved_text = improved_pdf_paragraph_split(raw_text)
        return improved_text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def parse_md(content_bytes):
    """
    Just read raw text. We'll let the same paragraph-splitting logic handle them.
    If you want to convert to HTML for display, do so on the front-end or separate logic.
    """
    return content_bytes.decode("utf-8", errors="replace")

def parse_adoc(content_bytes):
    """
    For .adoc, read raw text. We'll split paragraphs next.
    """
    return content_bytes.decode("utf-8", errors="replace")

def parse_txt(content_bytes):
    return content_bytes.decode("utf-8", errors="replace")

############################
# FLASK ROUTES
############################

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """
    1) Accept a file from the user
    2) Distinguish by extension, parse raw text
    3) Convert to paragraphs
    4) Analyze paragraphs with MSTP + advanced features
    5) Return JSON with paragraphs + aggregated report
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename.lower()
    extension = os.path.splitext(filename)[1]

    try:
        raw_text = ""
        if extension == '.docx':
            raw_text = parse_docx(file)
        elif extension == '.doc':
            raw_text = parse_doc(file)
        elif extension == '.pdf':
            raw_text = parse_pdf(file)
        elif extension == '.md':
            raw_text = parse_md(file.read())
        elif extension == '.adoc':
            raw_text = parse_adoc(file.read())
        elif extension in ['.txt', '']:
            raw_text = parse_txt(file.read())
        else:
            # fallback
            content_bytes = file.read()
            raw_text = content_bytes.decode("utf-8", errors="replace")

        # If there's an error message from the parse function
        if raw_text.startswith("Error"):
            return jsonify({"error": raw_text}), 400

        # Now split raw_text into paragraphs
        paragraphs = split_into_paragraphs(raw_text)
        if not paragraphs:
            return jsonify({"paragraphs": [], "report": {}})

        # Analyze paragraphs => returns (paragraph_data, aggregated_report)
        from .analysis_advanced import analyze_paragraphs_with_advanced_features
        paragraph_data, aggregated_report = analyze_paragraphs_with_advanced_features(
            paragraphs,
            mstp_suggestions_func=analyze_content  # your existing MSTP function
        )

        # Return the result
        return jsonify({
            "paragraphs": paragraph_data,
            "report": aggregated_report
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

############################
# OPTIONAL FEEDBACK ENDPOINTS
############################
feedback_list = []

@main.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    feedback = data.get('feedback')
    if not feedback:
        return jsonify({"error": "No feedback provided"}), 400

    feedback_list.append(feedback)
    return jsonify({"message": "Feedback submitted successfully", "feedback_list": feedback_list})

@main.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    return jsonify({"feedback_list": feedback_list})
