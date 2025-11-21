package bible

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/jeffreybradley1963/dbs-initiator/config"
)

// --- Exported Types ---

// Reference holds parsed Bible reference details.
type Reference struct {
	Book       string
	Chapter    int
	StartVerse int
	EndVerse   int
}

// Verse holds the reference and text for a single Bible verse.
type Verse struct {
	Reference string
	Text      string
}

// --- Internal API Parsing Structs ---

type apiBook struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type apiContentItem struct {
	Type    string        `json:"type"`
	Number  json.Number   `json:"number"`
	Content []interface{} `json:"content"`
}

type apiChapter struct {
	Number  json.Number      `json:"number"`
	Content []apiContentItem `json:"content"`
}

type apiResponse struct {
	Book    apiBook    `json:"book"`
	Chapter apiChapter `json:"chapter"`
}

var refRegex = regexp.MustCompile(`(?i)^(\d?\s?[a-zA-Z\.]+)\s+(\d+):(\d+)(?:-(\d+))?$`)

// ParseReference parses a string like "John 3:16-17" into a Reference struct.
func ParseReference(refStr string) (Reference, error) {
	matches := refRegex.FindStringSubmatch(refStr)
	if matches == nil {
		return Reference{}, fmt.Errorf("invalid format: '%s'", refStr)
	}

	bookInput := strings.ToLower(strings.TrimSpace(matches[1]))
	book, ok := config.BookAbbreviations[bookInput]
	if !ok {
		for key := range config.BibleBookIDs {
			if strings.EqualFold(key, bookInput) {
				book = key
				break
			}
		}
	}

	if book == "" {
		return Reference{}, fmt.Errorf("book '%s' not found or not supported", matches[1])
	}

	chapter, err := strconv.Atoi(matches[2])
	if err != nil {
		return Reference{}, fmt.Errorf("could not parse chapter '%s': %w", matches[2], err)
	}

	startVerse, err := strconv.Atoi(matches[3])
	if err != nil {
		return Reference{}, fmt.Errorf("could not parse start verse '%s': %w", matches[3], err)
	}

	endVerse := startVerse
	if len(matches[4]) > 0 {
		endVerse, err = strconv.Atoi(matches[4])
		if err != nil {
			return Reference{}, fmt.Errorf("could not parse end verse '%s': %w", matches[4], err)
		}
	}
	return Reference{Book: book, Chapter: chapter, StartVerse: startVerse, EndVerse: endVerse}, nil
}

// FetchVerses retrieves scripture text from the remote Bible API.
func FetchVerses(ref Reference) ([]Verse, string, string, error) {
	bookID, ok := config.BibleBookIDs[ref.Book]
	if !ok {
		return nil, "", "", fmt.Errorf("book '%s' does not have a corresponding API ID", ref.Book)
	}

	url := fmt.Sprintf("%s/%s/%d.json", config.APIBaseURL, bookID, ref.Chapter)
	log.Printf("Fetching scripture from: %s", url)

	resp, err := http.Get(url)
	if err != nil {
		return nil, "", "", fmt.Errorf("failed to make API request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, "", "", fmt.Errorf("API returned non-200 status: %s", resp.Status)
	}

	var apiResp apiResponse
	if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
		return nil, "", "", fmt.Errorf("failed to decode API response: %w", err)
	}

	var filteredVerses []Verse
	var textBuilder strings.Builder
	var currentHeading string
	var title string

	for _, item := range apiResp.Chapter.Content {
		if item.Type == "heading" {
			if len(item.Content) > 0 {
				if h, ok := item.Content[0].(string); ok {
					currentHeading = h
				}
			}
			continue
		}

		if item.Type != "verse" {
			continue
		}

		verseNum, err := item.Number.Int64()
		if err != nil {
			continue
		}

		if int(verseNum) >= ref.StartVerse && int(verseNum) <= ref.EndVerse {
			// If we haven't set a title yet, use the most recent heading
			if title == "" {
				title = currentHeading
			}

			verseTextContent, ok := item.Content[0].(string)
			if !ok {
				continue
			}

			verseRef := fmt.Sprintf("%s %d:%d", ref.Book, ref.Chapter, int(verseNum))
			verseText := fmt.Sprintf("[%d] %s", int(verseNum), verseTextContent)

			filteredVerses = append(filteredVerses, Verse{Reference: verseRef, Text: verseText})

			if textBuilder.Len() > 0 {
				textBuilder.WriteString(" ")
			}
			textBuilder.WriteString(verseText)
		}
	}

	if len(filteredVerses) == 0 {
		return nil, "", "", fmt.Errorf("no verses found for reference %s %d:%d-%d", ref.Book, ref.Chapter, ref.StartVerse, ref.EndVerse)
	}

	return filteredVerses, textBuilder.String(), title, nil
}
