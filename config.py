# --- CONFIGURATION & BIBLE DATA ---

# Your API base URL (Free Bible API used in the Apps Script logic)
API_BASE_URL = "https://bible.helloao.org/api/BSB"

# Max characters per line for your 1080x1920 vertical format
# This should be adjusted based on your chosen font size (e.g., 40-55 characters)
MAX_CHARS_PER_LINE = 20

# ID of the scene you have already created in OBS that will be duplicated.
# This scene MUST contain a Text (FreeType 2) source named 'SCROLLING_TEXT_SOURCE_NAME'.
TEMPLATE_SCENE_NAME = "Scripture-Template"
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

# Maps common abbreviations to the canonical book name used in BIBLE_BOOK_IDS
BOOK_ABBREVIATIONS = {
    "gen": "Genesis", "ex": "Exodus", "lev": "Leviticus", "num": "Numbers", "deut": "Deuteronomy",
    "josh": "Joshua", "judg": "Judges", "ruth": "Ruth", "1 sam": "1 Samuel", "2 sam": "2 Samuel",
    "1 kgs": "1 Kings", "2 kgs": "2 Kings", "1 chr": "1 Chronicles", "2 chr": "2 Chronicles",
    "ezra": "Ezra", "neh": "Nehemiah", "esth": "Esther", "job": "Job", "ps": "Psalms",
    "prov": "Proverbs", "eccl": "Ecclesiastes", "song": "Song of Songs", "isa": "Isaiah",
    "jer": "Jeremiah", "lam": "Lamentations", "ezek": "Ezekiel", "dan": "Daniel", "hos": "Hosea",
    "joel": "Joel", "amos": "Amos", "obad": "Obadiah", "jonah": "Jonah", "mic": "Micah",
    "nah": "Nahum", "hab": "Habakkuk", "zeph": "Zephaniah", "hag": "Haggai", "zech": "Zechariah",
    "mal": "Malachi", "matt": "Matthew", "mark": "Mark", "luke": "Luke", "john": "John",
    "acts": "Acts", "rom": "Romans", "1 cor": "1 Corinthians", "2 cor": "2 Corinthians",
    "gal": "Galatians", "eph": "Ephesians", "phil": "Philippians", "col": "Colossians",
    "1 thess": "1 Thessalonians", "2 thess": "2 Thessalonians", "1 tim": "1 Timothy",
    "2 tim": "2 Timothy", "titus": "Titus", "philem": "Philemon", "heb": "Hebrews",
    "james": "James", "1 pet": "1 Peter", "2 pet": "2 Peter", "1 jn": "1 John", "2 jn": "2 John",
    "3 jn": "3 John", "jude": "Jude", "rev": "Revelation"
}