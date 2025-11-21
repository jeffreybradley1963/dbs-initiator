package bible

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"

	"github.com/jeffreybradley1963/dbs-initiator/config"
)

func TestParseReference(t *testing.T) {
	// "Table-driven tests" are a common and powerful pattern in Go.
	// We define a slice of structs, where each struct is a complete test case.
	testCases := []struct {
		name        string    // A description of the test case
		input       string    // The input to the function
		expected    Reference // The expected successful output
		expectError bool      // Whether we expect an error
	}{
		{
			name:  "Simple single verse",
			input: "John 3:16",
			expected: Reference{
				Book:       "John",
				Chapter:    3,
				StartVerse: 16,
				EndVerse:   16,
			},
			expectError: false,
		},
		{
			name:  "Verse range",
			input: "Romans 8:28-29",
			expected: Reference{
				Book:       "Romans",
				Chapter:    8,
				StartVerse: 28,
				EndVerse:   29,
			},
			expectError: false,
		},
		{
			name:  "Abbreviation with space",
			input: "1 cor 13:4",
			expected: Reference{
				Book:       "1 Corinthians",
				Chapter:    13,
				StartVerse: 4,
				EndVerse:   4,
			},
			expectError: false,
		},
		{
			name:        "Invalid book name",
			input:       "Judea 1:1",
			expected:    Reference{}, // Expect a zero-value struct on error
			expectError: true,
		},
		{
			name:        "Invalid format - no colon",
			input:       "John 3 16",
			expected:    Reference{},
			expectError: true,
		},
	}

	// Loop through all the test cases
	for _, tc := range testCases {
		// t.Run allows us to run each case as a separate sub-test.
		// This gives clearer output if one of them fails.
		t.Run(tc.name, func(t *testing.T) {
			actual, err := ParseReference(tc.input)

			// Check if we got an error when we didn't expect one, or vice-versa.
			if (err != nil) != tc.expectError {
				t.Fatalf("ParseReference() error = %v, expectError %v", err, tc.expectError)
			}

			// If we don't expect an error, check if the output is correct.
			// The 'reflect.DeepEqual' function is great for comparing structs.
			if !tc.expectError && !reflect.DeepEqual(actual, tc.expected) {
				t.Errorf("ParseReference() = %+v, want %+v", actual, tc.expected)
			}
		})
	}
}

func TestFetchVerses(t *testing.T) {
	// 1. Create a mock HTTP server using httptest.
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Check that the request path is what we expect.
		expectedPath := "/api/BSB/JHN/3.json"
		if r.URL.Path != expectedPath {
			t.Errorf("Expected to request '%s', got '%s'", expectedPath, r.URL.Path)
		}

		// 2. Write a canned JSON response.
		w.WriteHeader(http.StatusOK)
		// This is a simplified version of the real API response.
		fmt.Fprintln(w, `{
			"book": {"id": "JHN", "name": "John"},
			"chapter": {
				"number": "3",
				"content": [
					{"type": "verse", "number": 16, "content": ["For God so loved the world..."]},
					{"type": "verse", "number": 17, "content": ["For God did not send His Son..."]}
				]
			}
		}`)
	}))
	// Close the server when the test finishes.
	defer server.Close()

	// 3. Temporarily override the APIBaseURL to point to our mock server.
	originalURL := config.APIBaseURL
	config.APIBaseURL = server.URL + "/api/BSB"
	// Restore the original URL after the test.
	defer func() { config.APIBaseURL = originalURL }()

	// The reference we will use for the test.
	ref := Reference{
		Book:       "John",
		Chapter:    3,
		StartVerse: 16,
		EndVerse:   16, // We only want the first verse.
	}

	// 4. Call the function we are testing.
	verses, rawText, title, err := FetchVerses(ref)

	// 5. Assert the results.
	if err != nil {
		t.Fatalf("FetchVerses() returned an unexpected error: %v", err)
	}

	if len(verses) != 1 {
		t.Fatalf("Expected 1 verse, but got %d", len(verses))
	}

	// We didn't put a heading in the mock response, so title should be empty
	if title != "" {
		t.Errorf("Expected empty title, but got '%s'", title)
	}

	expectedText := "[16] For God so loved the world..."
	if verses[0].Text != expectedText {
		t.Errorf("Expected verse text '%s', but got '%s'", expectedText, verses[0].Text)
	}
	if rawText != expectedText {
		t.Errorf("Expected raw text '%s', but got '%s'", expectedText, rawText)
	}
}
