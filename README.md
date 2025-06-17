# 🎯 YouTube Sentiment Analyzer

A modern full-stack web application for analyzing YouTube comment sentiments using advanced machine learning techniques.

![Demo](https://img.shields.io/badge/Demo-Live-green) ![Version](https://img.shields.io/badge/Version-1.0.0-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **📊 Real-time Sentiment Analysis** - Analyze YouTube comments using TextBlob and Transformer models
- **🤖 Multiple ML Models** - BERT, RoBERTa, DeBERTa support with pattern-based enhancements
- **📈 Interactive Visualizations** - Beautiful charts and data visualization
- **💾 Data Export** - Download analysis results as CSV
- **🎨 Modern UI** - Responsive design with Tailwind CSS
- **⚡ Fast Performance** - Optimized backend with FastAPI

## 🏗️ Tech Stack

**Frontend:**
- React.js + Tailwind CSS
- Recharts for data visualization
- Framer Motion for animations

**Backend:**
- FastAPI (Python)
- Hugging Face Transformers
- TextBlob for NLP
- YouTube Data API v3

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- YouTube Data API key

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/youtube-sentiment-analyzer.git
cd youtube-sentiment-analyzer
```

### 2. Backend Setup
```bash
cd server
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create `.env` file from example:
```bash
cp env.example.txt .env
# Edit .env and add your actual API key
```

Or create `.env` manually:
```env
YOUTUBE_API_KEY=your_api_key_here
```

Start server:
```bash
python main.py
```

### 3. Frontend Setup
```bash
cd client
npm install
npm start
```

### 4. Access Application
Open http://localhost:3000 in your browser

## 🚀 **Free Deployment Options**

### Option 1: Railway (Recommended - One-click Deploy)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects the full-stack setup
4. Add environment variables:
   - `YOUTUBE_API_KEY=your_api_key_here`
5. Deploy automatically!

### Option 2: Render (Split Deploy)
**Backend:**
1. Go to [Render.com](https://render.com)
2. Create new "Web Service"
3. Connect GitHub repo, set root directory to `server`
4. Add environment variable: `YOUTUBE_API_KEY`

**Frontend:**
1. Create new "Static Site"
2. Root directory: `client`
3. Build command: `npm run build`
4. Publish directory: `build`

### Option 3: Vercel + Railway
**Frontend (Vercel):**
```bash
cd client
npx vercel --prod
```

**Backend (Railway):**
- Deploy backend separately on Railway
- Update `REACT_APP_API_URL` in Vercel

## 💡 Usage

1. **Fetch Comments**: Enter a YouTube URL to fetch comments
2. **Choose Analysis Method**: Select between TextBlob or Transformer models
3. **Analyze**: Get sentiment classification (Positive/Neutral/Negative)
4. **Visualize**: View results in interactive charts
5. **Export**: Download data as CSV for further analysis

## 🤖 ML Models

- **TextBlob**: Fast, lightweight sentiment analysis
- **BERT**: State-of-the-art transformer model
- **RoBERTa**: Optimized BERT variant
- **DeBERTa**: Microsoft's improved transformer
- **Pattern Enhancement**: Keyword and emoji-based sentiment detection

## 📁 Project Structure

```
youtube-sentiment-analyzer/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── assets/         # Static files
│   └── package.json
├── server/                 # FastAPI backend
│   ├── ml/                 # ML models and pipeline
│   ├── main.py            # API server
│   └── requirements.txt
└── README.md
```

## 🔧 Configuration

### YouTube API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Add API key to `.env` file

### Model Configuration
Models are automatically downloaded on first use. Supported models:
- `bert-base-uncased`
- `roberta-base`
- `microsoft/deberta-base`

## 📊 API Endpoints

- `GET /comments/raw` - Fetch YouTube comments
- `POST /analyze_sentiment` - Analyze sentiment
- `GET /ml/models` - Get available models
- `POST /ml/analyze` - ML-based analysis
- `GET /demo/comments` - Demo data

## 🤝 Contributing

=======
### Development Process
>>>>>>> ff586f39b23de4e8e874c1bb5f0404ca6f55a641
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

<<<<<<< HEAD
## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.
=======
## 🔗 Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
>>>>>>> ff586f39b23de4e8e874c1bb5f0404ca6f55a641

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for transformer models
- [YouTube Data API](https://developers.google.com/youtube/v3) for data access
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [React](https://reactjs.org/) community

## 📧 Support

For support, please open an issue or contact the maintainers.

---

<<<<<<< HEAD
**⚠️ Note**: Please ensure compliance with YouTube's API terms of service. This project is for educational and research purposes. 
=======
**Note**: This project is for research and educational purposes. Please ensure compliance with YouTube's terms of service and API usage guidelines. 
>>>>>>> ff586f39b23de4e8e874c1bb5f0404ca6f55a641
