from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import re
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from textblob import TextBlob
import pandas as pd
import io

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app will run on port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

class CommentResponse(BaseModel):
    comments: List[Dict[str, str]]
    stats: Dict[str, int]

def get_video_id(url: str) -> str:
    # Handle different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([a-zA-Z0-9_-]{11})',  # Standard format
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',  # Short URL format
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})'  # Embed format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")

def analyze_sentiment(comment: str) -> str:
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity == 0:
        return "Neutral"
    else:
        return "Negative"

def get_video_comments(video_id: str) -> tuple[List[Dict[str, str]], Dict[str, int]]:
    comments_with_sentiment = []
    stats = {
        "total_comments": 0,
        "pages_processed": 0
    }
    
    try:
        print(f"Starting to fetch comments for video ID: {video_id}")
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100  # Maximum allowed by YouTube API per page
        ).execute()

        while True:
            stats["pages_processed"] += 1
            print(f"Processing page {stats['pages_processed']}")
            
            for item in response['items']:
                try:
                    comment = item['snippet']['topLevelComment']['snippet']
                    sentiment = analyze_sentiment(comment['textDisplay'])
                    
                    comments_with_sentiment.append({
                        "comment": comment['textDisplay'],
                        "sentiment": sentiment,
                        "timestamp": comment['publishedAt'],
                        "author": comment['authorDisplayName'],
                        "likes": str(comment.get('likeCount', 0))  # Convert likes to string
                    })
                    stats["total_comments"] += 1
                except Exception as e:
                    print(f"Error processing comment: {str(e)}")
                    continue

            # Check if there are more comments to fetch
            if 'nextPageToken' not in response:
                print("No more pages to fetch")
                break

            # Fetch next page of comments
            try:
                response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=100,
                    pageToken=response['nextPageToken']
                ).execute()
            except Exception as e:
                print(f"Error fetching next page: {str(e)}")
                # If we hit API limits or other issues, return what we have so far
                break

        print(f"Finished fetching comments. Total: {stats['total_comments']}")
        return comments_with_sentiment, stats
    except Exception as e:
        print(f"Critical error in get_video_comments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

@app.get("/comments", response_model=CommentResponse)
async def fetch_comments(url: str):
    try:
        print(f"Received request for URL: {url}")
        video_id = get_video_id(url)
        print(f"Extracted video ID: {video_id}")
        comments, stats = get_video_comments(video_id)
        return CommentResponse(comments=comments, stats=stats)
    except HTTPException as e:
        print(f"HTTP Exception: {str(e)}")
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

@app.get("/download_csv")
async def download_comments_csv(url: str):
    try:
        video_id = get_video_id(url)
        comments, _ = get_video_comments(video_id)
        
        # Create DataFrame and exclude timestamp column
        df = pd.DataFrame(comments)
        df = df.drop('timestamp', axis=1)  # Remove timestamp column
        
        # Create in-memory buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        # Return CSV file
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=youtube_comments_{video_id}.csv"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate CSV") 
