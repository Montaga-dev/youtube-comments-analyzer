# YouTube Comments Sentiment Analyzer

A modern full-stack application for collecting, analyzing, and understanding YouTube comment sentiments. Built with FastAPI, React, and machine learning capabilities.

![YouTube Sentiment Analysis](https://your-screenshot-url.png)

## 🎯 Purpose

This tool serves two main purposes:
1. **Comment Analysis Tool**: Fetch and analyze YouTube video comments with sentiment classification
2. **ML Research Platform**: Collect labeled data for training custom sentiment analysis models

## 🌟 Features

### Application Features
- Modern, responsive UI with video background
- Real-time sentiment analysis of YouTube comments
- CSV export functionality
- Interactive data visualization
- Error handling and loading states
- Accessible and keyboard-friendly interface

### Data Science Features
- Automated data collection pipeline
- Sentiment labeling (Positive, Neutral, Negative)
- Structured data export for ML training
- Basic sentiment analysis using TextBlob
- Extensible architecture for custom ML models

## 🛠 Tech Stack

### Backend
- FastAPI (Python web framework)
- TextBlob (Natural Language Processing)
- YouTube Data API v3
- Pandas (Data manipulation)

### Frontend
- React.js
- Tailwind CSS
- Heroicons
- Modern animations and transitions

## 📊 Data Science Applications

### 1. Data Collection
- Automated comment fetching
- Structured data storage
- Metadata preservation
- Time-based analysis support

### 2. Sentiment Analysis
```python
{
    "comment_text": "This video was amazing!",
    "sentiment": "Positive",
    "confidence_score": 0.89,
    "video_id": "abc123",
    "timestamp": "2024-02-20T10:30:00Z"
}
```

### 3. Research Applications
- Social media sentiment analysis
- User engagement studies
- Content effectiveness research
- Brand sentiment tracking

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- YouTube Data API key
- Git

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/youtube-sentiment-analyzer.git
   cd youtube-sentiment-analyzer
   ```

2. **Set up Python environment:**
   ```bash
   cd server
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   Create `.env` file in server directory:
   ```env
   YOUTUBE_API_KEY=your_api_key_here
   ```

5. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd client
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

## 💻 Usage

### Basic Usage
1. Open http://localhost:3000
2. Paste a YouTube video URL
3. Click "Fetch Comments"
4. View sentiment analysis results
5. Download data as CSV

### Data Collection
```python
# Example of collected data structure
{
    "video_id": "abc123",
    "comments": [
        {
            "text": "Great video!",
            "sentiment": "Positive",
            "timestamp": "2024-02-20T10:30:00Z"
        },
        # ... more comments
    ]
}
```

## 🔬 Research & Development

### Machine Learning Pipeline
1. **Data Collection**
   - Automated comment fetching
   - Sentiment labeling
   - Data cleaning

2. **Model Development**
   ```python
   class SentimentAnalyzer:
       def __init__(self):
           self.model = None
           self.preprocessor = TextPreprocessor()

       def train(self, data):
           # Training implementation
           pass

       def predict(self, text):
           # Prediction implementation
           pass
   ```

3. **Analysis Capabilities**
   - Basic sentiment analysis
   - Emotion detection
   - Topic modeling
   - Engagement patterns

### Extending the Platform

1. **Custom Models**
   ```python
   # Example of custom model integration
   class CustomSentimentModel:
       def __init__(self):
           self.model = load_custom_model()
           
       def analyze(self, text):
           preprocessed = preprocess_text(text)
           return self.model.predict(preprocessed)
   ```

2. **Additional Features**
   - Multi-language support
   - Advanced sentiment metrics
   - Real-time analysis
   - Batch processing

## 📈 Data Analysis Examples

### Sentiment Distribution
```python
def analyze_sentiment_distribution(comments):
    sentiments = [analyze_sentiment(comment) for comment in comments]
    return pd.Series(sentiments).value_counts()
```

### Time-based Analysis
```python
def analyze_sentiment_over_time(comments):
    df = pd.DataFrame(comments)
    return df.groupby('timestamp')['sentiment'].value_counts()
```

### Development Process
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🔗 Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)

## 🙏 Acknowledgments

- YouTube Data API team
- TextBlob developers
- FastAPI community
- React community

---

**Note**: This project is for research and educational purposes. Please ensure compliance with YouTube's terms of service and API usage guidelines. 
