# OBS Scripture & Image Scene Generator

[![Go CI](https://github.com/jeffreybradley1963/dbs-initiator/actions/workflows/go-ci.yml/badge.svg)](https://github.com/jeffreybradley1963/dbs-initiator/actions/workflows/go-ci.yml)

A Go application to automatically generate scenes in OBS Studio for displaying scripture verses and AI-generated illustrative images.

This tool is designed for streamers, content creators, and church media teams who want to quickly create a series of OBS scenes from a scripture passage. It creates a text-based scene for each verse and then uses Google's Gemini AI to analyze the passage, generate relevant image prompts, and create corresponding image-based scenes.

## Features

- **Automated Scene Creation**: Generates a new OBS scene for each verse in a given scripture reference.
- **AI-Powered Image Generation**: Analyzes scripture text to generate relevant, artistic images for key themes.
- **Template-Based**: Uses pre-configured template scenes in OBS for both text and images to ensure a consistent look and feel.
- **Independent Sources**: Each generated scene gets its own unique text or image source, so you can edit one without affecting others.
- **Full Scene Replication**: Copies all elements from your template scenes (backgrounds, overlays, cameras, etc.) into each new scene.

## Prerequisites

1.  **Go 1.23+** (only required if you are building from source).
2.  **OBS Studio 28+**: The application relies on API features available in modern versions of OBS.
3.  **OBS WebSocket Plugin**: You must have the `obs-websocket` plugin installed and enabled in OBS. This is included by default in OBS Studio 28 and later.
    - Ensure the WebSocket server is enabled by going to **Tools -> WebSocket Server Settings** in OBS and checking **Enable WebSocket Server**.
4.  **Google Gemini API Key**: You need an API key to use the AI image generation features. You can get one from Google AI Studio.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jeffreybradley1963/dbs-initiator.git
cd dbs-initiator
