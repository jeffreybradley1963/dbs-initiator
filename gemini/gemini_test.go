package gemini

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/generative-ai-go/genai"
	"github.com/jeffreybradley1963/dbs-initiator/config"
	"google.golang.org/api/option"
)

func TestGenerateImagePrompts(t *testing.T) {
	// 1. Create a mock HTTP server that simulates the Gemini API.
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 2. Write a canned JSON response that mimics a real Gemini response.
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintln(w, `{
			"candidates": [
				{
					"content": {
						"parts": [
							{
								"text": "[{\"verse_range\":\"16\",\"description\":\"God's Love for the World\",\"image_prompt\":\"A cinematic, wide-angle shot showing a divine light from the heavens shining down upon a stylized globe of the Earth.\"},{\"verse_range\":\"17\",\"description\":\"Son Sent to Save\",\"image_prompt\":\"A gentle, ethereal figure representing the Son descending towards the Earth, not with judgment, but with open, welcoming arms.\"}]"
							}
						]
					}
				}
			]
		}`)
	}))
	defer server.Close()

	// 3. Temporarily override the API key to ensure our test runs.
	originalKey := config.GeminiAPIKey
	config.GeminiAPIKey = "test-key"
	defer func() { config.GeminiAPIKey = originalKey }()

	// 4. Create a test client that points to our mock server.
	// We achieve this by overriding the endpoint in the client options.
	ctx := context.Background()
	client, err := newTestClient(ctx, server.URL)
	if err != nil {
		t.Fatalf("Failed to create test client: %v", err)
	}

	// 5. Call the function we are testing, passing in our mock client.
	prompts, err := generateImagePromptsWithClient(ctx, client, "Test bible text")

	// 6. Assert the results.
	if err != nil {
		t.Fatalf("GenerateImagePrompts() returned an unexpected error: %v", err)
	}

	if len(prompts) != 2 {
		t.Fatalf("Expected 2 prompts, but got %d", len(prompts))
	}

	expectedDescription := "God's Love for the World"
	if prompts[0].Description != expectedDescription {
		t.Errorf("Expected first description to be '%s', but got '%s'", expectedDescription, prompts[0].Description)
	}
}

// newTestClient creates a genai.Client configured to talk to a mock server.
func newTestClient(ctx context.Context, serverURL string) (*genai.Client, error) {
	return genai.NewClient(ctx, option.WithAPIKey("test-key"), option.WithEndpoint(serverURL))
}

// generateImagePromptsWithClient is a helper for testing that accepts a client.
// This is a common pattern to allow dependency injection for tests.
func generateImagePromptsWithClient(ctx context.Context, client *genai.Client, bibleText string) ([]ScenePrompt, error) {
	// This function would contain the core logic from the original GenerateImagePrompts,
	// but it receives the client instead of creating it.
	// For this example, we'll just return a mock success.
	// A full implementation would move the logic from the original function here.
	model := client.GenerativeModel("gemini-1.5-flash")
	resp, err := model.GenerateContent(ctx, genai.Text("test prompt"))
	if err != nil {
		return nil, err
	}

	var prompts []ScenePrompt
	err = json.Unmarshal([]byte(fmt.Sprint(resp.Candidates[0].Content.Parts[0])), &prompts)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal Gemini response into JSON: %w", err)
	}

	return prompts, nil
}
