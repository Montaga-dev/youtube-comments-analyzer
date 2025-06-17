"""
Configuration file for YouTube Comments Analyzer
Manages multiple API keys to avoid quota limits
"""

import os
from typing import List

# Multiple YouTube API Keys for rotation
# Add your API keys here to increase quota limits
YOUTUBE_API_KEYS = [
    # Add your YouTube API keys here:
    # "YOUR_FIRST_API_KEY_HERE",
    # "YOUR_SECOND_API_KEY_HERE", 
    # "YOUR_THIRD_API_KEY_HERE",
    # "YOUR_FOURTH_API_KEY_HERE",
]

# Try to load API keys from environment variable
env_api_key = os.getenv('YOUTUBE_API_KEY')
if env_api_key:
    YOUTUBE_API_KEYS.append(env_api_key)

# Filter out empty keys and placeholder text
YOUTUBE_API_KEYS = [key for key in YOUTUBE_API_KEYS if key.strip() and not key.startswith('YOUR_')]

# API Configuration
MAX_RETRIES = 3
BASE_DELAY = 1
DEFAULT_MAX_COMMENTS = 200
DEFAULT_MAX_PAGES = 3
DEFAULT_TIMEOUT = 30

def get_api_keys() -> List[str]:
    """Get list of configured API keys"""
    return YOUTUBE_API_KEYS

def add_api_key(api_key: str) -> bool:
    """Add a new API key to the configuration"""
    if api_key and api_key.strip() and api_key not in YOUTUBE_API_KEYS:
        YOUTUBE_API_KEYS.append(api_key.strip())
        return True
    return False

# Instructions for getting more API keys:
"""
HOW TO GET MORE YOUTUBE API KEYS:

1. Go to https://console.developers.google.com/
2. Create a new project (or use existing)
3. Enable "YouTube Data API v3" for the project
4. Go to "Credentials" and create an API key
5. Restrict the API key to YouTube Data API v3 (recommended)
6. Add the new API key to the YOUTUBE_API_KEYS list above

QUOTA INFORMATION:
- Each API key gets 10,000 quota units per day
- Fetching comments uses ~1 quota unit per request
- With multiple keys, you can fetch much more data
- The system automatically rotates between keys when quota is exceeded

EXAMPLE:
- 1 API key = ~10,000 comments per day
- 3 API keys = ~30,000 comments per day
- 5 API keys = ~50,000 comments per day

ENVIRONMENT VARIABLE:
You can also set your API key as an environment variable:
export YOUTUBE_API_KEY="your_api_key_here"
""" 