# tests/test_bible_utils.py

import pytest
from bible_utils import parse_reference, format_text_for_obs, get_verses_from_api

# --- Test 1: A simple, pure function ---
def test_parse_reference_single_verse():
    """Tests parsing a standard 'Book C:V' reference."""
    ref = "John 3:16"
    expected = {'book': 'John', 'chapter': 3, 'start_verse': 16, 'end_verse': 16}
    assert parse_reference(ref) == expected

def test_parse_reference_verse_range():
    """Tests parsing a 'Book C:V-V' reference."""
    ref = "1 Samuel 23:1-6"
    expected = {'book': '1 Samuel', 'chapter': 23, 'start_verse': 1, 'end_verse': 6}
    assert parse_reference(ref) == expected

def test_parse_reference_with_dot():
    """Tests that it handles periods in book names."""
    ref = "1 Sam. 23:1"
    expected = {'book': '1 Samuel', 'chapter': 23, 'start_verse': 1, 'end_verse': 1}
    assert parse_reference(ref) == expected

def test_parse_reference_invalid():
    """Tests that it raises an error for an invalid format."""
    with pytest.raises(ValueError):
        parse_reference("Invalid Reference")

# --- Test 2: Another pure function ---
def test_format_text_for_obs():
    """Tests the text wrapping logic."""
    # Assuming MAX_CHARS_PER_LINE = 50 in config.py
    long_text = "This is a very long line of text that should definitely be wrapped into multiple lines by the formatting function."
    expected = "This is a very long line of text that should\ndefinitely be wrapped into multiple lines by the\nformatting function."
    assert format_text_for_obs(long_text) == expected

# --- Test 3: A function with an external dependency (the API call) ---
def test_get_verses_from_api(requests_mock):
    """
    Tests the API fetching and processing logic by mocking the requests.get call.
    We don't want our tests to actually hit the network.
    """
    # 1. Define the fake data our mock API will return
    fake_api_response = {
        "chapter": {
            "content": [
                {"type": "verse", "number": 16, "content": ["For God so loved the world..."]},
                {"type": "verse", "number": 17, "content": ["For God did not send his Son..."]}
            ]
        }
    }
    
    # 2. Tell requests_mock to intercept calls to this URL and return our fake data
    api_url = "https://bible.helloao.org/api/BSB/JHN/3.json"
    requests_mock.get(api_url, json=fake_api_response)

    # 3. Call our function
    verses = get_verses_from_api("John 3:16-17")

    # 4. Assert that our function processed the fake data correctly
    assert len(verses) == 2
    assert verses[0]['reference'] == "John 3:16"
    assert "For God so loved the world..." in verses[0]['obs_text']
    assert verses[1]['reference'] == "John 3:17"
    assert "For God did not send his Son..." in verses[1]['obs_text']
