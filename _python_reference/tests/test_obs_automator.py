# tests/test_obs_automator.py

import pytest
from unittest.mock import MagicMock, call
from obs_automator import automate_scene_generation

# A fixture to create a reusable mock client for our tests
@pytest.fixture
def mock_obs_client():
    """Creates a mock OBS client that simulates the obsws_python ReqClient."""
    client = MagicMock()

    # --- Simulate the responses from OBS ---
    # Simulate finding the template scene and its items
    client.get_scene_item_list.return_value.scene_items = [
        {'sourceName': 'background', 'sceneItemId': 1},
        {'sourceName': 'sTextScrolling', 'sceneItemId': 2}
    ]
    # Simulate finding the text source's settings
    client.get_input_settings.return_value.input_settings = {'text': 'template text'}
    client.get_input_settings.return_value.input_kind = 'text_ft2_source_v2'
    # Simulate getting an item's transform
    client.get_scene_item_transform.return_value.scene_item_transform = {
        'scaleX': 1.0,
        'boundsWidth': 1920.0,
        'boundsHeight': 1080.0
    }
    # Simulate getting the ID of a newly created item
    client.get_scene_item_id.return_value.scene_item_id = 101

    return client

def test_creates_new_scene_and_sources(mock_obs_client):
    """
    Tests the primary path: creating a new scene for a verse.
    """
    # 1. Define the input data
    verses = [{
        'scene_name': 'Scripture-JHN-3:16',
        'reference': 'John 3:16',
        'obs_text': 'Formatted text for John 3:16'
    }]

    # Simulate OBS having no pre-existing scripture scenes
    mock_obs_client.get_scene_list.return_value.scenes = []

    # 2. Call the function with the mock client
    automate_scene_generation(mock_obs_client, verses)

    # 3. Assert that the correct methods were called on the mock client
    # Was a new scene created?
    mock_obs_client.create_scene.assert_called_with('Scripture-JHN-3:16')
    
    # Was the background duplicated?
    mock_obs_client.duplicate_scene_item.assert_called_with(
        scene_name='Scripture-Template', 
        item_id=1, 
        dest_scene_name='Scripture-JHN-3:16'
    )

    # Was a new, unique text source created?
    mock_obs_client.create_input.assert_called()
    
    # Was the final text set correctly?
    mock_obs_client.set_input_settings.assert_called_with(
        name='sTextScrolling_John_3-16',
        settings={'text': 'Formatted text for John 3:16'},
        overlay=True
    )

def test_updates_existing_scene(mock_obs_client):
    """
    Tests the update path: when a scene for a verse already exists.
    """
    verses = [{
        'scene_name': 'Scripture-JHN-3:16',
        'reference': 'John 3:16',
        'obs_text': 'NEW formatted text for John 3:16'
    }]

    # Simulate OBS already having this scene
    mock_obs_client.get_scene_list.return_value.scenes = [{'sceneName': 'Scripture-JHN-3:16'}]

    automate_scene_generation(mock_obs_client, verses)

    # Assert that a new scene was NOT created
    mock_obs_client.create_scene.assert_not_called()
    
    # Assert that the text was updated on the existing source
    mock_obs_client.set_input_settings.assert_called_with(
        name='sTextScrolling_John_3-16',
        settings={'text': 'NEW formatted text for John 3:16'},
        overlay=True
    )
