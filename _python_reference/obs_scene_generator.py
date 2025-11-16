import requests
import os
import time
import argparse
from obsws_python import ReqClient

from config import TEMPLATE_SCENE_NAME, SCROLLING_TEXT_SOURCE_NAME
from bible_utils import get_verses_from_api
from obs_automator import automate_scene_generation

# --- MAIN EXECUTION ---

def main():
    # 1. Setup Argument Parser
    parser = argparse.ArgumentParser(
        description="Automate OBS scene generation by fetching scripture text via API and injecting it into scene templates.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--ref',
        type=str,
        help="The scripture reference range (e.g., '1 Samuel 22:20-23')."
    )
    args = parser.parse_args()

    print("--- OBS SCENE GENERATOR (BSB) ---")
    print(f"Template Scene: {TEMPLATE_SCENE_NAME}")
    print(f"Text Source Name: {SCROLLING_TEXT_SOURCE_NAME}")
    
    # --- Get Scripture Reference (Required for both stages) ---
    scripture_ref = args.ref
    if not scripture_ref:
        scripture_ref = input("\nEnter scripture reference (e.g., 1 Samuel 22:20-23): ")

    if not scripture_ref:
        print("\nScripture reference is required. Exiting.")
        return

    # Get OBS Connection Details (Prefer Environment Variables)
    obs_host = os.environ.get('OBS_HOST', 'localhost')
    obs_port = int(os.environ.get('OBS_PORT', 4455))
    obs_password = os.environ.get('OBS_PASSWORD', '')

    # If environment variables are set, skip prompts for OBS connection
    if obs_password:
        print(f"Using credentials from environment variables (Host: {obs_host}, Port: {obs_port}).")
    else:
        # Prompt for details if environment variables are missing
        print("\nOBS connection details not found in environment variables. Prompting now:")
        obs_host = input(f"Enter OBS Host (default: {obs_host}): ") or obs_host
        try:
            obs_port = int(input(f"Enter OBS Port (default: {obs_port}): ") or obs_port)
        except ValueError:
            print("Invalid port, using default 4455.")
            obs_port = 4455
        obs_password = input("Enter OBS WebSocket Password (or leave blank): ")
    
    try:
        verses = get_verses_from_api(scripture_ref)
        
        if not verses:
            print("No verses found or API fetch failed.")
            return

        print(f"\nFound {len(verses)} verses to process from {scripture_ref}.")

        # --- Connection and Scene Generation with Retries ---
        max_retries = 5
        retry_delay = 5 # seconds
        for attempt in range(max_retries):
            try:
                print(f"\nAttempting to connect to OBS... ({attempt + 1}/{max_retries})")
                with ReqClient(host=obs_host, port=obs_port, password=obs_password, timeout=10) as client:
                    print("Successfully connected to OBS.")
                    current_collection = client.get_scene_collection_list().current_scene_collection_name
                    print(f"Operating on current scene collection: '{current_collection}'")

                    # 1. Validate that the template scene and source exist
                    print(f"Validating template scene '{TEMPLATE_SCENE_NAME}'...")
                    scenes = client.get_scene_list().scenes
                    if not any(s['sceneName'] == TEMPLATE_SCENE_NAME for s in scenes):
                        print(f"\nERROR: Template scene '{TEMPLATE_SCENE_NAME}' not found in the current scene collection.")
                        print("Please make sure you are in the correct scene collection and the template scene exists.")
                        return

                    print(f"Validating text source '{SCROLLING_TEXT_SOURCE_NAME}' in template scene...")
                    scene_items = client.get_scene_item_list(TEMPLATE_SCENE_NAME).scene_items
                    if not any(item['sourceName'] == SCROLLING_TEXT_SOURCE_NAME for item in scene_items):
                        print(f"\nERROR: Text source '{SCROLLING_TEXT_SOURCE_NAME}' not found in the '{TEMPLATE_SCENE_NAME}' scene.")
                        print("Please add a text source with this name to your template scene.")
                        return
                    print("Validation successful.")

                    # 2. Automate OBS scene creation within the current collection.
                    automate_scene_generation(client, verses)

                # If we get here, everything was successful.
                break

            except ConnectionRefusedError as e:
                if attempt < max_retries - 1:
                    print(f"Connection refused. OBS WebSocket may not be ready. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("\nConnection failed after multiple retries. Please ensure OBS is running and the WebSocket server is enabled.")
                    raise e
        
        print("\n*** Automation Complete! ***")
        print("Scripture scenes have been added to your current OBS scene collection.")
        print("If you modified a template, you may want to clean it up for the next run.")

    except ValueError as e:
        print(f"\nInput Error: {e}")
    except requests.RequestException as e:
        print(f"\nAPI Request Error: Failed to fetch scripture. Check API URL or Internet connection. {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
