import requests
import os
import argparse
from obsws_python import ReqClient

from config import TEMPLATE_SCENE_NAME, TEMPLATE_SCENE_COLLECTION_NAME, SCROLLING_TEXT_SOURCE_NAME
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
    
    # 2. Get OBS Connection Details (Prefer Environment Variables)
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
    
    # 3. Get Scripture Reference (Prefer Command Line Argument)
    scripture_ref = args.ref
    if not scripture_ref:
        scripture_ref = input("\nEnter scripture reference (e.g., 1 Samuel 22:20-23): ")

    if not scripture_ref:
        print("\nScripture reference is required. Exiting.")
        return
    
    try:
        # 4. Fetch data and format
        verses = get_verses_from_api(scripture_ref)
        
        if not verses:
            print("No verses found or API fetch failed.")
            return

        print(f"\nFound {len(verses)} verses to process from {scripture_ref}.")

        original_collection_name = None
        with ReqClient(host=obs_host, port=obs_port, password=obs_password, timeout=5) as client:
            # --- Scene Collection Logic ---
            # 1. Get current scene collection to restore later
            original_collection_name = client.get_scene_collection_list().current_scene_collection_name
            print(f"Current scene collection is '{original_collection_name}'.")

            # 2. Switch to the template scene collection
            print(f"Switching to template scene collection '{TEMPLATE_SCENE_COLLECTION_NAME}'...")
            client.set_current_scene_collection(TEMPLATE_SCENE_COLLECTION_NAME)

            # 3. Automate OBS scene creation (this function now handles its own connection)
            automate_scene_generation(verses, obs_host, obs_port, obs_password)

            # 4. Create a new scene collection from the current state
            new_collection_name = f"Scripture-{scripture_ref.replace(' ', '-').replace(':', '_')}"
            print(f"Saving new scene collection as '{new_collection_name}'...")
            client.create_scene_collection(new_collection_name)
            print(f"Successfully created and switched to '{new_collection_name}'.")
        
        print("\n*** Automation Complete! ***")
        print("New scenes created/updated in OBS. Ready for image placement.")

    except ValueError as e:
        print(f"\nInput Error: {e}")
    except requests.RequestException as e:
        print(f"\nAPI Request Error: Failed to fetch scripture. Check API URL or Internet connection. {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # 5. Switch back to the original scene collection
        if original_collection_name:
            with ReqClient(host=obs_host, port=obs_port, password=obs_password, timeout=5) as client:
                print(f"\nSwitching back to original scene collection '{original_collection_name}'...")
                client.set_current_scene_collection(original_collection_name)
                print("Switched back successfully.")


if __name__ == "__main__":
    main()
