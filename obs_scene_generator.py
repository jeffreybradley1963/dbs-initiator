import requests
import json
import re
import os
import argparse
from obsws_python import ReqClient

# --- CONFIGURATION & BIBLE DATA ---

# Your API base URL (Free Bible API used in the Apps Script logic)
API_BASE_URL = "https://bible.helloao.org/api/BSB"

# Max characters per line for your 1080x1920 vertical format
# This should be adjusted based on your chosen font size (e.g., 40-55 characters)
MAX_CHARS_PER_LINE = 50 

# ID of the scene you have already created in OBS that will be duplicated.
# This scene MUST contain a Text (FreeType 2) source named 'SCROLLING_TEXT_SOURCE_NAME'.
TEMPLATE_SCENE_NAME = "Scripture-Template" 
TEMPLATE_SCENE_COLLECTION_NAME = "Daily-Template" # The scene collection containing your template scene
SCROLLING_TEXT_SOURCE_NAME = "sTextScrolling" # Use the name you gave the scrolling text source

# Your BIBLE_BOOK_IDS map (taken from your Apps Script)
BIBLE_BOOK_IDS = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU", 
    "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA", "2 Samuel": "2SA", 
    "1 Kings": "1KI", "2 Kings": "2KI", "1 Chronicles": "1CH", "2 Chronicles": "2CH", "Ezra": "EZR", 
    "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA", "Proverbs": "PRO", 
    "Ecclesiastes": "ECC", "Song of Songs": "SNG", "Isaiah": "ISA", "Jeremiah": "JER", 
    "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN", "Hosea": "HOS", "Joel": "JOL", 
    "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON", "Micah": "MIC", "Nahum": "NAM", 
    "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG", "Zechariah": "ZEC", "Malachi": "MAL", 
    "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT", 
    "Romans": "ROM", "1 Corinthians": "1CO", "2 Corinthians": "2CO", "Galatians": "GAL", 
    "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL", "1 Thessalonians": "1TH", 
    "2 Thessalonians": "2TH", "1 Timothy": "1TI", "2 Timothy": "2TI", "Titus": "TIT", 
    "Philemon": "PHM", "Hebrews": "HEB", "James": "JAS", "1 Peter": "1PE", "2 Peter": "2PE", 
    "1 John": "1JN", "2 John": "2JN", "3 John": "3JN", "Jude": "JUD", "Revelation": "REV"
}

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
    
    # Regex to capture Book (with optional number), Chapter, Start Verse, and optional End Verse
    match = re.match(r"^(\d?\s*[a-z]+)\s*(\d+):(\d+)(?:-(\d+))?$", normalized_ref)

    if not match:
        raise ValueError(f"Could not parse reference: '{reference}'")

    book_part, chapter_str, start_verse_str, end_verse_str = match.groups()
    
    book = to_title_case(book_part.strip())
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

# Example usage:
# ws = obs_ws("localhost", 4444, "your_password") # Replace with your OBS WebSocket details
# duplicate_scene(ws, "Original Scene Name", "Duplicated Scene Name")

def automate_scene_generation(verses, host, port, password):
    """Connects to OBS and automates scene creation and modification."""
    print("Connecting to OBS WebSocket...")
    try:
        # Initialize the client
        # The ReqClient constructor handles the connection.
        client = ReqClient(host=host, port=port, password=password, timeout=5)

    except Exception as e:
        print(f"ERROR: Could not connect to OBS. Ensure OBS is running, the WebSocket Server is enabled (under Tools), and the connection details are correct. Details: {e}")
        return

    print("Successfully connected to OBS.")
    try:
        # Get all scenes to check for existing scenes
        scenes_response = client.get_scene_list()
        all_scenes = scenes_response.scenes

        # Get settings of the template scrolling text source
        template_source_settings_response = client.get_input_settings(SCROLLING_TEXT_SOURCE_NAME)
        template_source_settings = template_source_settings_response.input_settings
        template_source_kind = template_source_settings_response.input_kind

        # Get all items from the template scene to duplicate them
        template_scene_items_response = client.get_scene_item_list(TEMPLATE_SCENE_NAME)
        template_scene_items = template_scene_items_response.scene_items

        print(f"Attempting to create scenes and inject text based on '{TEMPLATE_SCENE_NAME}'...")

        for verse in verses:
            new_scene_name = verse['scene_name']
            # Create a unique source name for each verse's text source
            unique_source_name = f"{SCROLLING_TEXT_SOURCE_NAME}_{verse['reference'].replace(' ', '_').replace(':', '-')}"

            # Check if scene already exists
            scene_exists = False
            for scene in all_scenes:
                if scene['sceneName'] == new_scene_name:
                    scene_exists = True
                    break

            if scene_exists:
                print(f"Scene '{new_scene_name}' already exists. Skipping creation and updating text.")
                # Update the text content of the unique source associated with this existing scene
                client.set_input_settings(
                    name=unique_source_name,
                    settings={'text': verse['obs_text']},
                    overlay=True
                )
                print(f"Updated text in existing scene: {new_scene_name}")
                continue
            
            # 1. Create a new, empty scene.
            client.create_scene(new_scene_name)
            print(f"Created new scene: {new_scene_name}")
            
            # 2. Duplicate all items from the template scene, handling the text source specially.
            for item in template_scene_items:
                if item['sourceName'] == SCROLLING_TEXT_SOURCE_NAME:
                    # This is our special text source. Create a new unique one and apply its transform.
                    print(f"Handling special source: {SCROLLING_TEXT_SOURCE_NAME}")

                    # a. Get the transform of the template text item.
                    transform_response = client.get_scene_item_transform(TEMPLATE_SCENE_NAME, item['sceneItemId'])
                    template_transform = transform_response.scene_item_transform

                    # Ensure boundsWidth and boundsHeight are at least 1.0 to prevent OBS errors
                    if template_transform['boundsWidth'] < 1.0:
                        template_transform['boundsWidth'] = 1.0
                    if template_transform['boundsHeight'] < 1.0:
                        template_transform['boundsHeight'] = 1.0

                    # b. Create the new unique input (source).
                    client.create_input(
                        sceneName=new_scene_name,
                        inputName=unique_source_name,
                        inputKind=template_source_kind,
                        inputSettings=template_source_settings,
                        sceneItemEnabled=True
                    )
                    print(f"Created unique source '{unique_source_name}' for new scene.")

                    # c. Get the ID of the newly created scene item.
                    new_item_id_response = client.get_scene_item_id(new_scene_name, unique_source_name)
                    new_item_id = new_item_id_response.scene_item_id

                    # d. Apply the saved transform to the new scene item.
                    client.set_scene_item_transform(new_scene_name, new_item_id, template_transform)
                    print(f"Applied transform from template to '{unique_source_name}'.")
                else:
                    # This is a regular item (like 'Base Layer'), just duplicate it.
                    client.duplicate_scene_item(scene_name=TEMPLATE_SCENE_NAME, item_id=item['sceneItemId'], dest_scene_name=new_scene_name)
                    print(f"Duplicated item '{item['sourceName']}' to '{new_scene_name}'.")

            # 3. Set the text content on the unique source.
            client.set_input_settings(
                name=unique_source_name,
                settings={'text': verse['obs_text']},
                overlay=True
            )
            print(f"Copied source and injected scripture text for {verse['reference']}")
    except Exception as e:
        print(f"OBS Automation Error: {e}")
    finally: # The client automatically disconnects when the 'with' block is exited, but explicit is fine.
        # The new client doesn't have a disconnect method in the same way. It's handled by context management or garbage collection.
        client.disconnect()
        print("Disconnected from OBS.")


# --- MAIN EXECUTION ---

def main():
    # 1. Setup Argument Parser
    original_collection_name = None
    parser = argparse.ArgumentParser(
        description="Automate OBS scene generation by fetching scripture text via API and injecting it into scene templates.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--ref',
        type=str,
        help="The scripture reference range (e.g., '1 Samuel 22:20-23')."
    )
    args = parser.parse_args()

    print("--- OBS SCENE GENERATOR (BSB) ---")
    print(f"Template Scene: {TEMPLATE_SCENE_NAME}")
    print(f"Template Scene Collection: {TEMPLATE_SCENE_COLLECTION_NAME}")
    print(f"Text Source Name: {SCROLLING_TEXT_SOURCE_NAME}")
    
    # 2. Get OBS Connection Details (Prefer Environment Variables)
    obs_host = os.environ.get('OBS_HOST', 'localhost')
    obs_port = int(os.environ.get('OBS_PORT', 4455))
    obs_password = os.environ.get('OBS_PASSWORD', '')

    # If environment variables are set, skip prompts for OBS connection
    if obs_password:
        print(f"Using credentials from environment variables (Host: {obs_host}, Port: {obs_port}).")
    else:
        # Prompt for details if environment variables are missing
        print("\nOBS connection details not found in environment variables. Prompting now:")
        obs_host = input(f"Enter OBS Host (default: {obs_host}): ") or obs_host
        try:
            obs_port = int(input(f"Enter OBS Port (default: {obs_port}): ") or obs_port)
        except ValueError:
            print("Invalid port, using default 4455.")
            obs_port = 4455
        obs_password = input("Enter OBS WebSocket Password (or leave blank): ")
    
    # 3. Get Scripture Reference (Prefer Command Line Argument)
    scripture_ref = args.ref
    if not scripture_ref:
        scripture_ref = input("\nEnter scripture reference (e.g., 1 Samuel 22:20-23): ")

    if not scripture_ref:
        print("\nScripture reference is required. Exiting.")
        return
    
    try:
        # 4. Fetch data and format
        verses = get_verses_from_api(scripture_ref)
        
        if not verses:
            print("No verses found or API fetch failed.")
            return

        print(f"\nFound {len(verses)} verses to process from {scripture_ref}.")
        client = ReqClient(host=obs_host, port=obs_port, password=obs_password, timeout=5)
        print("Attributes of client object:", dir(client)) # This will list everything
        # 5. Automate OBS scene creation
        automate_scene_generation(verses, obs_host, obs_port, obs_password)
        
        print("\n*** Automation Complete! ***")
        print("New scenes created/updated in OBS. Ready for image placement.")

    except ValueError as e:
        print(f"\nInput Error: {e}")
    except requests.RequestException as e:
        print(f"\nAPI Request Error: Failed to fetch scripture. Check API URL or Internet connection. {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
