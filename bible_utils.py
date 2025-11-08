import requests
import re
from config import API_BASE_URL, BIBLE_BOOK_IDS, MAX_CHARS_PER_LINE, BOOK_ABBREVIATIONS

# --- BIBLE API AND PARSING FUNCTIONS ---

def to_title_case(s):
    """Helper function to convert a string to Title Case."""
    return ' '.join(
        word.capitalize() if not word.isdigit() else word
        for word in s.split(' ')
    )

def parse_reference(reference):
    """Parses a scripture reference string into a structured object."""
    normalized_ref = reference.lower().replace('.', '')
    normalized_ref = reference.lower().strip().replace('.', '')

    # Regex to capture Book (with optional number), Chapter, Start Verse, and optional End Verse
    match = re.match(r"^(\d?\s*[a-z]+)\s*(\d+):(\d+)(?:-(\d+))?$", normalized_ref)

    if not match:
        raise ValueError(f"Could not parse reference: '{reference}'")

    book_part, chapter_str, start_verse_str, end_verse_str = match.groups()

    book = to_title_case(book_part.strip())
    # Look up the abbreviation. If not found, assume it's already the full name.
    book_key = book_part.strip()
    canonical_book_name = BOOK_ABBREVIATIONS.get(book_key)
    
    book = to_title_case(canonical_book_name or book_key)
    chapter = int(chapter_str)
    start_verse = int(start_verse_str)
    end_verse = int(end_verse_str) if end_verse_str else start_verse

    return { 'book': book, 'chapter': chapter, 'start_verse': start_verse, 'end_verse': end_verse }

def format_text_for_obs(text):
    """
    Inserts manual line breaks to ensure text wraps correctly for the narrow OBS canvas.
    This replicates the manual <CTRL><ENTER> input you were using.
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the next word exceeds the max length
        if len(current_line) + len(word) + 1 > MAX_CHARS_PER_LINE and current_line:
            lines.append(current_line)
            current_line = word
        else:
            # Append word to current line
            if current_line:
                current_line += " " + word
            else:
                current_line = word

    if current_line:
        lines.append(current_line)

    # OBS Text (FreeType 2) uses \n for line breaks
    return "\n".join(lines)


def get_verses_from_api(reference):
    """Fetches verses from the API and formats them for OBS."""
    parsed_ref = parse_reference(reference)
    book_id = BIBLE_BOOK_IDS.get(parsed_ref['book'])

    if not book_id:
        raise ValueError(f"Unknown book: '{parsed_ref['book']}' in BIBLE_BOOK_IDS.")

    api_url = f"{API_BASE_URL}/{book_id}/{parsed_ref['chapter']}.json"

    print(f"Fetching data from: {api_url}")

    response = requests.get(api_url)
    response.raise_for_status()
    chapter_data = response.json()

    all_verses = chapter_data.get('chapter', {}).get('content', [])

    verses_to_process = []

    for item in all_verses:
        if item.get('type') == 'verse':
            verse_number = item.get('number')

            if parsed_ref['start_verse'] <= verse_number <= parsed_ref['end_verse']:
                verse_text_parts = []
                for part in item.get('content', []):
                    if isinstance(part, str):
                        verse_text_parts.append(part)
                    elif isinstance(part, dict) and part.get('text'):
                        verse_text_parts.append(part['text'])

                raw_text = " ".join(verse_text_parts).strip()

                # Combine verse reference and text
                full_verse_text = f"{parsed_ref['book']} {parsed_ref['chapter']}:{verse_number} (BSB)\n"

                # Format the text body with line breaks
                formatted_body = format_text_for_obs(raw_text)

                verses_to_process.append({
                    'reference': f"{parsed_ref['book']} {parsed_ref['chapter']}:{verse_number}",
                    'obs_text': full_verse_text + formatted_body,
                    'scene_name': f"Scripture-{book_id}-{parsed_ref['chapter']}:{verse_number}"
                })

    return verses_to_process