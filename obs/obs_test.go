package obs

import "testing"

// mockOBSClient is a mock implementation of our OBSClient interface for testing.
type mockOBSClient struct {
	// We can add fields here to track calls and assert behavior.
	// For example:
	// lastSceneCreated string
	// lastSceneSet     string
	// disconnectCalled bool
}

// CreateTextScene is the mock implementation.
func (m *mockOBSClient) CreateTextScene(sceneName, text string) error {
	// In a real test, we would record the sceneName and text.
	// m.lastSceneCreated = sceneName
	return nil // Simulate success
}

// SetCurrentScene is the mock implementation.
func (m *mockOBSClient) SetCurrentScene(sceneName string) {
	// m.lastSceneSet = sceneName
}

// Disconnect is the mock implementation.
func (m *mockOBSClient) Disconnect() error {
	// m.disconnectCalled = true
	return nil
}

// TestClient_CreateTextScene is a placeholder for a future test.
// Fully testing the real CreateTextScene is complex as it involves many
// calls to the underlying goobs client. For now, we've set up the structure
// with a mock that allows other parts of our application to be tested easily.
func TestClient_CreateTextScene(t *testing.T) {
	// This is where you would write a test for the real clientImpl if needed.
	// It would likely be an integration test that requires a running OBS instance.
	t.Skip("Skipping integration test for CreateTextScene for now.")
}
