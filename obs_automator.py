from obsws_python import ReqClient
from config import TEMPLATE_SCENE_NAME, SCROLLING_TEXT_SOURCE_NAME

def automate_scene_generation(verses, host, port, password):
    """Connects to OBS and automates scene creation and modification."""
    print("Connecting to OBS WebSocket...")
    try:
        # Initialize the client
        # The ReqClient constructor handles the connection.
        client = ReqClient(host=host, port=port, password=password, timeout=5)

    except Exception as e:
        print(f"ERROR: Could not connect to OBS. Ensure OBS is running, the WebSocket Server is enabled (under Tools), and the connection details are correct. Details: {e}")
        return

    print("Successfully connected to OBS.")
    try:
        # Get all scenes to check for existing scenes
        scenes_response = client.get_scene_list()
        all_scenes = scenes_response.scenes

        # Get settings of the template scrolling text source
        template_source_settings_response = client.get_input_settings(SCROLLING_TEXT_SOURCE_NAME)
        template_source_settings = template_source_settings_response.input_settings
        template_source_kind = template_source_settings_response.input_kind

        # Get all items from the template scene to duplicate them
        template_scene_items_response = client.get_scene_item_list(TEMPLATE_SCENE_NAME)
        template_scene_items = template_scene_items_response.scene_items

        print(f"Attempting to create scenes and inject text based on '{TEMPLATE_SCENE_NAME}'...")

        for verse in verses:
            new_scene_name = verse['scene_name']
            # Create a unique source name for each verse's text source
            unique_source_name = f"{SCROLLING_TEXT_SOURCE_NAME}_{verse['reference'].replace(' ', '_').replace(':', '-')}"

            # Check if scene already exists
            scene_exists = False
            for scene in all_scenes:
                if scene['sceneName'] == new_scene_name:
                    scene_exists = True
                    break

            if scene_exists:
                print(f"Scene '{new_scene_name}' already exists. Skipping creation and updating text.")
                # Update the text content of the unique source associated with this existing scene
                client.set_input_settings(
                    name=unique_source_name,
                    settings={'text': verse['obs_text']},
                    overlay=True
                )
                print(f"Updated text in existing scene: {new_scene_name}")
                continue

            # 1. Create a new, empty scene.
            client.create_scene(new_scene_name)
            print(f"Created new scene: {new_scene_name}")

            # 2. Duplicate all items from the template scene, handling the text source specially.
            for item in template_scene_items:
                if item['sourceName'] == SCROLLING_TEXT_SOURCE_NAME:
                    # This is our special text source. Create a new unique one and apply its transform.
                    print(f"Handling special source: {SCROLLING_TEXT_SOURCE_NAME}")

                    # a. Get the transform of the template text item.
                    transform_response = client.get_scene_item_transform(TEMPLATE_SCENE_NAME, item['sceneItemId'])
                    template_transform = transform_response.scene_item_transform

                    # Ensure boundsWidth and boundsHeight are at least 1.0 to prevent OBS errors
                    if template_transform['boundsWidth'] < 1.0:
                        template_transform['boundsWidth'] = 1.0
                    if template_transform['boundsHeight'] < 1.0:
                        template_transform['boundsHeight'] = 1.0

                    # b. Create the new unique input (source).
                    client.create_input(
                        sceneName=new_scene_name,
                        inputName=unique_source_name,
                        inputKind=template_source_kind,
                        inputSettings=template_source_settings,
                        sceneItemEnabled=True
                    )
                    print(f"Created unique source '{unique_source_name}' for new scene.")

                    # c. Get the ID of the newly created scene item.
                    new_item_id_response = client.get_scene_item_id(new_scene_name, unique_source_name)
                    new_item_id = new_item_id_response.scene_item_id

                    # d. Apply the saved transform to the new scene item.
                    client.set_scene_item_transform(new_scene_name, new_item_id, template_transform)
                    print(f"Applied transform from template to '{unique_source_name}'.")
                else:
                    # This is a regular item (like 'Base Layer'), just duplicate it.
                    client.duplicate_scene_item(scene_name=TEMPLATE_SCENE_NAME, item_id=item['sceneItemId'], dest_scene_name=new_scene_name)
                    print(f"Duplicated item '{item['sourceName']}' to '{new_scene_name}'.")

            # 3. Set the text content on the unique source.
            client.set_input_settings(
                name=unique_source_name,
                settings={'text': verse['obs_text']},
                overlay=True
            )
            print(f"Copied source and injected scripture text for {verse['reference']}")
    except Exception as e:
        print(f"OBS Automation Error: {e}")
    finally: # The client automatically disconnects when the 'with' block is exited, but explicit is fine.
        # The new client doesn't have a disconnect method in the same way. It's handled by context management or garbage collection.
        client.disconnect()
        print("Disconnected from OBS.")