"""
Response formatting utilities for cleaning and structuring LLM outputs.
"""
import re
import json


def clean_and_format_response(text: str) -> str:
    """
    Clean and format LLM response to look professional.
    Handles escaped characters, formatting, and structure.
    """
    if not text:
        return ""
    
    # Step 1: Handle various encoding issues
    try:
        # Try bytes decode for double-encoded strings
        if isinstance(text, str) and '\\n' in text:
            text = bytes(text, 'utf-8').decode('unicode_escape')
    except Exception as e:
        print(f"Decode attempt failed: {e}")
        # Continue with manual cleaning
    
    # Step 2: Manual escape sequence replacement
    escape_map = {
        '\\n': '\n',
        '\\r\\n': '\n',
        '\\r': '\n',
        '\\t': '    ',  # Convert tabs to spaces
        '\\"': '"',
        "\\'": "'",
        '\\\\': '\\',
        '**': ''
    }
    
    for escaped, actual in escape_map.items():
        print(actual)
        text = text.replace(escaped, actual)
    
    # Step 3: Remove common artifacts
    text = text.replace('```json', '').replace('```', '')
    text = re.sub(r'<\|.*?\|>', '', text)  # Remove special tokens
    
    # Step 4: Normalize whitespace
    # Replace multiple spaces with single space (except at line start)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Preserve intentional indentation but clean excessive spaces
        stripped = line.strip()
        if stripped:
            # Check if line starts with list marker
            if re.match(r'^[\d\-\*•]+[\.\):]?\s', stripped):
                # It's a list item, preserve structure
                cleaned_lines.append(stripped)
            else:
                # Regular line, clean excessive spaces
                cleaned = re.sub(r'\s{2,}', ' ', stripped)
                cleaned_lines.append(cleaned)
        else:
            # Empty line
            cleaned_lines.append('')
    
    text = '\n'.join(cleaned_lines)
    
    # Step 5: Fix paragraph spacing
    # Remove more than 2 consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 6: Ensure proper spacing after punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    # Step 7: Format lists properly
    text = format_lists(text)
    
    # Step 8: Final cleanup
    text = text.strip()
    
    return text

def format_to_human_readable(text: str) -> str:
    text = clean_rag_response(text)

    # If short, return as-is
    if len(text.split()) < 25:
        return text

    # Convert numbered markdown to plain numbers
    text = re.sub(r"^\s*\d+\.\s*", lambda m: f"{int(m.group().strip('. '))}. ", text, flags=re.MULTILINE)

    # Convert * bullets to hyphens
    text = re.sub(r"^\s*\*\s*", "- ", text, flags=re.MULTILINE)

    return text.strip()


def clean_rag_response(text: str) -> str:
        # -------------------------------
    # 1. Fix escaped newlines
    # -------------------------------
    text = text.replace("\\n", "\n")

    # -------------------------------
    # 2. Remove markdown bold/italics
    # -------------------------------
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # -------------------------------
    # 3. Convert markdown links: 
    # [Title](URL) → Title: URL
    # -------------------------------
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1: \2", text)

    # -------------------------------
    # 4. Convert '+' bullets to '-'
    # -------------------------------
    text = re.sub(r"^\s*\+\s*", "- ", text, flags=re.MULTILINE)

    # -------------------------------
    # 5. Convert '*' bullets to '-'
    # -------------------------------
    text = re.sub(r"^\s*\*\s*", "- ", text, flags=re.MULTILINE)

    # -------------------------------
    # 6. Ensure numbered lists are clean
    # "1." or "1)" → "1. "
    # -------------------------------
    text = re.sub(r"^\s*(\d+)[\.\)]\s*", r"\1. ", text, flags=re.MULTILINE)

    # -------------------------------
    # 7. Clean excess newlines
    # -------------------------------
    text = re.sub(r"\n{3,}", "\n\n", text)

    # -------------------------------
    # 8. Remove quote wrapping
    # -------------------------------
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]

    return text.strip()


def format_lists(text: str) -> str:
    """
    Format bullet points and numbered lists properly.
    """
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if this is a list item
        is_list_item = bool(re.match(r'^[\d\-\*•]+[\.\):]?\s', stripped))
        
        if is_list_item:
            if not in_list and i > 0:
                # Add blank line before list starts
                formatted_lines.append('')
            formatted_lines.append(stripped)
            in_list = True
        else:
            if in_list and stripped:
                # Add blank line after list ends
                formatted_lines.append('')
            formatted_lines.append(stripped)
            in_list = False if stripped else in_list
    
    return '\n '.join(formatted_lines)


def extract_structured_content(text: str) -> dict:
    """
    Extract structured content from response if present.
    Useful for detecting if response contains JSON or special formatting.
    """
    # Try to extract JSON blocks
    json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
    if json_match:
        try:
            json_data = json.loads(json_match.group(0))
            return {"has_json": True, "json_data": json_data, "text": text}
        except:
            pass
    
    return {"has_json": False, "text": text}


def format_sources_citation(text: str, sources: list) -> str:
    """
    Enhance source citations in the response.
    Looks for [Source N] patterns and adds links.
    """
    if not sources:
        return text
    
    # Find all source references
    for source in sources:
        source_num = source.get('source_number', 0)
        url = source.get('url', '')
        
        # Replace [Source N] with formatted version
        pattern = rf'\[Source {source_num}\]'
        replacement = f'[Source {source_num}]({url})' if url != 'Unknown' else f'[Source {source_num}]'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def truncate_response(text: str, max_length: int = 2000, preserve_sentences: bool = True) -> str:
    """
    Truncate response if too long while preserving sentence boundaries.
    """
    if len(text) <= max_length:
        return text
    
    if preserve_sentences:
        # Truncate at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_question = truncated.rfind('?')
        last_exclamation = truncated.rfind('!')
        
        last_sentence_end = max(last_period, last_question, last_exclamation)
        
        if last_sentence_end > max_length * 0.8:  # Only if we're not losing too much
            return truncated[:last_sentence_end + 1] + "\n\n[Response truncated for length]"
    
    return text[:max_length] + "...\n\n[Response truncated for length]"


def add_metadata_footer(text: str, metadata: dict) -> str:
    """
    Add helpful metadata footer to response.
    """
    footer_parts = []
    
    if metadata.get('retrieved_chunks'):
        footer_parts.append(f"📚 Retrieved {metadata['retrieved_chunks']} relevant chunks")
    
    if metadata.get('model'):
        footer_parts.append(f"🤖 Generated by {metadata['model']}")
    
    if footer_parts:
        footer = "\n\n---\n" + " | ".join(footer_parts)
        return text + footer
    
    return text