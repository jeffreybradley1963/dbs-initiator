# OBS Scripture Scene Generator

A Python script to automatically generate scenes in OBS Studio for displaying scripture verses, fetched from a public Bible API.

This tool is designed for streamers, content creators, and church media teams who want to quickly create a series of OBS scenes from a scripture passage, with each verse in its own scene, based on a master template.

## Features

- **Automated Scene Creation**: Generates a new OBS scene for each verse in a given scripture reference.
- **Template-Based**: Uses a pre-configured template scene in OBS to ensure a consistent look and feel.
- **Independent Sources**: Each generated scene gets its own unique text source, so you can edit one verse's text without affecting others.
- **Full Scene Duplication**: Copies all elements from your template scene (backgrounds, overlays, cameras, etc.) into each new scene.
- **Preserves Layout**: The position, transform, and styling of the template's text source are applied to each new scene's text source.

## Prerequisites

1.  **Python 3.7+**
2.  **OBS Studio 28+**: The script relies on API features available in modern versions of OBS.
3.  **OBS WebSocket Plugin**: You must have the `obs-websocket` plugin installed and enabled in OBS. This is included by default in OBS Studio 28 and later.
    - Ensure the WebSocket server is enabled by going to **Tools -> WebSocket Server Settings** in OBS.

## Setup

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone <your-repository-url>
cd <your-repository-directory>
```

### 2. Install Dependencies

It is highly recommended to use a Python virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Configure OBS Studio

The script requires a specific setup in OBS to function correctly.

1.  **Enable WebSocket Server**:
    - In OBS, go to **Tools -> WebSocket Server Settings**.
    - Check **Enable WebSocket Server**.
    - Note the **Server Port** (default is `4455`).
    - It is strongly recommended to set a **Server Password** for security.

2.  **Create a Template Scene Collection**:
    - In OBS, go to **Scene Collection -> New**.
    - Name this collection something like `My-Study-Template`.

3.  **Create a Template Scene**:
    - Within your new template collection, create a new scene.
    - Name it `Scripture-Template`. This name must match the `TEMPLATE_SCENE_NAME` variable in the script.

4.  **Design Your Template Scene**:
    - Add all the sources you want to be present in every scripture scene (e.g., background images, video loops, camera sources, overlays).
    - Add a **Text (FreeType 2)** source. This will be the template for the scripture text.
    - Name this text source `sTextScrolling`. This name must match the `SCROLLING_TEXT_SOURCE_NAME` variable in the script.
    - Position, scale, and style this text source exactly as you want the scripture text to appear. The content of the text source itself does not matter, as the script will overwrite it.

!OBS Template Setup <!-- Optional: Add a screenshot of your OBS setup -->

### 4. Configure the Script

Open `config.py` and review the configuration constants at the top of the file.

```python
# ID of the scene you have already created in OBS that will be duplicated.
TEMPLATE_SCENE_NAME = "Scripture-Template"

# Use the name you gave the scrolling text source
SCROLLING_TEXT_SOURCE_NAME = "sTextScrolling"
```

Make sure these names exactly match the names you used in OBS.

## Usage

The script requires your OBS WebSocket connection details and the scripture reference you want to generate.

### Connection Details

It's recommended to set your OBS connection details as environment variables so you don't have to enter them every time.

**On Windows (Command Prompt):**
```cmd
set OBS_HOST=localhost
set OBS_PORT=4455
set OBS_PASSWORD=your_password
```

**On macOS/Linux:**
```bash
export OBS_HOST=localhost
export OBS_PORT=4455
export OBS_PASSWORD='your_password'
```

If you don't set these, the script will prompt you for them.

### Running the Script

Run the script from your terminal, passing the scripture reference using the `--ref` argument.

```bash
python obs_scene_generator.py --ref "John 3:16-18"
```

If you don't provide the `--ref` argument, the script will prompt you to enter it.

### What Happens

When you run the script, it will:
1. Connect to OBS.
2. Switch to your `TEMPLATE_SCENE_COLLECTION_NAME`.
3. For each verse in the reference, it creates a new scene, duplicates all items from `TEMPLATE_SCENE_NAME`, creates a unique text source, and injects the formatted scripture text.
4. Create a new scene collection named after the scripture reference (e.g., `Scripture-John-3_16-18`).
5. Switch back to the scene collection you were using before you ran the script.

Your OBS is left untouched, and a new, fully prepared scene collection is ready for you to use for your stream or recording.

## Troubleshooting

- **Connection Error**: Make sure OBS is running, the WebSocket server is enabled, and your host, port, and password are correct.
- **Template Scene/Collection Not Found**: Double-check that the names in the script's configuration section exactly match the names in OBS.
- **Text Source Not Found**: Ensure the text source in your template scene is named correctly and matches the `SCROLLING_TEXT_SOURCE_NAME` in the script.
- **Permission Denied Errors**: If you see errors related to file caches (like `.egg-cache`), ensure the user running the script has write permissions to the relevant directories.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
