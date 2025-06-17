import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import os
from textblob import TextBlob
import joblib
import re

class TextClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.tokenizers = {}
        
        # Pozitif pattern'lar
        self.positive_patterns = {
            'strong_positive': ['amazing', 'excellent', 'fantastic', 'brilliant', 'outstanding', 'perfect', 'wonderful', 'incredible', 'awesome', 'great', 'love', 'best', 'superb', 'magnificent'],
            'positive': ['good', 'nice', 'fine', 'okay', 'decent', 'satisfactory', 'pleasant', 'happy', 'glad', 'thank', 'appreciate', 'helpful', 'useful', 'impressive', 'solid', 'cool'],
            'positive_emojis': ['😊', '😄', '😃', '🙂', '👍', '❤️', '💕', '🔥', '✨', '🌟', '👏', '🎉', '💯']
        }
        
        # Negatif pattern'lar da ekleyelim
        self.negative_patterns = {
            'strong_negative': ['terrible', 'horrible', 'awful', 'disgusting', 'hate', 'worst', 'sucks', 'garbage', 'trash', 'pathetic', 'disaster'],
            'negative': ['bad', 'poor', 'disappointing', 'boring', 'annoying', 'stupid', 'lame', 'weak', 'fail', 'wrong'],
            'negative_emojis': ['😠', '😡', '👎', '💩', '😤', '🤮', '😞', '😢', '😭']
        }
        
        self.load_all_models()
        
    def analyze_patterns(self, text: str) -> Dict[str, Any]:
        """Metni pattern'lara göre analiz eder ve sentiment score'u döndürür."""
        text_lower = text.lower()
        pattern_score = 0
        pattern_info = {
            'strong_positive_found': [],
            'positive_found': [],
            'positive_emojis_found': [],
            'strong_negative_found': [],
            'negative_found': [],
            'negative_emojis_found': []
        }
        
        # Strong positive patterns kontrol
        for pattern in self.positive_patterns['strong_positive']:
            if pattern in text_lower:
                pattern_score += 0.8
                pattern_info['strong_positive_found'].append(pattern)
        
        # Positive patterns kontrol
        for pattern in self.positive_patterns['positive']:
            if pattern in text_lower:
                pattern_score += 0.4
                pattern_info['positive_found'].append(pattern)
        
        # Positive emojis kontrol
        for emoji in self.positive_patterns['positive_emojis']:
            if emoji in text:
                pattern_score += 0.6
                pattern_info['positive_emojis_found'].append(emoji)
        
        # Strong negative patterns kontrol
        for pattern in self.negative_patterns['strong_negative']:
            if pattern in text_lower:
                pattern_score -= 0.8
                pattern_info['strong_negative_found'].append(pattern)
        
        # Negative patterns kontrol
        for pattern in self.negative_patterns['negative']:
            if pattern in text_lower:
                pattern_score -= 0.4
                pattern_info['negative_found'].append(pattern)
        
        # Negative emojis kontrol
        for emoji in self.negative_patterns['negative_emojis']:
            if emoji in text:
                pattern_score -= 0.6
                pattern_info['negative_emojis_found'].append(emoji)
        
        return {
            'pattern_score': max(-1.0, min(1.0, pattern_score)),  # -1 ile 1 arasında sınırla
            'pattern_info': pattern_info
        }
        
    def load_all_models(self):
        """Load all available transformer models and their tokenizers from the models directory."""
        model_dir = os.path.join(os.path.dirname(__file__), "models")
        if not os.path.exists(model_dir):
            return
        for folder in os.listdir(model_dir):
            path = os.path.join(model_dir, folder)
            if os.path.isdir(path):
                try:
                    self.models[folder] = self.load_model(path)
                    self.tokenizers[folder] = self.load_tokenizer(path)
                except Exception as e:
                    continue
    
    def load_model(self, model_path: str) -> AutoModelForSequenceClassification:
        """Load a transformer model from the given path."""
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.to(self.device)
        model.eval()
        return model
    
    def load_tokenizer(self, model_path: str) -> AutoTokenizer:
        """Load a tokenizer from the given path."""
        return AutoTokenizer.from_pretrained(model_path)
    
    def predict_with_textblob(self, text: str) -> Dict[str, Any]:
        """Predict sentiment using TextBlob enhanced with patterns."""
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Pattern analizi yap
        pattern_analysis = self.analyze_patterns(text)
        pattern_score = pattern_analysis['pattern_score']
        
        # TextBlob ve pattern skorlarını birleştir
        # Pattern skoru güçlüyse onu daha fazla ağırlıklandır
        if abs(pattern_score) > 0.5:
            combined_polarity = 0.3 * textblob_polarity + 0.7 * pattern_score
        else:
            combined_polarity = 0.7 * textblob_polarity + 0.3 * pattern_score
        
        # Final sentiment belirleme
        if combined_polarity > 0.1:
            sentiment = "positive"
        elif combined_polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return {
            "text": text,
            "sentiment": sentiment,
            "confidence": abs(combined_polarity),
            "method": "textblob_enhanced",
            "textblob_score": textblob_polarity,
            "pattern_score": pattern_score,
            "combined_score": combined_polarity,
            "pattern_info": pattern_analysis['pattern_info']
        }
    
    def predict_with_transformer(self, text: str, model_name: str) -> Dict[str, Any]:
        """Predict sentiment using a transformer model enhanced with patterns."""
        if model_name not in self.models or model_name not in self.tokenizers:
            raise ValueError(f"Model {model_name} not found. Available: {list(self.models.keys())}")
            
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            prediction = torch.argmax(probabilities, dim=1).item()
            transformer_confidence = probabilities[0][prediction].item()
        
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        transformer_sentiment = sentiment_map[prediction]
        
        # Pattern analizi yap
        pattern_analysis = self.analyze_patterns(text)
        pattern_score = pattern_analysis['pattern_score']
        
        # Transformer ve pattern sonuçlarını birleştir
        final_sentiment = transformer_sentiment
        final_confidence = transformer_confidence
        
        # Eğer pattern güçlü bir sinyal veriyorsa, transformer sonucunu düzenle
        if abs(pattern_score) > 0.6:
            if pattern_score > 0.6 and transformer_sentiment != "positive":
                final_sentiment = "positive"
                final_confidence = min(0.9, transformer_confidence + abs(pattern_score) * 0.3)
            elif pattern_score < -0.6 and transformer_sentiment != "negative":
                final_sentiment = "negative"
                final_confidence = min(0.9, transformer_confidence + abs(pattern_score) * 0.3)
        elif abs(pattern_score) > 0.3:
            # Orta seviye pattern etkisi
            if pattern_score > 0.3 and transformer_sentiment == "neutral":
                final_sentiment = "positive"
                final_confidence = min(0.8, transformer_confidence + abs(pattern_score) * 0.2)
            elif pattern_score < -0.3 and transformer_sentiment == "neutral":
                final_sentiment = "negative" 
                final_confidence = min(0.8, transformer_confidence + abs(pattern_score) * 0.2)
        
        return {
            "text": text,
            "sentiment": final_sentiment,
            "confidence": final_confidence,
            "method": f"transformer_{model_name}_enhanced",
            "transformer_original": transformer_sentiment,
            "transformer_confidence": transformer_confidence,
            "pattern_score": pattern_score,
            "pattern_info": pattern_analysis['pattern_info']
        }
    
    def predict(self, text: str, use_transformer: bool = False, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Predict sentiment for a text using either TextBlob or a transformer model."""
        if use_transformer:
            if not model_name:
                raise ValueError("Model name must be provided when using transformer")
            return self.predict_with_transformer(text, model_name)
        else:
            return self.predict_with_textblob(text)
    
    def predict_batch(self, texts: List[str], use_transformer: bool = False, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Predict sentiment for a list of texts."""
        return [self.predict(text, use_transformer, model_name) for text in texts] 