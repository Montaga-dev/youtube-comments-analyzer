"""
Demo data for YouTube Comments Analyzer
Used when API quota is exceeded or for testing purposes
"""

import random
from datetime import datetime, timedelta

# Sample comments for different video types
DEMO_COMMENTS = {
    "tech": [
        "This is amazing! The future of AI is here 🤖",
        "Great explanation, finally understood this concept",
        "Can you make a tutorial on this?",
        "This changed my perspective completely",
        "Wow, I never thought about it this way",
        "Thanks for sharing this knowledge!",
        "Mind blown! 🤯",
        "This is exactly what I was looking for",
        "Incredible work, keep it up!",
        "Very informative and well presented",
        "I disagree with some points but overall good",
        "Could you explain the technical details more?",
        "This is too complicated for beginners",
        "Love your content, subscribed!",
        "When will you release the next part?",
        "This doesn't work for me, any suggestions?",
        "Perfect timing, I needed this for my project",
        "Your videos are always so helpful",
        "Can you cover more advanced topics?",
        "This is revolutionary technology!"
    ],
    "entertainment": [
        "LMAO this is hilarious 😂",
        "I can't stop watching this!",
        "This made my day better",
        "So funny, shared with all my friends",
        "I'm crying from laughing so hard",
        "This is pure gold!",
        "Best video I've seen all week",
        "You're so talented!",
        "This deserves more views",
        "I've watched this 10 times already",
        "This is not funny at all",
        "Meh, could be better",
        "I don't get the joke",
        "This is amazing content!",
        "Please make more like this",
        "This is so creative!",
        "I love your sense of humor",
        "This brightened my day",
        "Absolutely brilliant!",
        "This is why I love YouTube"
    ],
    "educational": [
        "Thank you for this clear explanation",
        "This helped me pass my exam!",
        "Finally someone who explains it properly",
        "Very well structured lesson",
        "I wish my teacher explained like this",
        "This is better than my textbook",
        "Great examples and illustrations",
        "Could you add more practice problems?",
        "This is exactly what I needed to learn",
        "Your teaching style is excellent",
        "I'm confused about the second part",
        "Can you make a video about related topics?",
        "This is too fast for me to follow",
        "Perfect pace and explanation",
        "I learned more in 10 minutes than in class",
        "This should be shown in schools",
        "Very comprehensive coverage",
        "Thanks for making learning fun!",
        "This concept is now crystal clear",
        "Excellent educational content"
    ]
}

def generate_demo_comments(video_id: str, max_comments: int = 50, category: str = "tech") -> tuple[list, dict]:
    """
    Generate demo comments when API quota is exceeded
    
    Args:
        video_id: YouTube video ID
        max_comments: Maximum number of comments to generate
        category: Category of comments (tech, entertainment, educational)
    
    Returns:
        Tuple of (comments_list, stats_dict)
    """
    
    # Select comment pool based on category
    if category not in DEMO_COMMENTS:
        category = "tech"
    
    comment_pool = DEMO_COMMENTS[category]
    
    # Generate random comments
    comments = []
    authors = [f"User{i:03d}" for i in range(1, 101)]
    
    for i in range(min(max_comments, len(comment_pool))):
        # Random timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        comment = {
            "comment": random.choice(comment_pool),
            "sentiment": "Not analyzed",
            "timestamp": timestamp.isoformat() + "Z",
            "author": random.choice(authors),
            "likes": str(random.randint(0, 100))
        }
        comments.append(comment)
    
    # Generate stats
    stats = {
        "total_comments": len(comments),
        "pages_processed": 1,
        "max_comments_reached": len(comments) >= max_comments,
        "max_pages_reached": False,
        "timeout_reached": False,
        "api_key_used": "DEMO_MODE",
        "total_api_keys": "DEMO_MODE",
        "demo_mode": True,
        "demo_category": category
    }
    
    return comments, stats

def get_demo_video_info(video_id: str) -> dict:
    """Get demo video information"""
    return {
        "video_id": video_id,
        "title": f"Demo Video {video_id[:8]}",
        "description": "This is demo data used when YouTube API quota is exceeded",
        "view_count": random.randint(1000, 1000000),
        "like_count": random.randint(10, 10000),
        "comment_count": random.randint(50, 500)
    }

# Sentiment distribution for demo comments
DEMO_SENTIMENT_DISTRIBUTION = {
    "tech": {"Positive": 0.6, "Neutral": 0.3, "Negative": 0.1},
    "entertainment": {"Positive": 0.8, "Neutral": 0.15, "Negative": 0.05},
    "educational": {"Positive": 0.7, "Neutral": 0.25, "Negative": 0.05}
}

def apply_demo_sentiment(comments: list, category: str = "tech") -> list:
    """Apply sentiment analysis to demo comments based on category distribution"""
    if category not in DEMO_SENTIMENT_DISTRIBUTION:
        category = "tech"
    
    distribution = DEMO_SENTIMENT_DISTRIBUTION[category]
    sentiments = []
    
    # Create sentiment list based on distribution
    for sentiment, ratio in distribution.items():
        count = int(len(comments) * ratio)
        sentiments.extend([sentiment] * count)
    
    # Fill remaining with positive sentiment
    while len(sentiments) < len(comments):
        sentiments.append("Positive")
    
    # Shuffle sentiments
    random.shuffle(sentiments)
    
    # Apply sentiments to comments
    for i, comment in enumerate(comments):
        if i < len(sentiments):
            comment["sentiment"] = sentiments[i]
        else:
            comment["sentiment"] = "Positive"
    
    return comments 