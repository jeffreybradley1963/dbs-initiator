package config

import (
	"os"
	"strconv"
)

var (
	// APIBaseURL is the base URL for the Bible API.
	APIBaseURL = "https://bible.helloao.org/api/BSB"
	// MaxCharsPerLine is the target character limit for wrapping text lines in OBS.
	MaxCharsPerLine = 45
	// TemplateSceneName is the name of the OBS scene to use as a template.
	TemplateSceneName = "Scripture-Template"
	// ScrollingTextSourceName is the name of the text source within the template scene.
	ScrollingTextSourceName = "sTextScrolling"
	// ImageTemplateSceneName is the name of the OBS scene to use as a template for generated images.
	ImageTemplateSceneName = "ImageAndDiscussion"
	// ImageSourceName is the name of the image source within the image template scene.
	// This is used to find the source type and copy its settings.
	ImageSourceName = "ScriptureIllustration"

	// OBS Configuration - populated from environment variables at startup.
	OBSHost     string
	OBSPort     int
	OBSPassword string

	// GeminiAPIKey is the API key for the Google Gemini service.
	GeminiAPIKey string
)

// init is a special Go function that runs automatically on package initialization.
// It's the perfect place to load configuration from the environment.
func init() {
	// Load OBS_HOST, default to "localhost"
	OBSHost = os.Getenv("OBS_HOST")
	if OBSHost == "" {
		OBSHost = "localhost"
	}

	// Load OBS_PASSWORD
	OBSPassword = os.Getenv("OBS_PASSWORD")

	// Load OBS_PORT, default to 4455
	portStr := os.Getenv("OBS_PORT")
	OBSPort, _ = strconv.Atoi(portStr) // Atoi returns 0 on error, which is fine for a default.
	if OBSPort == 0 {
		OBSPort = 4455
	}

	// Load GEMINI_API_KEY
	GeminiAPIKey = os.Getenv("GEMINI_API_KEY")
}

// BibleBookIDs maps the full book name to its 3-letter API identifier.
var BibleBookIDs = map[string]string{
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
	"1 John": "1JN", "2 John": "2JN", "3 John": "3JN", "Jude": "JUD", "Revelation": "REV",
}

// BookAbbreviations maps common abbreviations to the canonical book name used in BibleBookIDs.
var BookAbbreviations = map[string]string{
	"gen": "Genesis", "ex": "Exodus", "lev": "Leviticus", "num": "Numbers", "deut": "Deuteronomy",
	"josh": "Joshua", "judg": "Judges", "1 sam": "1 Samuel", "2 sam": "2 Samuel", "1 kgs": "1 Kings",
	"2 kgs": "2 Kings", "1 chr": "1 Chronicles", "2 chr": "2 Chronicles", "ps": "Psalms", "prov": "Proverbs",
	"eccl": "Ecclesiastes", "isa": "Isaiah", "jer": "Jeremiah", "lam": "Lamentations", "ezek": "Ezekiel",
	"dan": "Daniel", "hos": "Hosea", "joel": "Joel", "amos": "Amos", "obad": "Obadiah", "jonah": "Jonah",
	"mic": "Micah", "nah": "Nahum", "hab": "Habakkuk", "zeph": "Zephaniah", "hag": "Haggai", "zech": "Zechariah",
	"mal": "Malachi", "matt": "Matthew", "mark": "Mark", "luke": "Luke", "john": "John", "acts": "Acts",
	"rom": "Romans", "1 cor": "1 Corinthians", "2 cor": "2 Corinthians", "gal": "Galatians", "eph": "Ephesians",
	"phil": "Philippians", "col": "Colossians", "1 thess": "1 Thessalonians", "2 thess": "2 Thessalonians",
	"1 tim": "1 Timothy", "2 tim": "2 Timothy", "heb": "Hebrews", "1 pet": "1 Peter", "2 pet": "2 Peter",
	"1 jn": "1 John", "2 jn": "2 John", "3 jn": "3 John", "rev": "Revelation",
}
