# Discord InterDiffusion Bot

A Python Discord Bot using Discord.py to generate images with AnyAI's new InterDiffusion-4.0 model!

## Features

- Easy to set up and run
- Cache system to prevent spam
- Simple & Custom rate limiting system, also to prevent spam.
- Regenerate and Delete buttons.
- Customize seed, negative / positive prompt, and steps.

## Prerequisites

- Python 3.6 or higher
- `discord.py` library
- `requests` library

## Setup

1. Install the required libraries: pip install -r requirements.txt
2. Open `main.py` and fill in the following variables:
- `server_id`: The ID of the server you want to clone.
- `bot_token`: Your Discord bot token.
- `proxy` (optional): Proxy server URL if needed.

## Usage

1. Run the script: python main.py

## License

This project is licensed under the [MIT License](LICENSE).
