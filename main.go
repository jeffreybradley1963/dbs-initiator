package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/jeffreybradley1963/dbs-initiator/bible"
	"github.com/jeffreybradley1963/dbs-initiator/gemini"
	"github.com/jeffreybradley1963/dbs-initiator/obs"
)

// --- Main Application Logic ---

func main() {
	// 1. Get scripture reference from command-line arguments.
	if len(os.Args) < 2 {
		log.Fatal("Please provide a scripture reference, e.g., \"John 3:16-17\"")
	}
	scriptureRefStr := os.Args[1]
	log.Printf("Processing reference: %s", scriptureRefStr)

	// --- CORE WORKFLOW ---
	err := processScripture(context.Background(), scriptureRefStr)
	if err != nil {
		log.Fatalf("Failed to process scripture: %v", err)
	}

	log.Println("Successfully generated all scenes and images in OBS.")
}

// processScripture is the main orchestrator function.
func processScripture(ctx context.Context, refStr string) error {
	// 2. Parse the reference string (like your Python function).
	reference, err := bible.ParseReference(refStr)
	if err != nil {
		return fmt.Errorf("invalid reference format: %w", err)
	}
	log.Printf("Parsed reference: %+v", reference) // Print the parsed struct for verification

	// 3. Fetch the full scripture text from the Bible API.
	verses, rawText, err := bible.FetchVerses(reference)
	if err != nil {
		return fmt.Errorf("could not retrieve scripture text: %w", err)
	}

	// 4. Connect to OBS.
	obsClient, err := obs.Connect()
	if err != nil {
		return fmt.Errorf("failed to connect to OBS: %w", err)
	}
	defer obsClient.Disconnect()

	// 5. Create individual verse scenes in OBS.
	// We loop backwards to ensure scenes are created in the correct order in the OBS UI.
	log.Println("Creating verse scenes in OBS (in reverse order for correct UI sorting)...")
	for i := len(verses) - 1; i >= 0; i-- {
		verse := verses[i]
		// obsText := formatTextForOBS(verse.Text) // We'll implement this later
		err := obsClient.CreateTextScene(verse.Reference, verse.Text)
		if err != nil {
			// Log the error but continue trying to create other scenes
			log.Printf("Warning: could not create OBS scene for %s: %v", verse.Reference, err)
		}
	}

	// Set the first verse's scene as the active one.
	if len(verses) > 0 {
		firstSceneName := verses[0].Reference
		obsClient.SetCurrentScene(firstSceneName)
	}

	// 6. Use Gemini LLM to get image generation prompts.
	log.Println("Asking Gemini to analyze scripture for image prompts...")
	imagePrompts, err := gemini.GenerateImagePrompts(ctx, rawText)
	if err != nil {
		return fmt.Errorf("failed to generate image prompts: %w", err)
	}

	// Create a directory for the generated images based on the scripture reference.
	// e.g., "output/1_Samuel_23"
	// We'll make this more specific to include the verse range to avoid overwrites.
	// e.g., "output/1_Samuel_23_1-5"
	safeBookName := strings.ReplaceAll(reference.Book, " ", "_")
	dirName := fmt.Sprintf("%s_%d_%d-%d", safeBookName, reference.Chapter, reference.StartVerse, reference.EndVerse)
	outputDir := filepath.Join("output", dirName)
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory '%s': %w", outputDir, err)
	}

	// 7. Generate images and create scenes in OBS.
	for i, prompt := range imagePrompts {
		log.Printf("Generating image %d of %d for verses %s: %s", i+1, len(imagePrompts), prompt.VerseRange, prompt.Description)

		// 7a. Generate the image data using our new function.
		imageData, err := gemini.GenerateImage(ctx, prompt.ImagePrompt)
		if err != nil {
			log.Printf("Warning: could not generate image for '%s': %v", prompt.Description, err)
			continue // Skip to the next prompt if image generation fails.
		}

		// 7b. Save the image to a local file inside the unique directory.
		imageFileName := fmt.Sprintf("img_%d.png", i)
		imageFilePath := filepath.Join(outputDir, imageFileName)
		err = os.WriteFile(imageFilePath, imageData, 0644)
		if err != nil {
			log.Printf("Warning: failed to save image file '%s': %v", imageFilePath, err)
			continue
		}
		log.Printf("Successfully saved image to %s", imageFilePath)

		// Get the absolute path to pass to OBS.
		absImageFilePath, err := filepath.Abs(imageFilePath)
		if err != nil {
			log.Printf("Warning: could not determine absolute path for '%s': %v", imageFilePath, err)
			continue
		}

		// 7c. Create the image scene in OBS, pointing to the new file.
		log.Printf("Creating OBS image scene for '%s'...", prompt.Description)
		obsClient.CreateImageScene(prompt.Description, absImageFilePath)
	}

	return nil
}
