package obs

import (
	"fmt"
	"log"

	"github.com/andreykaipov/goobs"
	"github.com/andreykaipov/goobs/api/requests/inputs"
	"github.com/andreykaipov/goobs/api/requests/sceneitems"
	"github.com/andreykaipov/goobs/api/requests/scenes"
	"github.com/jeffreybradley1963/dbs-initiator/config"
)

// OBSClient defines the interface for all OBS operations our application needs.
// This allows us to use a real client in production and a mock client in tests.
type OBSClient interface {
	CreateTextScene(sceneName, text string) error
	CreateImageScene(sceneName, imageFilePath string) error
	SetCurrentScene(sceneName string)
	Disconnect() error
}

// clientImpl is the concrete implementation of our OBSClient interface.
type clientImpl struct {
	*goobs.Client
}

// Connect establishes a connection to the OBS WebSocket server.
func Connect() (OBSClient, error) {
	client, err := goobs.New(
		fmt.Sprintf("%s:%d", config.OBSHost, config.OBSPort),
		goobs.WithPassword(config.OBSPassword),
	)
	if err != nil {
		return nil, err
	}
	log.Println("Successfully connected to OBS.")
	return &clientImpl{Client: client}, nil
}

// CreateTextScene creates a new scene by copying a template and updates its text source.
func (c *clientImpl) CreateTextScene(sceneName, text string) error {
	return c.createSceneFromTemplate(
		sceneName,
		config.TemplateSceneName,
		config.ScrollingTextSourceName,
		"text-",
		map[string]interface{}{"text": text},
	)
}

// CreateImageScene creates a new scene for a generated image.
func (c *clientImpl) CreateImageScene(sceneName, imageFilePath string) error {
	return c.createSceneFromTemplate(
		sceneName,
		config.ImageTemplateSceneName,
		config.ImageSourceName,
		"img-",
		map[string]interface{}{"file": imageFilePath},
	)
}

// createSceneFromTemplate is a generic helper function to handle the scene creation workflow.
func (c *clientImpl) createSceneFromTemplate(sceneName, templateSceneName, templateSourceName, newSourcePrefix string, finalSettings map[string]interface{}) error {
	// 1. Create the new, empty scene. We'll ignore the error if it already exists.
	_, err := c.Scenes.CreateScene(&scenes.CreateSceneParams{
		SceneName: &sceneName,
	})
	if err != nil {
		log.Printf("Note: Could not create scene '%s' (it may already exist). Error: %v", sceneName, err)
	}

	// 2. Get all items from the template scene to copy them.
	resp, err := c.SceneItems.GetSceneItemList(&sceneitems.GetSceneItemListParams{
		SceneName: &templateSceneName,
	})
	if err != nil {
		return fmt.Errorf("could not get item list from template scene '%s': %w", templateSceneName, err)
	}

	// 3. Create a new, unique source for this specific scene.
	newSourceName := fmt.Sprintf("%s%s", newSourcePrefix, sceneName)

	// Get settings from the template source to use as a base.
	settingsResp, err := c.Inputs.GetInputSettings(&inputs.GetInputSettingsParams{
		InputName: &templateSourceName,
	})
	if err != nil {
		return fmt.Errorf("could not get settings from template source '%s': %w", templateSourceName, err)
	}

	// Create the new input, inheriting the template's settings.
	_, err = c.Inputs.CreateInput(&inputs.CreateInputParams{
		SceneName:        &sceneName,
		InputName:        &newSourceName,
		InputKind:        &settingsResp.InputKind, // Should be "image_source"
		InputSettings:    settingsResp.InputSettings,
		SceneItemEnabled: boolp(true),
	})
	if err != nil {
		log.Printf("Note: Could not create new source '%s' (it may already exist). Error: %v", newSourceName, err)
	}

	// 4. Copy all other items from the template to the new scene.
	for _, item := range resp.SceneItems {
		if item.SourceName == templateSourceName {
			continue // Skip the template source itself.
		}
		_, err := c.SceneItems.CreateSceneItem(&sceneitems.CreateSceneItemParams{
			SceneName:  &sceneName,
			SourceName: &item.SourceName,
		})
		if err != nil {
			log.Printf("Warning: could not copy source '%s' to scene '%s': %v", item.SourceName, sceneName, err)
		}
	}

	// 5. Finally, apply the final settings to our new, unique source.
	_, err = c.Inputs.SetInputSettings(&inputs.SetInputSettingsParams{
		InputName:     &newSourceName,
		InputSettings: finalSettings,
	})

	log.Printf("Successfully created/updated scene '%s'", sceneName)
	return err
}

// SetCurrentScene makes the given scene the active program scene.
func (c *clientImpl) SetCurrentScene(sceneName string) {
	if sceneName != "" {
		log.Printf("Setting '%s' as the active scene.", sceneName)
		_, err := c.Scenes.SetCurrentProgramScene(&scenes.SetCurrentProgramSceneParams{
			SceneName: &sceneName,
		})
		if err != nil {
			log.Printf("Warning: could not set current scene to '%s': %v", sceneName, err)
		}
	}
}

// boolp is a helper function to return a pointer to a bool.
func boolp(b bool) *bool {
	return &b
}
