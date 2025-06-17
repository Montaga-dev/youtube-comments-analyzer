# YouTube API Setup Guide - Solving Quota Issues

## Problem
Your YouTube Comments Analyzer is hitting API quota limits, causing the "quota exceeded" error. This happens because each YouTube API key has a daily limit of 10,000 quota units.

## Solution
Set up multiple YouTube API keys to increase your daily quota limit and enable automatic key rotation.

## Step-by-Step Guide

### 1. Create Additional Google Cloud Projects

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown (top left)
3. Click "New Project"
4. Give it a name like "YouTube Analyzer 2"
5. Click "Create"
6. Repeat this process to create 2-3 more projects

### 2. Enable YouTube Data API v3 for Each Project

For each project you created:

1. Select the project from the dropdown
2. Go to "APIs & Services" > "Library"
3. Search for "YouTube Data API v3"
4. Click on it and press "Enable"

### 3. Create API Keys for Each Project

For each project:

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key
4. (Optional but recommended) Click "Restrict Key":
   - Under "API restrictions", select "Restrict key"
   - Choose "YouTube Data API v3"
   - Click "Save"

### 4. Add API Keys to Your Configuration

Open `server/config.py` and add your new API keys:

```python
YOUTUBE_API_KEYS = [
    "AIzaSyCYQ9a0lhLLhVLXJFyw8pVsuHBk7Wpd_7o",  # Primary key
    "YOUR_SECOND_API_KEY_HERE",                    # Add your second key
    "YOUR_THIRD_API_KEY_HERE",                     # Add your third key
    "YOUR_FOURTH_API_KEY_HERE",                    # Add your fourth key
]
```

### 5. Restart Your Server

```bash
cd server
python main.py
```

## Quota Information

- **1 API key** = ~10,000 comments per day
- **3 API keys** = ~30,000 comments per day  
- **5 API keys** = ~50,000 comments per day

## How It Works

The system automatically:
1. Uses the first API key until quota is exceeded
2. Rotates to the next available key
3. Continues until all keys are exhausted
4. Falls back to demo data if all keys are exhausted

## Verification

After setup, check the API status in your app:
- You should see "X key(s) configured" 
- "Quota rotation enabled" should appear
- The system will show which key is currently active

## Alternative Solutions

If you can't create multiple API keys:

1. **Use Demo Mode**: Click "Try Demo" to see sample data
2. **Wait for Reset**: Quotas reset daily at midnight Pacific Time
3. **Optimize Usage**: Reduce `max_comments` and `max_pages` parameters

## Troubleshooting

### "API key not valid" Error
- Make sure YouTube Data API v3 is enabled for the project
- Check that the API key is copied correctly (no extra spaces)

### Still Getting Quota Errors
- Verify all API keys are added to `config.py`
- Restart the server after adding keys
- Check the API status endpoint: `http://localhost:8000/api/status`

### Demo Mode Not Working
- Make sure the server is running
- Check server logs for any errors
- Try the demo endpoint directly: `http://localhost:8000/demo/comments`

## Cost Information

YouTube Data API v3 is **free** up to the quota limits. You won't be charged for normal usage within the free tier limits.

## Security Best Practices

1. **Restrict API Keys**: Limit each key to only YouTube Data API v3
2. **Don't Share Keys**: Keep your API keys private
3. **Use Environment Variables**: Consider using `.env` files for production
4. **Monitor Usage**: Check your quota usage in Google Cloud Console

## Need Help?

If you're still experiencing issues:
1. Check the server logs for detailed error messages
2. Verify your API keys in Google Cloud Console
3. Test with the demo mode first
4. Make sure all dependencies are installed

The system is designed to be resilient - it will automatically fall back to demo data if API issues occur, so your application will continue to work even during quota problems. 