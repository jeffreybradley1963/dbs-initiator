package gemini

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/google/generative-ai-go/genai"
	"github.com/jeffreybradley1963/dbs-initiator/config"
	"google.golang.org/api/option"
)

// ScenePrompt is the structure we'll ask the Gemini LLM to generate.
type ScenePrompt struct {
	VerseRange  string `json:"verse_range"`
	Description string `json:"description"`
	ImagePrompt string `json:"image_prompt"`
}

// GenerateImagePrompts uses the Gemini LLM to analyze scripture and suggest image prompts.
func GenerateImagePrompts(ctx context.Context, bibleText string) ([]ScenePrompt, error) {
	if config.GeminiAPIKey == "" {
		return nil, fmt.Errorf("GEMINI_API_KEY environment variable not set")
	}

	// Explicitly use the v1 API to ensure access to the latest models.
	client, err := genai.NewClient(ctx,
		option.WithAPIKey(config.GeminiAPIKey),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create Gemini client: %w", err)
	}
	defer client.Close()

	log.Println("Sending request to Gemini to generate image prompts...")

	prompt := fmt.Sprintf(`
Analyze the following bible verses. Identify 1 to 3 key moments or themes that would be suitable for a visual representation.
For each moment, provide a JSON object with three fields:
1. "verse_range": A string indicating the verse or verses it applies to (e.g., "16", "17-18").
2. "description": A very short, 3-5 word description suitable for a scene name (e.g., "God's Love for the World").
3. "image_prompt": A detailed, artistic prompt for an image generation model. Describe the scene, mood, style (e.g., "cinematic, dramatic lighting"), and composition.

Bible Text:
---
%s
---
`, bibleText)

	// Use a fast text model that supports JSON output mode.
	model := client.GenerativeModel("models/gemini-2.5-flash")
	model.SetTemperature(0.2)
	model.ResponseMIMEType = "application/json"

	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		return nil, fmt.Errorf("failed to generate content from Gemini: %w", err)
	}

	var prompts []ScenePrompt
	err = json.Unmarshal([]byte(fmt.Sprint(resp.Candidates[0].Content.Parts[0])), &prompts)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal Gemini response into JSON: %w", err)
	}

	return prompts, nil
}

// GenerateImage creates an image from a text prompt using a Gemini model.
func GenerateImage(ctx context.Context, prompt string) ([]byte, error) {
	if config.GeminiAPIKey == "" {
		return nil, fmt.Errorf("GEMINI_API_KEY environment variable not set")
	}

	// Use a client with the v1 API for image generation models.
	client, err := genai.NewClient(ctx,
		option.WithAPIKey(config.GeminiAPIKey),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create Gemini client for image generation: %w", err)
	}
	defer client.Close()
	// Retrieve the list of models
	// iter := client.ListModels(ctx) // Use nil for default ListModelsConfig
	// for {
	// 	model, err := iter.Next()
	// 	if err != nil {
	// 		break
	// 	}
	// 	if err != nil {
	// 		log.Fatal(err)
	// 	}
	// 	fmt.Printf("Model Name: %s, Supported Actions: %v\n", model.Name, model.SupportedGenerationMethods)
	// }
	// Use a model capable of image generation.
	model := client.GenerativeModel("models/gemini-2.5-flash-image")

	log.Printf("Sending image generation request to Gemini...")
	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		return nil, fmt.Errorf("failed to generate image from Gemini: %w", err)
	}

	// Extract the raw image data from the response.
	if len(resp.Candidates) == 0 {
		return nil, fmt.Errorf("gemini response contained no candidates")
	}

	// Check if the generation was stopped for safety reasons.
	candidate := resp.Candidates[0]
	if candidate.FinishReason == genai.FinishReasonSafety {
		// Log the specific safety ratings if available.
		return nil, fmt.Errorf("image generation was blocked by safety filters. Ratings: %v", candidate.SafetyRatings)
	}

	// Iterate through all parts of the response to find the image blob.
	// This is more robust than assuming it's always the first part.
	for _, part := range candidate.Content.Parts {
		if blob, ok := part.(genai.Blob); ok {
			return blob.Data, nil
		}
	}

	// If we get here, no image data was found. Log the finish reason for debugging.
	return nil, fmt.Errorf("no image data found in Gemini response (FinishReason: %s)", candidate.FinishReason)
}
