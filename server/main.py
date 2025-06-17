from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from textblob import TextBlob
import pandas as pd
import io
from ml.ml_pipeline import MLPipeline
import json
import time
import random
import logging
# Import configuration
from config import get_api_keys, MAX_RETRIES, BASE_DELAY, DEFAULT_MAX_COMMENTS, DEFAULT_MAX_PAGES, DEFAULT_TIMEOUT
# Import demo data
from demo_data import generate_demo_comments, apply_demo_sentiment

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app will run on port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="server/static"), name="static")

# Get API keys from configuration
API_KEYS = get_api_keys()

# Current API key index for rotation
current_api_key_index = 0

def get_youtube_client():
    """Get YouTube client with current API key"""
    global current_api_key_index
    if not API_KEYS:
        raise HTTPException(status_code=500, detail="No YouTube API keys configured")
    
    api_key = API_KEYS[current_api_key_index]
    return build('youtube', 'v3', developerKey=api_key)

def rotate_api_key():
    """Rotate to next API key"""
    global current_api_key_index
    if len(API_KEYS) > 1:
        current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
        logger.info(f"Rotated to API key {current_api_key_index + 1}/{len(API_KEYS)}")
        return True
    return False

def is_quota_exceeded_error(error):
    """Check if error is due to quota exceeded"""
    if hasattr(error, 'resp') and hasattr(error.resp, 'status'):
        if error.resp.status == 403:
            error_details = str(error)
            return any(keyword in error_details.lower() for keyword in [
                'quota', 'quotaexceeded', 'dailylimitexceeded', 'usagelimitexceeded'
            ])
    return False

def exponential_backoff_retry(func, max_retries=MAX_RETRIES, base_delay=BASE_DELAY):
    """Execute function with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as e:
            if is_quota_exceeded_error(e):
                logger.warning(f"Quota exceeded on attempt {attempt + 1}")
                if rotate_api_key():
                    logger.info("Trying with rotated API key")
                    continue
                else:
                    logger.error("No more API keys to rotate - falling back to demo data")
                    raise HTTPException(
                        status_code=429, 
                        detail="QUOTA_EXCEEDED"  # Special code for demo fallback
                    )
            elif attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"API error after {max_retries} attempts: {str(e)}")
                raise HTTPException(status_code=500, detail=f"YouTube API error: {str(e)}")
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"Retrying in {delay:.2f} seconds due to error: {str(e)}")
                time.sleep(delay)
            else:
                raise e
    
    raise HTTPException(status_code=500, detail="Max retries exceeded")

# Initialize ML pipeline
ml_pipeline = MLPipeline()

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

def get_video_comments_raw(video_id: str, max_comments: int = 500, max_pages: int = 5, timeout_seconds: int = 30) -> tuple[List[Dict[str, str]], Dict[str, int]]:
    """Fetch comments without sentiment analysis - just raw comments"""
    comments_raw = []
    stats = {
        "total_comments": 0,
        "pages_processed": 0,
        "max_comments_reached": False,
        "max_pages_reached": False,
        "timeout_reached": False,
        "api_key_used": current_api_key_index + 1,
        "total_api_keys": len(API_KEYS)
    }
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting to fetch RAW comments for video ID: {video_id} (max: {max_comments} comments, {max_pages} pages, timeout: {timeout_seconds}s)")
        logger.info(f"Using API key {current_api_key_index + 1}/{len(API_KEYS)}")
        
        def fetch_first_page():
            youtube = get_youtube_client()
            return youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=min(100, max_comments)  # Don't fetch more than needed
            ).execute()
        
        response = exponential_backoff_retry(fetch_first_page)

        while True:
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                logger.info(f"Reached timeout limit ({timeout_seconds}s)")
                stats["timeout_reached"] = True
                break
                
            stats["pages_processed"] += 1
            logger.info(f"Processing page {stats['pages_processed']}/{max_pages}")
            
            # Check if we've reached the maximum number of pages
            if stats["pages_processed"] > max_pages:
                logger.info(f"Reached maximum pages limit ({max_pages})")
                stats["max_pages_reached"] = True
                break
            
            for item in response['items']:
                try:
                    # Check if we've reached the maximum number of comments
                    if stats["total_comments"] >= max_comments:
                        logger.info(f"Reached maximum comments limit ({max_comments})")
                        stats["max_comments_reached"] = True
                        break
                        
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    comments_raw.append({
                        "comment": comment['textDisplay'],
                        "sentiment": "Not analyzed",  # Will be filled later
                        "timestamp": comment['publishedAt'],
                        "author": comment['authorDisplayName'],
                        "likes": str(comment.get('likeCount', 0))
                    })
                    stats["total_comments"] += 1
                except Exception as e:
                    logger.warning(f"Error processing comment: {str(e)}")
                    continue
            
            # Break if we've reached max comments
            if stats["max_comments_reached"]:
                break

            # Check if there are more comments to fetch
            if 'nextPageToken' not in response:
                logger.info("No more pages to fetch")
                break

            # Fetch next page of comments with retry logic
            def fetch_next_page():
                youtube = get_youtube_client()
                return youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=min(100, max_comments - stats["total_comments"]),
                    pageToken=response['nextPageToken']
                ).execute()
            
            try:
                response = exponential_backoff_retry(fetch_next_page)
            except HTTPException as e:
                logger.error(f"Failed to fetch next page: {str(e)}")
                # Return what we have so far instead of failing completely
                break

        logger.info(f"Finished fetching RAW comments. Total: {stats['total_comments']}")
        return comments_raw, stats
    except HTTPException:
        # Re-raise HTTP exceptions (like quota exceeded)
        raise
    except Exception as e:
        logger.error(f"Critical error in get_video_comments_raw: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

def get_video_comments(video_id: str, max_comments: int = 1000, max_pages: int = 10, timeout_seconds: int = 60) -> tuple[List[Dict[str, str]], Dict[str, int]]:
    comments_with_sentiment = []
    stats = {
        "total_comments": 0,
        "pages_processed": 0,
        "max_comments_reached": False,
        "max_pages_reached": False,
        "timeout_reached": False,
        "api_key_used": current_api_key_index + 1,
        "total_api_keys": len(API_KEYS)
    }
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting to fetch comments for video ID: {video_id} (max: {max_comments} comments, {max_pages} pages, timeout: {timeout_seconds}s)")
        logger.info(f"Using API key {current_api_key_index + 1}/{len(API_KEYS)}")
        
        def fetch_first_page():
            youtube = get_youtube_client()
            return youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=min(100, max_comments)
            ).execute()
        
        response = exponential_backoff_retry(fetch_first_page)

        while True:
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                logger.info(f"Reached timeout limit ({timeout_seconds}s)")
                stats["timeout_reached"] = True
                break
                
            stats["pages_processed"] += 1
            logger.info(f"Processing page {stats['pages_processed']}/{max_pages}")
            
            # Check if we've reached the maximum number of pages
            if stats["pages_processed"] > max_pages:
                logger.info(f"Reached maximum pages limit ({max_pages})")
                stats["max_pages_reached"] = True
                break
            
            for item in response['items']:
                try:
                    # Check if we've reached the maximum number of comments
                    if stats["total_comments"] >= max_comments:
                        logger.info(f"Reached maximum comments limit ({max_comments})")
                        stats["max_comments_reached"] = True
                        break
                        
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
                    logger.warning(f"Error processing comment: {str(e)}")
                    continue
            
            # Break if we've reached max comments
            if stats["max_comments_reached"]:
                break

            # Check if there are more comments to fetch
            if 'nextPageToken' not in response:
                logger.info("No more pages to fetch")
                break

            # Fetch next page of comments with retry logic
            def fetch_next_page():
                youtube = get_youtube_client()
                return youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=min(100, max_comments - stats["total_comments"]),
                    pageToken=response['nextPageToken']
                ).execute()
            
            try:
                response = exponential_backoff_retry(fetch_next_page)
            except HTTPException as e:
                logger.error(f"Failed to fetch next page: {str(e)}")
                # Return what we have so far instead of failing completely
                break

        logger.info(f"Finished fetching comments. Total: {stats['total_comments']}")
        return comments_with_sentiment, stats
    except HTTPException:
        # Re-raise HTTP exceptions (like quota exceeded)
        raise
    except Exception as e:
        logger.error(f"Critical error in get_video_comments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

@app.get("/api/status")
async def get_api_status():
    """Get current API status and quota information"""
    return {
        "api_keys_configured": len(API_KEYS),
        "current_api_key": current_api_key_index + 1,
        "status": "operational" if API_KEYS else "no_api_keys",
        "demo_available": True,
        "quota_management": "enabled" if len(API_KEYS) > 1 else "single_key"
    }

@app.get("/demo/comments")
async def get_demo_comments(video_id: str = "dQw4w9WgXcQ", max_comments: int = 20, category: str = "tech"):
    """Get demo comments for testing purposes"""
    try:
        comments, stats = generate_demo_comments(video_id, max_comments, category)
        comments = apply_demo_sentiment(comments, category)
        return CommentResponse(comments=comments, stats=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate demo comments: {str(e)}")

@app.get("/comments/raw", response_model=CommentResponse)
async def fetch_comments_raw(url: str, max_comments: int = 200, max_pages: int = 3, use_demo: bool = False):
    """Fetch comments without sentiment analysis - faster and safer"""
    try:
        video_id = get_video_id(url)
        
        # If demo mode is requested or if we want to test
        if use_demo:
            logger.info("Using demo data as requested")
            comments, stats = generate_demo_comments(video_id, max_comments, "tech")
            return CommentResponse(comments=comments, stats=stats)
        
        try:
            comments, stats = get_video_comments_raw(video_id, max_comments, max_pages, timeout_seconds=60)
            return CommentResponse(comments=comments, stats=stats)
        except HTTPException as e:
            if e.status_code == 429 and e.detail == "QUOTA_EXCEEDED":
                logger.warning("API quota exceeded, falling back to demo data")
                comments, stats = generate_demo_comments(video_id, max_comments, "tech")
                # Add warning message to stats
                stats["warning"] = "YouTube API quota exceeded. Showing demo data instead."
                stats["demo_fallback"] = True
                return CommentResponse(comments=comments, stats=stats)
            else:
                raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        # As last resort, provide demo data
        try:
            video_id = get_video_id(url)
            comments, stats = generate_demo_comments(video_id, max_comments, "tech")
            stats["warning"] = f"Error occurred: {str(e)}. Showing demo data instead."
            stats["error_fallback"] = True
            return CommentResponse(comments=comments, stats=stats)
        except:
            raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

@app.get("/comments", response_model=CommentResponse)
async def fetch_comments(url: str, max_comments: int = 500, max_pages: int = 5):
    """Fetch comments with TextBlob sentiment analysis (legacy endpoint)"""
    try:
        video_id = get_video_id(url)
        comments, stats = get_video_comments(video_id, max_comments, max_pages)
        return CommentResponse(comments=comments, stats=stats)
    except HTTPException as e:
        raise e
    except Exception as e:
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

# ML-related models
class MLAnalysisRequest(BaseModel):
    texts: List[str]
    use_transformer: bool = False
    model_name: Optional[str] = None
    
    class Config:
        protected_namespaces = ()

class SentimentAnalysisRequest(BaseModel):
    comments: List[Dict[str, str]]  # Raw comments to analyze
    method: str = "textblob"  # "textblob" or "transformer"
    model_name: Optional[str] = None  # Required if method is "transformer"
    
    class Config:
        protected_namespaces = ()

# ML-related endpoints
@app.post("/ml/analyze")
async def analyze_comments_ml(request: MLAnalysisRequest):
    try:
        results = ml_pipeline.analyze_texts(request.texts, request.use_transformer, request.model_name)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML analysis failed: {str(e)}")

@app.get("/ml/models")
async def get_available_models():
    """Get list of available transformer models."""
    try:
        available_models = list(ml_pipeline.classifier.models.keys())
        return {"models": available_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@app.post("/analyze_sentiment")
async def analyze_sentiment_endpoint(request: SentimentAnalysisRequest):
    """Analyze sentiment of already fetched comments"""
    try:
        analyzed_comments = []
        
        for comment_data in request.comments:
            comment_text = comment_data.get("comment", "")
            
            if request.method == "textblob":
                # Use TextBlob for sentiment analysis
                sentiment = analyze_sentiment(comment_text)
                confidence = abs(TextBlob(comment_text).sentiment.polarity)
                method_used = "textblob"
            elif request.method == "transformer":
                # Use transformer model
                if not request.model_name:
                    raise HTTPException(status_code=400, detail="model_name is required for transformer method")
                
                result = ml_pipeline.classifier.predict_with_transformer(comment_text, request.model_name)
                sentiment = result["sentiment"].title()  # Convert to Title case to match TextBlob format
                confidence = result["confidence"]
                method_used = f"transformer_{request.model_name}"
            else:
                raise HTTPException(status_code=400, detail="Invalid method. Use 'textblob' or 'transformer'")
            
            # Update the comment with sentiment analysis
            analyzed_comment = comment_data.copy()
            analyzed_comment["sentiment"] = sentiment
            analyzed_comment["confidence"] = confidence
            analyzed_comment["method"] = method_used
            analyzed_comments.append(analyzed_comment)
        
        # Calculate stats
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for comment in analyzed_comments:
            sentiment_counts[comment["sentiment"]] += 1
        
        return {
            "comments": analyzed_comments,
            "stats": {
                "total_comments": len(analyzed_comments),
                "sentiment_distribution": sentiment_counts,
                "method_used": request.method,
                "model_name": request.model_name if request.method == "transformer" else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 